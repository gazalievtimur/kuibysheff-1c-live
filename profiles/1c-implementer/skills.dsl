skill "workspace" {
  policy: "Read plan and coder inputs; write CFE tree under out/cfe/ only."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "platform_help" {
  policy: "When metadata or directive packaging is unclear, call sntx_sem.search_help or sntx_sem.get_topic before guessing. Prefer packaging from coder sources when already clear."
  allowed_tools: [
    "sntx_sem.search_help",
    "sntx_sem.get_topic"
  ]
}

skill "code_index" {
  policy: "Verify against the CF baseline. Call only tools from Available MCP tools. Arguments come from agent.describe_tool. Follow in/code-index-contract.md. Do not call code-index.search or code-index.get_file. A denied tool is absent; do not repeat it. Read-only."
  allowed_tools: [
    "code-index.find_symbol",
    "code-index.list_files",
    "code-index.grep_code",
    "code-index.grep_body",
    "code-index.read_file",
    "code-index.get_file_summary"
  ]
}

skill "local_research" {
  policy: "Read baseline CF for borrow/compare."
  allowed_tools: [
    "local_tools.search_docs",
    "local_tools.read_file"
  ]
}

skill "bsl_lint" {
  policy: "REQUIRED after packing BSL under out/cfe: call bsl-language-server.analyze with absolute srcDir from in/bsl-lint.json. Fix packaging-related diagnostics before done=true."
  allowed_tools: [
    "bsl-language-server.analyze",
    "bsl-language-server.version",
    "bsl_language_server.analyze",
    "bsl_language_server.version"
  ]
}

skill "cfe-validate" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-diff" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cf-validate" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-validate" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-validate" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-validate" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-build" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-build" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-create" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-dump-cf" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-dump-xml" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-load-cf" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-load-git" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-load-xml" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-update" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-run" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "db-list" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-config" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-configuration" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-dependencies" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-extensions" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-external" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-infobase" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-mcp" {
  policy: "Read this skill with profile.read_skill. It maps REAL MCP servers in this profile (code-index, sntx_sem, bsl-language-server) and forbids inventing mcp-1c-platform-tools. Platform load/dump/run goes through db-*/cfe-*/epf-* scripts via home.run, not VS Code MCP tool names."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run", "code-index.find_symbol", "code-index.read_file", "code-index.get_file_summary", "sntx_sem.search_help", "sntx_sem.get_topic", "bsl-language-server.analyze"]
}

skill "1c-platform-tools-run" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-setversion" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-support" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "1c-platform-tools-test" {
  policy: "Read this skill with profile.read_skill before packaging or checking the tree. Run its python script with home.run program python. Do not invent attributes."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}
