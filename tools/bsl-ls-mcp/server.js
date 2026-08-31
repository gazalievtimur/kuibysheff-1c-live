import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "child_process";
import { mkdirSync, readFileSync, existsSync, rmSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { tmpdir } from "os";
import { promisify } from "util";

const execFileAsync = promisify(execFile);
const here = dirname(fileURLToPath(import.meta.url));

const JAR_PATH =
  process.env.BSL_LS_JAR ||
  join(here, "..", "bsl-ls", "bsl-language-server.jar");

const JAVA_BIN = process.env.JAVA_HOME
  ? join(process.env.JAVA_HOME, "bin", process.platform === "win32" ? "java.exe" : "java")
  : "java";

const server = new Server(
  { name: "bsl-language-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

function displayPath(filePath, srcDir) {
  let normalized = String(filePath || "")
    .replace(/^file:\/\/\//, "")
    .replace(/^file:\/\//, "");
  try {
    normalized = decodeURIComponent(normalized);
  } catch {
    // keep raw
  }
  const src = String(srcDir || "").replace(/\\/g, "/").replace(/\/+$/, "");
  const posix = normalized.replace(/\\/g, "/");
  if (src && posix.toLowerCase().startsWith(src.toLowerCase())) {
    return posix.slice(src.length).replace(/^[\\/]/, "");
  }
  return posix;
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze",
      description:
        "Статический анализ BSL (1С) через BSL Language Server. Возвращает диагностики по файлам.",
      inputSchema: {
        type: "object",
        properties: {
          srcDir: {
            type: "string",
            description: "Абсолютный путь к каталогу с исходниками (.bsl / .os)",
          },
          configFile: {
            type: "string",
            description: "Опциональный путь к .bsl-language-server.json",
          },
        },
        required: ["srcDir"],
      },
    },
    {
      name: "version",
      description: "Версия BSL Language Server",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "version") {
    try {
      const { stdout } = await execFileAsync(JAVA_BIN, ["-jar", JAR_PATH, "--version"]);
      return { content: [{ type: "text", text: stdout.trim() }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Ошибка: ${e.message}` }] };
    }
  }

  if (name === "analyze") {
    const { srcDir, configFile } = args || {};
    const outputDir = join(tmpdir(), `bsl-ls-${Date.now()}`);
    mkdirSync(outputDir, { recursive: true });

    const javaArgs = [
      "-jar",
      JAR_PATH,
      "analyze",
      "--srcDir",
      srcDir,
      "--reporter",
      "json",
      "--outputDir",
      outputDir,
    ];
    if (configFile) {
      javaArgs.push("--configuration", configFile);
    }

    try {
      await execFileAsync(JAVA_BIN, javaArgs, { timeout: 120_000 });

      const reportFile = join(outputDir, "bsl-json.json");
      if (!existsSync(reportFile)) {
        rmSync(outputDir, { recursive: true, force: true });
        return {
          content: [{ type: "text", text: "Анализ завершён. Диагностик не найдено." }],
        };
      }

      const report = JSON.parse(readFileSync(reportFile, "utf-8"));
      const fileinfos = report.fileinfos || report;
      const issues = [];
      let totalErrors = 0;
      let totalWarnings = 0;

      for (const fileEntry of fileinfos) {
        const fileDiags = fileEntry.diagnostics || [];
        if (fileDiags.length === 0) {
          continue;
        }
        totalErrors += fileDiags.filter((d) => d.severity === "Error").length;
        totalWarnings += fileDiags.filter((d) => d.severity === "Warning").length;
        const relPath = displayPath(fileEntry.path || fileEntry.fileUri || "", srcDir);
        for (const d of fileDiags) {
          const line = d.range?.start?.line ?? 0;
          const sevMap = {
            Error: "ОШИБКА",
            Warning: "ПРЕДУПРЕЖДЕНИЕ",
            Information: "ИНФО",
            Hint: "ПОДСКАЗКА",
          };
          const sev = sevMap[d.severity] || d.severity;
          issues.push(`${sev} ${relPath}:${line + 1} — ${d.message} [${d.code}]`);
        }
      }

      rmSync(outputDir, { recursive: true, force: true });
      const summary = `Итого: ${totalErrors} ошибок, ${totalWarnings} предупреждений\n\n`;
      return {
        content: [
          {
            type: "text",
            text: summary + (issues.length > 0 ? issues.join("\n") : "Диагностик нет."),
          },
        ],
      };
    } catch (e) {
      rmSync(outputDir, { recursive: true, force: true });
      return { content: [{ type: "text", text: `Ошибка анализа: ${e.message}` }] };
    }
  }

  return { content: [{ type: "text", text: `Неизвестный инструмент: ${name}` }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
