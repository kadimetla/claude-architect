# Emergency card: live class recovery

Read this while the cohort watches. One page, no scrolling, no thinking.

**The one thing to remember:** every launcher is idempotent and port-scoped. When something goes down, **run the same command again**. It repairs the gap and leaves everything else alone.

```powershell
cd C:\github\claude-architect
.\start-sidecar-group.ps1 -NoJupyter
```

That is the answer to most of what follows. It skips whatever is already healthy and restarts only what is missing. Tested: killing the Inspector outright and re-running this brought it back in about 15 seconds.

---

## MCP Inspector closed, crashed, or the tab went away

```powershell
.\start-sidecar-group.ps1 -NoJupyter
```

Comes back on <http://localhost:6274>. Takes ~15 seconds.

**If it refuses with "PORT IS IN USE":** an orphaned `node` is squatting on 6277. Clear it and retry.

```powershell
.\stop-sidecar-group.ps1
.\start-sidecar-group.ps1 -NoJupyter
```

**Talk track while it restarts:** "The Inspector is a Node app the MCP SDK ships. It's a *client* - killing it does not touch the server, which is why we can bounce it mid-demo." That is true and it buys you the 15 seconds.

---

## Inspector shows 404 / "Unexpected token < ... not valid JSON"

**Not a bug. Not your box.** The endpoint returned an **HTML error page** where JSON was expected, meaning nothing is listening at that URL. It says "oauth" only because discovery is the first step attempted.

You are pointed at a server that is not running (this is what WARNERCO does - it is a robotics MCP from a different course and is not part of this repo).

**Fix:** connect to `oreilly-cca-mcp` instead. It is **stdio**, a local subprocess, and physically cannot return an HTTP 404.

**Teaching save:** this is a genuinely good accident. "Watch - stdio cannot 404, because there is no HTTP layer to 404. That error is the transport telling you it never reached an MCP server at all."

---

## MCP CLI REPL stopped

```powershell
.\scripts\run-mcp-cli.ps1
```

Safe to run any time. It has no port, so nothing collides. Re-running just opens another REPL.

---

## A notebook cell fails live

1. **Restart the kernel and run cells above.** Most live failures are stale kernel state, not code.
2. **Check the kernel.** VS Code has **ten kernelspecs** registered on this box. If the picker shows `ai103-*`, `warnerco-py313`, or `.net-*`, you grabbed the wrong one. It must read **`notebooks/.venv`**.
3. **API 429 / overloaded:** wait ten seconds and re-run the cell. Do not start debugging code. Fall back to Claude Max if the API is genuinely throttling.
4. **Cache demo prints `cache_read=0`:** the cacheable prefix fell under the model floor (Haiku needs **4096** tokens, Sonnet 1024). Do not fix this live. Say "we will look at the counters after the break" and move on. Both cache demos were verified green before class.

---

## Kernel is wrong / "Access is denied: os error 5"

You are on the machine-wide Python, not the repo venv. Reselect the kernel in VS Code:

**Kernel picker -> Python Environments -> `notebooks/.venv`**

That error is the tell: the system Python isn't writable, so the `uv pip install` cell fails.

---

## Total reset (last resort, ~30 seconds)

```powershell
.\stop-sidecar-group.ps1
.\start-sidecar-group.ps1 -NoJupyter
```

If even that fails, run the board and read the FAIL rows. It changes nothing, so it is always safe:

```powershell
.\scripts\preflight-class.ps1
```

---

## What NOT to do mid-class

- **Do not run `.\scripts\run-mcp-inspector.ps1` directly.** It clears ports 6274/6277 *before* launching, so it kills a working Inspector. Go through `start-sidecar-group.ps1`, which skips anything already healthy.
- **Do not pass `-Restart`** unless you actually want everything torn down and rebuilt.
- **Do not chase the `internal-knowledge-base` server.** It points at `mcp.example.com` on purpose - it is a prop demonstrating SSE transport and env-var expansion. It will never connect. That is the demo.
- **Do not `pip install` anything to fix a uv problem.** There are already two `uv` binaries on this box (see below).

---

## Known, accepted, not-a-bug

| Thing | Why it is fine |
|---|---|
| `internal-knowledge-base` never connects | Teaching prop. `mcp.example.com` is not real. |
| WARNERCO Inspector 404 | Different course's server, not running here. |
| `uv --version` says 0.7.21 in your terminal | Two uv installs; a stale pip copy under `Program Files` wins your PATH. Everything runs green on it. Fix after class, needs an elevated shell. |
| `ZMQError: not a socket` after a notebook run | Windows/zmq teardown noise. Cells already executed. |
| Windows Terminal "did not open" warning | The `wt.exe` Store alias no-ops in some hosts. The launcher detects it and retries in a plain window automatically. Harmless. |
