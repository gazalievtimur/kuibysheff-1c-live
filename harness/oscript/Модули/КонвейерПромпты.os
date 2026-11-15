// Промпты стадий kbshff run.

Функция ДляСтадии(Стадия, ProductId, Ожидание, ВидАртефакта = "cfe") Экспорт
	Если Ожидание = Неопределено Тогда
		Ожидание = Новый Соответствие;
	КонецЕсли;
	Вид = НРег(СокрЛП(Строка(ВидАртефакта)));
	Если Вид <> "epf" И Вид <> "erf" Тогда
		Вид = "cfe";
	КонецЕсли;
	Yax = JsonУтилиты.ПолучитьПоле(Ожидание, "yaxunit");
	ПроцедураИмя = СокрЛП(Строка(JsonУтилиты.ПолучитьПоле(Yax, "procedure", "")));
	Иглы = Новый Массив;
	Для Каждого Элемент Из МассивПоля(Ожидание, "test_contains") Цикл
		Если ЗначениеЗаполнено(Элемент) Тогда
			Иглы.Добавить(Строка(Элемент));
		КонецЕсли;
	КонецЦикла;
	Preamble = "Read in/agreements-protocol.md and in/agreements.json first. Identifiers are literals (no synonyms, no renaming)." + Символы.ПС
		+ "Read in/artifact.json. kind=" + Вид + "." + Символы.ПС;
	GateLine = "";
	Если ЗначениеЗаполнено(ПроцедураИмя) Или Иглы.Количество() > 0 Тогда
		Куски = Новый Массив;
		Если ЗначениеЗаполнено(ПроцедураИмя) Тогда
			Куски.Добавить("required procedure name (exact spelling): " + ПроцедураИмя);
		КонецЕсли;
		Если Иглы.Количество() > 0 Тогда
			Куски.Добавить("BSL must contain: " + СтрСоединить(Иглы, ", "));
		КонецЕсли;
		GateLine = "Also read in/agreements.md and in/expect.json. " + СтрСоединить(Куски, "; ") + "." + Символы.ПС;
	КонецЕсли;
	Если Стадия = "analyst" Тогда
		Возврат Preamble + ТекстАналитика(Вид, ProductId, ПроцедураИмя) + "Return JSON only on every turn.";
	ИначеЕсли Стадия = "yaxunit" Тогда
		Возврат Preamble
			+ "Write YAxUnit tests for the approved plan. Read in/docs/ first "
			+ "(public YAxUnit snapshot). Read in/prd.md, in/tasks.md, in/cfe-scope.md. "
			+ "Before platform BSL in tests, call sntx_sem.search_bsl_syntax or search_help. "
			+ "After writing tests, call bsl-language-server.analyze with srcDir from "
			+ "in/bsl-lint.json (absolute paths). "
			+ "Do not implement the feature. Tests must fail on the baseline CF. "
			+ "Test server code and data only (ДобавитьСерверныйТест, ЮТест.ОжидаетЧто on the method result). "
			+ "No form or UI tests: do not call ОткрытьФорму, do not assert form items, the current row, or smoke form opening. "
			+ "For balances, call the server function from agreements and assert the value table. "
			+ "Read in/code-index-contract.md. code-index repo=cf. Call only tools from Available MCP tools. Do not repeat find_symbol. "
			+ "Do not call code-index.search or get_file." + Символы.ПС
			+ GateLine
			+ "Write out/tests/, out/cfe-tests/, test-report.md (cite docs URLs + verification table), "
			+ "manifest.json (apply_mode=none). Return JSON only on every turn.";
	ИначеЕсли Стадия = "coder" Тогда
		Возврат Preamble + ТекстКодера(Вид) + "Return JSON only on every turn.";
	Иначе
		Возврат Preamble + ТекстСборщика(Вид) + "Return JSON only on every turn.";
	КонецЕсли;
КонецФункции

