skill "workspace" {
  policy: "List and read in/ and out/ only. Never list the home root. One home.write per turn, paths under out/. home.run program python runs a profile skill script and nothing else."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "conf_docs" {
  policy: "Required to confirm objects and forms. Read skill conf-doc (profile.read_skill) for tool args. list_objects with q as a name substring, then get_object with object_type and name copied from that result. search is allowed once if the substring finds nothing. Read-only. Do not repeat list_objects after agreements.md exists. Do not use 1cconfinfo as a substitute for conf_doc MCP."
  allowed_tools: ["conf_doc.conf_doc_list_objects", "conf_doc.conf_doc_search", "conf_doc.conf_doc_get_object", "conf_doc.conf_doc_get_object_chunk", "conf_doc.conf_doc_query"]
}

skill "conf-doc" {
  policy: "MCP conf_doc usage guide. profile.read_skill name conf-doc. No python script. Confirm object/form names via conf_doc_* tools only."
  allowed_tools: ["conf_doc.conf_doc_list_objects", "conf_doc.conf_doc_search", "conf_doc.conf_doc_get_object", "conf_doc.conf_doc_get_object_chunk", "conf_doc.conf_doc_query"]
}

skill "code_index" {
  policy: "Optional, one call, only when conf_doc did not return the form. Call only a tool from Available MCP tools. Arguments come from agent.describe_tool. Follow in/code-index-contract.md. Do not call search or get_file. A denied tool is absent; do not repeat it. daemon_offline means stop using this skill."
  allowed_tools: ["code-index.find_symbol", "code-index.list_files", "code-index.read_file", "code-index.get_file_summary"]
}

skill "web_search" {
  policy: "Optional public lookup. Cite the URL. A hit is not a requirement and does not replace conf_doc."
  allowed_tools: ["searxng.searxng_web_search", "searxng.searxng_search_suggestions", "searxng.searxng_instance_info", "searxng.web_url_read"]
}

skill "cf-info" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "meta-info" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "form-info" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "form-patterns" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "cfe-diff" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "1cconfinfo" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}

skill "db-list" {
  policy: "Read this skill with profile.read_skill before inspecting metadata. Run its python script with home.run program python. Do not invent field names."
  allowed_tools: ["home.list", "home.read", "home.run"]
}
