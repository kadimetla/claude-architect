/**
 * The agentic loop - the Domain 1 centerpiece.
 *
 * This is a real agentic loop: it calls Claude, inspects the stop_reason, and
 * branches explicitly on every possible value. When Claude wants a tool, the
 * loop executes it through the MCP client and feeds the result back. The loop
 * terminates on end_turn, on a hard stop reason, or on a max-iteration guard -
 * never on a guess.
 *
 * Every iteration appends an AgentTraceStep, so the caller can show the loop's
 * decision path in the agent-trace view. The loop is "check the result, not
 * the prose" made literal.
 */
import type Anthropic from "@anthropic-ai/sdk";
import type { AgentTraceStep } from "../../shared/types.js";
import { getDiscoveredTools, callMcpTool } from "./mcp-client.js";

/** Inputs for one agentic run. */
export interface LoopInput {
  client: Anthropic;
  model: string;
  system: string;
  /** The opening user message. */
  userMessage: string;
  /** Hard cap on loop iterations - the loop's safety valve. */
  maxIterations?: number;
  maxTokens?: number;
  /**
   * If set, the loop forces this tool on the FIRST turn (Domain 4 forced
   * structured output). Later turns use tool_choice auto so the model can
   * also call MCP tools.
   */
  forceToolFirst?: string;
  /**
   * Local tools to offer ALONGSIDE the MCP-discovered tools. These are
   * output-shaping tools (for example emit_question) that the loop captures
   * for the caller but does not execute via MCP. forceToolFirst usually names
   * one of these.
   */
  extraTools?: Anthropic.Tool[];
}

/** The result of an agentic run. */
export interface LoopResult {
  /** Every assistant message block from the final turn. */
  finalContent: Anthropic.ContentBlock[];
  /** The stop_reason that ended the loop. */
  finalStopReason: string;
  trace: AgentTraceStep[];
  usage: { inputTokens: number; outputTokens: number };
  /**
   * tool_use inputs captured per tool name across the whole run - the
   * generator reads its emit_question call out of here.
   */
  toolInputs: Record<string, unknown[]>;
}

/**
 * Runs the agentic loop to completion.
 *
 * The loop's spine is the `switch (stop_reason)`: each case is a deliberate,
 * documented branch, which is exactly what the CCA-F exam tests under "agentic
 * loops and stop_reason".
 */
