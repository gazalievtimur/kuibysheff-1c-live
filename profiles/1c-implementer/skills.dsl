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
  policy: "Verify against CF baseline. Every call must pass repo=cf. Read-only."
  allowed_tools: [
    "code-index.search",
    "code-index.get_file",
    "code-index.list_files",
    "code-index.find_symbol",
    "code_index.search",
    "code_index.get_file",
    "code_index.list_files",
    "code_index.find_symbol"
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
