# bsl-language-server call contract (1c-live)

Same MCP as in the ЗУП Cursor project: Node bridge → `bsl-language-server.jar` → `analyze`.

Server name: **`bsl-language-server`**. Tool: **`analyze`**.

## When (required)

On **yaxunit**, **coder**, and **implementer** (tests and application BSL are both BSL):

1. Write BSL under `out/…`.
2. Read absolute directories from `in/bsl-lint.json` → `src_dirs`.
3. Call `analyze` once per written tree (or once covering the main tree).
4. Fix errors / important warnings, then re-analyze if you changed files.
5. Note the result briefly in `test-report.md` / `code-report.md` / `implement-report.md`.

Do **not** skip lint because «tests are not production code» — YAxUnit modules are BSL too.

## Tool shape

```json
{
  "server": "bsl-language-server",
  "tool": "analyze",
  "arguments": {
    "srcDir": "C:/absolute/path/from/in/bsl-lint.json"
  }
}
```

Optional: `configFile` → path to `.bsl-language-server.json`.

## Env (harness)

| Variable | Meaning |
| --- | --- |
| `BSL_LS_MCP` / `BSL_LS_SERVER` | Absolute path to `bsl-ls-mcp/server.js` |
| `BSL_LS_JAR` | Absolute path to `bsl-language-server-*-exec.jar` |
| `JAVA_HOME` | Java 17+ (often VS Code `redhat.java` JRE) |
| `BSL_LS_NODE` | Optional override for `node` |

Defaults match the ЗУП layout under `%USERPROFILE%\.claude\bsl-ls-mcp\` and `bsl-ls\`.