export async function runAgentLoop(input: LoopInput): Promise<LoopResult> {
  const { client, model, system, userMessage } = input;
  const maxIterations = input.maxIterations ?? 8;
  const maxTokens = input.maxTokens ?? 2048;

  // The tool list = MCP-discovered tools + any local output-shaping tools.
  const mcpTools = await getDiscoveredTools();
  const mcpToolNames = new Set(mcpTools.map((t) => t.name));
  const anthropicTools: Anthropic.Tool[] = [
    ...mcpTools.map((t) => ({
      name: t.name,
      description: t.description,
      input_schema: t.inputSchema as Anthropic.Tool.InputSchema,
    })),
    ...(input.extraTools ?? []),
  ];

  const messages: Anthropic.MessageParam[] = [{ role: "user", content: userMessage }];
  const trace: AgentTraceStep[] = [];
  const toolInputs: Record<string, unknown[]> = {};
  let inputTokens = 0;
  let outputTokens = 0;

  for (let iteration = 1; iteration <= maxIterations; iteration++) {
    // Force a specific tool on turn 1 if requested; auto thereafter.
    const toolChoice: Anthropic.ToolChoice =
      iteration === 1 && input.forceToolFirst
        ? { type: "tool", name: input.forceToolFirst }
        : { type: "auto" };

    const response = await client.messages.create({
      model,
      max_tokens: maxTokens,
      system,
      tools: anthropicTools,
      tool_choice: toolChoice,
      messages,
    });

    inputTokens += response.usage.input_tokens;
    outputTokens += response.usage.output_tokens;

    // Capture every tool_use input so callers can read structured output out.
    for (const block of response.content) {
      if (block.type === "tool_use") {
        (toolInputs[block.name] ??= []).push(block.input);
      }
    }

    const stopReason = response.stop_reason ?? "unknown";

    // --- The stop_reason switch: one explicit branch per outcome. ----------
    switch (stopReason) {
      case "tool_use": {
        // Claude asked for one or more tools. MCP tools are executed via the
        // MCP client; local output-shaping tools (extraTools, e.g.
        // emit_question) are captured and acknowledged so the loop continues.
        messages.push({ role: "assistant", content: response.content });

        const toolUses = response.content.filter(
          (b): b is Anthropic.ToolUseBlock => b.type === "tool_use",
        );
        const toolResults: Anthropic.ToolResultBlockParam[] = [];
        const toolCalls: AgentTraceStep["toolCalls"] = [];

        for (const tu of toolUses) {
          if (mcpToolNames.has(tu.name)) {
            const { text, isError } = await callMcpTool(
              tu.name,
              tu.input as Record<string, unknown>,
            );
            toolResults.push({
              type: "tool_result",
              tool_use_id: tu.id,
              content: text,
              is_error: isError,
            });
            toolCalls.push({ name: tu.name, ok: !isError, summary: text.slice(0, 200) });
          } else {
            // A local tool: the input is already captured in toolInputs.
            // Acknowledge it so the conversation stays well-formed.
            toolResults.push({
              type: "tool_result",
              tool_use_id: tu.id,
              content: "Draft received.",
            });
            toolCalls.push({ name: tu.name, ok: true, summary: "local tool - draft captured" });
          }
        }

        messages.push({ role: "user", content: toolResults });
        trace.push({
          iteration,
          stopReason,
          action: `Handled ${toolUses.length} tool call(s); fed results back to the model.`,
          toolCalls,
        });
        continue; // loop continues
      }

      case "end_turn": {
        trace.push({
          iteration,
          stopReason,
          action: "Model finished its turn. Loop complete.",
          toolCalls: [],
        });
        return finish(response, stopReason, trace, toolInputs, inputTokens, outputTokens);
      }

      case "max_tokens": {
        // Truncated output. Surface it - do not silently treat it as success.
        trace.push({
          iteration,
          stopReason,
          action: "Output hit max_tokens and was truncated. Stopping and surfacing the result.",
          toolCalls: [],
        });
        return finish(response, stopReason, trace, toolInputs, inputTokens, outputTokens);
      }

      case "pause_turn": {
        // A long-running server turn paused. Resume by echoing the content back.
        messages.push({ role: "assistant", content: response.content });
        trace.push({
          iteration,
          stopReason,
          action: "Server turn paused; resuming the conversation to let it continue.",
          toolCalls: [],
        });
        continue;
      }

      case "stop_sequence":
      case "refusal":
      default: {
        // refusal: the model declined. stop_sequence: a configured stop hit.
        // Both are terminal and must be reported, not swallowed.
        trace.push({
          iteration,
          stopReason,
          action: `Terminal stop_reason "${stopReason}". Ending the loop and surfacing it.`,
          toolCalls: [],
        });
        return finish(response, stopReason, trace, toolInputs, inputTokens, outputTokens);
      }
    }
  }

  // The iteration guard tripped - the loop did not converge.
  trace.push({
    iteration: maxIterations,
    stopReason: "max_iterations",
    action: `Loop hit its ${maxIterations}-iteration guard without an end_turn.`,
    toolCalls: [],
  });
  return {
    finalContent: [],
    finalStopReason: "max_iterations",
    trace,
    usage: { inputTokens, outputTokens },
    toolInputs,
  };
}

/** Packages a terminal response into a LoopResult. */
function finish(
  response: Anthropic.Message,
  stopReason: string,
  trace: AgentTraceStep[],
  toolInputs: Record<string, unknown[]>,
  inputTokens: number,
  outputTokens: number,
): LoopResult {
  return {
    finalContent: response.content,
    finalStopReason: stopReason,
    trace,
    usage: { inputTokens, outputTokens },
    toolInputs,
  };
}