Функция ТекстАналитика(Вид, ProductId, ПроцедураИмя)
	Если ЗначениеЗаполнено(ПроцедураИмя) Тогда
		Extra = "Write out/agreements.md first (verbatim identifiers from in/agreements.json). Repeat the gate procedure in tasks.md." + Символы.ПС
			+ " Gate procedure: " + ПроцедураИмя + "." + Символы.ПС;
	Иначе
		Extra = "expect is empty: that is not blocked. Do not rewrite in/task_brief.md. "
			+ "Confirm object and form with conf_doc.conf_doc_list_objects (q is a name substring) then conf_doc_get_object (object_type, name), and one code-index call from Available MCP tools. Read in/code-index-contract.md. "
			+ "conf_doc_search is allowed; the vector index exists. "
			+ "If code-index returns daemon_offline, ignore it and finish from conf_doc. "
			+ "Do not call sntx_sem. Language semantics are out of scope. "
			+ "There is no code-index.search or code-index.get_file tool: a denial is not an offline index, do not switch to reading the CF tree file by file. "
			+ "Object and form names in agreements.md must be copied from a conf_doc_list_objects or conf_doc_get_object result. Never invent a metadata name. "
			+ "The first home.write is out/agreements.md, only after that confirmation, no later than iteration 8. "
			+ "After out/agreements.md exists, do not call conf_doc_list_objects, conf_doc_search, or find_symbol again. "
			+ "Write the remaining required files one per turn, then done=true. "
			+ "Choose the gate test procedure name yourself and write it in agreements.md. Repeat that name in tasks.md." + Символы.ПС;
	КонецЕсли;
	Общее = "Read in/task_brief.md and in/product.json. "
		+ "Configuration objects, forms, registers and metadata: conf_doc.conf_doc_list_objects (q is a name substring) then conf_doc.conf_doc_get_object (object_type and name). "
		+ "conf_doc_search is allowed; the vector index exists. "
		+ "Read in/code-index-contract.md. code-index repo=cf. Call only tools from Available MCP tools. "
		+ "Do not repeat the same find_symbol. Do not call code-index.search or code-index.get_file. Do not walk the CF tree file by file. "
		+ "Do not call sntx_sem. Language semantics are out of scope for this stage." + Символы.ПС
		+ Extra
		+ "Write at most ONE file per turn (home.write once). Never batch multiple "
		+ "plan files in a single JSON response — large replies fail to parse." + Символы.ПС;
	Если Вид = "cfe" Тогда
		Возврат "Подготовь утверждаемый план доработки в расширении для product=" + ProductId + "." + Символы.ПС
			+ Общее
			+ "Write prd.md, architecture.md, tasks.md (labels bsl|metadata|cfe_packaging), "
			+ "cfe-scope.md, workflow-state.md (verification table), "
			+ "manifest.json (apply_mode=none)." + Символы.ПС
			+ "Finish required deliverables (cfe-scope.md, manifest.json) before optional notes." + Символы.ПС;
	КонецЕсли;
	Область = ?(Вид = "epf", "внешней обработки", "внешнего отчёта");
	Файл = ?(Вид = "epf", "epf-scope.md", "erf-scope.md");
	Возврат "Подготовь утверждаемый план " + Область + " (не расширения конфигурации) для product=" + ProductId + "." + Символы.ПС
		+ Общее
		+ "Write prd.md, architecture.md, tasks.md (labels bsl|metadata|packaging), "
		+ Файл + ", workflow-state.md (verification table), "
		+ "manifest.json (apply_mode=none)." + Символы.ПС
		+ Файл + " names the external object, its forms and modules. No borrows, no &Вместо, no &ИзменениеИКонтроль." + Символы.ПС
		+ "Do not write cfe-scope.md. Do not plan a configuration extension." + Символы.ПС
		+ "Finish required deliverables (" + Файл + ", manifest.json) before optional notes." + Символы.ПС;
КонецФункции

Функция ТекстПамятиКодера()
	Возврат "Keep coder_memory.md in the home root, not under out/. "
		+ "If the file is absent, do not home.read it: read in/agreements-protocol.md, in/code-index-contract.md, in/agreements.json, in/agreements.md, in/tasks.md, in/artifact.json and in/tests/ once, "
		+ "then home.write coder_memory.md before iteration 3 with sections Status, Contract, Facts, Next, Stopped and inputs_read: yes. "
		+ "Facts holds the last code-index hit (file_path, line_start, line_end, procedure name). Next is not another find_symbol. "
		+ "If the file exists but its text is not in this turn, the only tool call is home.read of coder_memory.md. Do not open the plan in/ files again. "
		+ "While inputs_read is yes, do not read those plan in/ files again. Do not call code-index until inputs_read is yes. "
		+ "A memory update is the one home.write of that turn. Record Facts before the first out/src write. "
		+ "One home.write per turn: either coder_memory.md or one file under out/. Never batch several files in one JSON response. "
		+ "Write the first out/src file by iteration 12. "
		+ "Copy the test's called module and method into Contract verbatim and implement that call. "
		+ "Query existing balances. Do not post documents or write registers to fabricate stock. "
		+ "If the test requires an effect that is neither in tasks.md nor produced by the test's own data, set phase blocked, leave out/src empty, and write the blocked report. "
		+ "CF lookup is code-index only, always repo=cf. Read in/code-index-contract.md. "
		+ "Call only tools from Available MCP tools. Do not repeat the same find_symbol. "
		+ "Do not call code-index.search or code-index.get_file. Do not page metadata XML with local_tools. "
		+ "Do not point home.run rg or python at the configuration tree. "
		+ "sntx_sem.get_topic takes topic_id from the search hit." + Символы.ПС;
КонецФункции

