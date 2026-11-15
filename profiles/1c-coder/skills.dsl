skill "workspace" {
  policy: "Read plan inputs. Write sources only under out/, including out/coder_memory.md. One home.write per turn: either out/coder_memory.md or one file under out/. Short reports use arguments.content. BSL and XML use body raw and a <<<FILE block after the JSON object. Do not write the home root or notes/. home.run program python executes skill scripts from the workspace skills directory (absolute path from skill text). Forbidden: python -c one-liners that scrape Form.xml/Configuration.xml — use form-info/form-validate. It may receive the granted CF dump path as a script argument. Do not git commit or push. Do not install packages."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "platform_help" {
  policy: "REQUIRED before writing BSL or extension directives: call sntx_sem.search_bsl_syntax or sntx_sem.search_help at least once, then get_topic if needed. get_topic argument is topic_id, copied from the search hit id. Read skill sntx-sem / sntx-sem-contract.md. After two timeouts stop. Do not invent platform syntax or directive semantics."
  allowed_tools: ["sntx_sem.search_help", "sntx_sem.search_bsl_syntax", "sntx_sem.get_topic", "sntx_sem.find_examples"]
}

skill "code_index" {
  policy: "Search the CF dump via MCP code-index. Call only tools from Available MCP tools. Arguments come from agent.describe_tool. Follow in/code-index-contract.md. Do not call code-index.search or code-index.get_file. A denied tool is absent; do not repeat it. Do not page metadata XML. Do not call code-index until out/coder_memory.md has inputs_read: yes."
  allowed_tools: ["code-index.find_symbol", "code-index.list_files", "code-index.grep_code", "code-index.grep_body", "code-index.read_file", "code-index.get_file_summary"]
}

skill "code-index" {
  policy: "Same as code_index. profile.read_skill name code-index for the MCP guide. No python script."
  allowed_tools: ["code-index.find_symbol", "code-index.list_files", "code-index.grep_code", "code-index.grep_body", "code-index.read_file", "code-index.get_file_summary"]
}

skill "sntx-sem" {
  policy: "MCP sntx_sem guide. profile.read_skill name sntx-sem. No python script. Circuit-break after two timeouts."
  allowed_tools: ["sntx_sem.search_help", "sntx_sem.search_bsl_syntax", "sntx_sem.get_topic", "sntx_sem.find_examples"]
}

skill "bsl_lint" {
  policy: "REQUIRED after writing BSL under out/src: call bsl-language-server.analyze with absolute srcDir of THIS home out/src (no \\?\). See bsl-ls-contract.md. Use in/bsl-lint.json only if its srcDir is under this home and ends with out/src; ignore stale paths from other tasks. Fix diagnostics before done=true."
  allowed_tools: ["bsl-language-server.analyze", "bsl-language-server.version", "bsl_language_server.analyze", "bsl_language_server.version"]
}

skill "bsl-language-server" {
  policy: "Same as bsl_lint. profile.read_skill name bsl-language-server. No python script."
  allowed_tools: ["bsl-language-server.analyze", "bsl-language-server.version", "bsl_language_server.analyze", "bsl_language_server.version"]
}

skill "local_research" {
  policy: "Use code-index for the configuration. Do not page metadata XML. Skill instructions come from profile.read_skill, and their python scripts run with home.run."
  allowed_tools: ["home.read", "home.run"]
}

skill "cf-edit" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cf-init" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cf-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-borrow" {
  policy: "Read this skill with profile.read_skill (name only, no scripts path) before any borrowed form XML. Run cfe-borrow.py with home.run program python and -ConfigPath from the contract. The script clears the form module: read Module.bsl first and write it back afterwards. Then one form-edit for attributes/table and elementEvents together. Do not re-borrow in a loop. done=true only when BaseForm+ObjectBelonging=Adopted AND agreed handlers exist in Form.xml Events and Module.bsl."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-init" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-patch-method" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-diff" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "cfe-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-add" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-compile" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-edit" {
  policy: "Read this skill with profile.read_skill (name only). Prefer the CFE ValueTable+OnActivateRow JSON example in the skill. into/after are top-level; table columns use children+labelField; wire existing CF lists via elementEvents+callType. Run form-edit.py via home.run with absolute script path. One corrected JSON retry max — no Form.xml python -c scrapers. Write JSON and results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-info" {
  policy: "Use form-info instead of reading or scraping Form.xml. profile.read_skill name only; home.run form-info.py with -FormPath under out/src. Confirm table placement and Events after form-edit."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-patterns" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-remove" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "form-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "meta-compile" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "meta-edit" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "meta-info" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "help-add" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "interface-edit" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "interface-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-init" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-add-form" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-bsp-init" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-bsp-add-command" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-build" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-dump" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "epf-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-init" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-build" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-dump" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "erf-validate" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}

skill "odata" {
  policy: "Read this skill with profile.read_skill before writing the matching sources. Run its python script with home.run program python. Write results only under out/."
  allowed_tools: ["home.list", "home.read", "home.write", "home.run"]
}
