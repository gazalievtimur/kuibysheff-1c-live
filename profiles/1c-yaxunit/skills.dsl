skill "workspace" {
  policy: "Read in/docs and plan; write tests under out/ only."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "yaxunit_docs" {
  policy: "Public YAxUnit snapshot is under in/docs/. Read it before writing tests. Do not invent API."
  allowed_tools: ["home.list", "home.read", "local_tools.read_file", "local_tools.search_docs"]
}

skill "platform_help" {
  policy: "REQUIRED before writing BSL assertions that touch platform APIs (documents, write, refuse): call sntx_sem.search_bsl_syntax or sntx_sem.search_help at least once. Prefer get_topic on the best hit. Do not invent BSL."
  allowed_tools: [
    "sntx_sem.search_help",
    "sntx_sem.search_bsl_syntax",
    "sntx_sem.get_topic",
    "sntx_sem.find_examples"
  ]
}

skill "code_index" {
  policy: "Read/search CF dump to know objects under test. Every call must pass repo=cf. Do not invent symbols."
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
  policy: "REQUIRED after writing YAxUnit BSL: call bsl-language-server.analyze with absolute srcDir from in/bsl-lint.json. Fix errors before done=true. Tests are BSL too."
  allowed_tools: [
    "bsl-language-server.analyze",
    "bsl-language-server.version",
    "bsl_language_server.analyze",
    "bsl_language_server.version"
  ]
}

skill "local_research" {
  policy: "Fallback research over the product CF workspace via local_tools."
  allowed_tools: [
    "local_tools.search_docs",
    "local_tools.read_file"
  ]
}

skill "web_search" {
  policy: "Supplement in/docs/ only. Public YAxUnit URLs. Cite them. Never invent results. Never use ITS."
  allowed_tools: [
    "searxng.searxng_web_search",
    "searxng.searxng_search_suggestions",
    "searxng.searxng_instance_info",
    "searxng.web_url_read"
  ]
}
