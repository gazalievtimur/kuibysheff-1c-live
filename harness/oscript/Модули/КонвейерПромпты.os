// Промпты стадий kbshff run.

Функция ДляСтадии(Стадия, ProductId, Ожидание) Экспорт
	Если Ожидание = Неопределено Тогда
		Ожидание = Новый Соответствие;
	КонецЕсли;
	Yax = JsonУтилиты.ПолучитьПоле(Ожидание, "yaxunit");
	ПроцедураИмя = СокрЛП(Строка(JsonУтилиты.ПолучитьПоле(Yax, "procedure", "")));
	Иглы = Новый Массив;
	Для Каждого Элемент Из МассивПоля(Ожидание, "test_contains") Цикл
		Если ЗначениеЗаполнено(Элемент) Тогда
			Иглы.Добавить(Строка(Элемент));
		КонецЕсли;
	КонецЦикла;
	Preamble = "Read in/agreements-protocol.md and in/agreements.json first. Identifiers are literals (no synonyms, no renaming)." + Символы.ПС;
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
		Extra = "Write out/agreements.md first (verbatim identifiers from in/agreements.json). Repeat the gate procedure in tasks.md." + Символы.ПС;
		Если ЗначениеЗаполнено(ПроцедураИмя) Тогда
			Extra = Extra + " Gate procedure: " + ПроцедураИмя + "." + Символы.ПС;
		КонецЕсли;
		Возврат Preamble
			+ "Подготовь утверждаемый план доработки в расширении для product=" + ProductId + "." + Символы.ПС
			+ "Read in/task_brief.md and in/product.json. Research CF via code-index "
			+ "(always pass repo=cf) and sntx_sem (required: search_bsl_syntax or "
			+ "search_help, then get_topic)." + Символы.ПС
			+ Extra
			+ "Write prd.md, architecture.md, tasks.md (labels bsl|metadata|cfe_packaging), "
			+ "cfe-scope.md, workflow-state.md (verification table), "
			+ "manifest.json (apply_mode=none)." + Символы.ПС
			+ "Write at most ONE file per turn (home.write once). Never batch multiple "
			+ "plan files in a single JSON response — large replies fail to parse." + Символы.ПС
			+ "Finish required deliverables (cfe-scope.md, manifest.json) before optional notes." + Символы.ПС
			+ "Return JSON only on every turn.";
	ИначеЕсли Стадия = "yaxunit" Тогда
		Возврат Preamble
			+ "Write YAxUnit tests for the approved plan. Read in/docs/ first "
			+ "(public YAxUnit snapshot). Read in/prd.md, in/tasks.md, in/cfe-scope.md. "
			+ "Before platform BSL in tests, call sntx_sem.search_bsl_syntax or search_help. "
			+ "After writing tests, call bsl-language-server.analyze with srcDir from "
			+ "in/bsl-lint.json (absolute paths). "
			+ "Do not implement the feature. Tests must fail on the baseline CF." + Символы.ПС
			+ GateLine
			+ "Write out/tests/, out/cfe-tests/, test-report.md (cite docs URLs + verification table), "
			+ "manifest.json (apply_mode=none). Return JSON only on every turn.";
	ИначеЕсли Стадия = "coder" Тогда
		Возврат Preamble
			+ "Implement approved bsl/metadata steps from in/tasks.md into out/src/." + Символы.ПС
			+ "Read in/agreements.md and in/tests/ so the change satisfies the YAxUnit tests. "
			+ "Before writing BSL/directives, call sntx_sem.search_bsl_syntax or search_help "
			+ "(then get_topic if needed). After writing sources, call "
			+ "bsl-language-server.analyze with srcDir from in/bsl-lint.json. "
			+ "Do not rename tests. Skip cfe_packaging. Write code-report.md "
			+ "(verification table), files-index.md, "
			+ "manifest.json (apply_mode=none)." + Символы.ПС
			+ "Write at most ONE file per turn (home.write once). Never batch multiple "
			+ "source files in a single JSON response — large replies fail to parse." + Символы.ПС
			+ "Write code-report.md last, after out/src is complete." + Символы.ПС
			+ "Return JSON only on every turn.";
	Иначе
		Возврат Preamble
			+ "Package coder sources from in/coder/ into out/cfe/ per in/cfe-scope.md." + Символы.ПС
			+ "Read in/agreements.md. Copy in/cfe-tests/ to out/cfe-tests/ without rewriting tests. "
			+ "Write implement-report.md (verification table), checklist.md, "
			+ "manifest.json (apply_mode=copy_out)." + Символы.ПС
			+ "Return JSON only on every turn.";
	КонецЕсли;
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
