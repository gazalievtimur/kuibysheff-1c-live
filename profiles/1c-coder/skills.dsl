skill "workspace" {
  policy: "Read plan inputs; write sources only under out/. One home.write per turn (one file per iteration). home.run limited to read-only git/rg when configured."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "platform_help" {
  policy: "REQUIRED before writing BSL or extension directives: call sntx_sem.search_bsl_syntax or sntx_sem.search_help at least once, then get_topic if needed. Do not invent platform syntax or directive semantics."
  allowed_tools: [
    "sntx_sem.search_help",
    "sntx_sem.search_bsl_syntax",
    "sntx_sem.get_topic",
    "sntx_sem.find_examples"
  ]
}

skill "code_index" {
  policy: "Read/search CF dump. Every call must pass repo=cf. Use find_symbol with name=. Do not invent symbols."
  allowed_tools: [
    "code-index.search",
    "code-index.find_symbol",
    "code-index.get_file",
    "code-index.list_files",
    "code_index.search",
    "code_index.find_symbol",
    "code_index.get_file",
    "code_index.list_files"
  ]
}

skill "bsl_lint" {
  policy: "REQUIRED after writing BSL under out/src: call bsl-language-server.analyze with absolute srcDir from in/bsl-lint.json. Fix diagnostics before done=true."
  allowed_tools: [
    "bsl-language-server.analyze",
    "bsl-language-server.version",
    "bsl_language_server.analyze",
    "bsl_language_server.version"
  ]
}

skill "local_research" {
  policy: "Read baseline CF files via local_tools."
  allowed_tools: [
    "local_tools.search_docs",
    "local_tools.read_file"
  ]
}