Функция ТекстКодера(Вид)
	Память = ТекстПамятиКодера();
	Если Вид = "cfe" Тогда
		Возврат "Implement approved bsl/metadata steps from in/tasks.md into out/src/." + Символы.ПС
			+ Память
			+ "Before writing BSL/directives, call sntx_sem.search_bsl_syntax or search_help "
			+ "(then get_topic with topic_id). After writing sources, call "
			+ "bsl-language-server.analyze with srcDir from in/bsl-lint.json. "
			+ "Do not rename tests. Skip cfe_packaging. Write code-report.md "
			+ "(verification table), files-index.md, "
			+ "manifest.json (apply_mode=none)." + Символы.ПС
			+ "Write code-report.md last, after out/src is complete." + Символы.ПС;
	КонецЕсли;
	Куда = ?(Вид = "epf", "external data processor", "external report");
	Возврат "Implement approved bsl/metadata steps from in/tasks.md into out/src/ as ordinary modules of an " + Куда + "." + Символы.ПС
		+ "Do not use &Вместо or &ИзменениеИКонтроль. Do not write extension XML. "
		+ "If in/tests is absent, do not invent tests. "
		+ Память
		+ "Before writing BSL, call sntx_sem.search_bsl_syntax or search_help "
		+ "(then get_topic with topic_id). After writing sources, call "
		+ "bsl-language-server.analyze with srcDir from in/bsl-lint.json. "
		+ "Skip packaging. Write code-report.md "
		+ "(verification table), files-index.md, "
		+ "manifest.json (apply_mode=none)." + Символы.ПС
		+ "Write code-report.md last, after out/src is complete." + Символы.ПС;
КонецФункции

Функция ТекстРетраяСборки(Стадия, ВидАртефакта = "cfe", КаскадКодера = Ложь) Экспорт
	Вид = НРег(СокрЛП(Строка(ВидАртефакта)));
	Если Вид <> "epf" И Вид <> "erf" Тогда
		Вид = "cfe";
	КонецЕсли;
	Каталог = ?(Вид = "cfe", "cfe", Вид);
	Префикс = "Read in/build-feedback.md first (platform load error). "
		+ "Do not call ibcmd or Designer. "
		+ "Fix the dump so the orchestrator can build the binary." + Символы.ПС;
	Если Стадия = "coder" Тогда
		Возврат Префикс
			+ "Repair out/src only. Do not write out/" + Каталог + "/ packaging trees. "
			+ ?(КаскадКодера, "The implementer already failed packaging; the BSL/metadata in out/src is the root cause.", "")
			+ Символы.ПС;
	КонецЕсли;
	Возврат Префикс
		+ "Repair out/" + Каталог + "/ so Configuration.xml (or the external root XML) and modules load cleanly. "
		+ "Re-copy or re-pack from in/coder/ as needed. Keep out/cfe-tests/ for cfe." + Символы.ПС;
КонецФункции

Функция ТекстСборщика(Вид)
	Если Вид = "cfe" Тогда
		Возврат "Package coder sources from in/coder/ into out/cfe/ per in/cfe-scope.md." + Символы.ПС
			+ "Read in/agreements.md and in/code-index-contract.md. code-index repo=cf. "
			+ "Call only tools from Available MCP tools. Do not repeat find_symbol. "
			+ "Do not call code-index.search or get_file. "
			+ "Copy in/cfe-tests/ to out/cfe-tests/ without rewriting tests. "
			+ "Write implement-report.md (verification table), checklist.md, "
			+ "manifest.json (apply_mode=copy_out)." + Символы.ПС;
	КонецЕсли;
	Каталог = Вид;
	Элемент = ?(Вид = "epf", "ExternalDataProcessor", "ExternalReport");
	Файл = ?(Вид = "epf", "epf-scope.md", "erf-scope.md");
	Возврат "Package coder sources from in/coder/ into out/" + Каталог + "/ as a hierarchical configurator dump." + Символы.ПС
		+ "Read in/" + Файл + ", in/artifact.json, and in/code-index-contract.md. "
		+ "code-index repo=cf. Call only tools from Available MCP tools. Do not repeat find_symbol. "
		+ "Do not call code-index.search or get_file. "
		+ "Root file is <Name>.xml with element " + Элемент + ". "
		+ "Modules live under <Name>/Ext/ (ObjectModule.bsl and forms from the scope). "
		+ "Do not create out/cfe. Do not copy cfe-tests. Do not use extension directives. "
		+ "The orchestrator compiles this tree; do not run Designer or ibcmd." + Символы.ПС
		+ "Write implement-report.md (verification table), checklist.md, "
		+ "manifest.json (apply_mode=copy_out)." + Символы.ПС;
КонецФункции

Функция МассивПоля(Объект, Ключ)
	Значение = JsonУтилиты.ПолучитьПоле(Объект, Ключ);
	Если Значение = Неопределено Тогда
		Возврат Новый Массив;
	КонецЕсли;
	Если JsonУтилиты.ЭтоМассив(Значение) Тогда
		Возврат Значение;
	КонецЕсли;
	Результат = Новый Массив;
	Результат.Добавить(Значение);
	Возврат Результат;
КонецФункции
