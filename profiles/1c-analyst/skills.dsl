skill "workspace" {
  policy: "Read in/ and write plan artifacts under out/ only. One home.write per turn (one file per iteration). Optional home.run for read-only git/rg when configured."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "platform_help" {
  policy: "REQUIRED before claiming BSL or extension-directive facts: call sntx_sem.search_bsl_syntax or sntx_sem.search_help at least once, then get_topic for the best hit. Do not invent platform syntax. Workflow search then get_topic then optional find_examples."
  allowed_tools: [
    "sntx_sem.search_help",
    "sntx_sem.search_bsl_syntax",
    "sntx_sem.search_query_language",
    "sntx_sem.get_topic",
    "sntx_sem.find_examples",
    "sntx_sem.list_domains"
  ]
}

skill "conf_docs" {
  policy: "Search configuration documentation when conf-doc MCP is available. Read-only."
  allowed_tools: [
    "conf_doc.conf_doc_search",
    "conf_doc.conf_doc_get_object",
    "conf_doc.conf_doc_get_object_chunk",
    "conf_doc.conf_doc_query"
  ]
}

skill "code_index" {
  policy: "Search CF dump via code-index. Every call must pass repo=cf. Use find_symbol with name= and list_files with path_prefix or pattern. Read-only."
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

skill "local_research" {
  policy: "Fallback research over the product CF workspace via local_tools."
  allowed_tools: [
    "local_tools.search_docs",
    "local_tools.read_file"
  ]
}

skill "web_search" {
  policy: "Search the web and read public URLs through SearXNG. Read-only. Do not invent results. Web supplements the brief; it never replaces TZ."
  allowed_tools: [
    "searxng.searxng_web_search",
    "searxng.searxng_search_suggestions",
    "searxng.searxng_instance_info",
    "searxng.web_url_read"
  ]
}
