// Платформенный шаг: ibcmd + копии CF/CFE + чеклист (как run-yaxunit.ps1).

Функция ВыполнитьШаг(CfDir, YaxUnitDir, AgentCfeDir, WorkDir, RequirePlatform) Экспорт
	Окружение.ОбеспечитьКаталог(WorkDir);
	Чеклист = Окружение.ОбъединитьПуть(WorkDir, "platform-checklist.md");
	Ibcmd = НайтиIbcmd();
	Если Не ЗначениеЗаполнено(Ibcmd) Тогда
		Сообщение = "SKIP: ibcmd not found (set IBCMD_PATH or install 1C platform).";
		Сообщить(Сообщение);
		Текст = "# Platform step skipped
			|
			|" + Сообщение + "
			|
			|Prepared paths (for manual run):
			|- CF: " + CfDir + "
			|- YAxUnit CFE: " + YaxUnitDir + "
			|- Agent CFE: " + AgentCfeDir + "
			|";
		Окружение.ЗаписатьТекст(Чеклист, Текст);
		Если RequirePlatform Тогда
			ВызватьИсключение Сообщение;
		КонецЕсли;
		Возврат РезультатШага(0, Сообщение, "");
	КонецЕсли;
	Если Не Окружение.КаталогСуществует(AgentCfeDir) Тогда
		Сообщение = "Agent CFE directory missing: " + AgentCfeDir;
		Если RequirePlatform Тогда
			ВызватьИсключение Сообщение;
		КонецЕсли;
		Сообщить("SKIP: " + Сообщение);
		Возврат РезультатШага(0, "SKIP: " + Сообщение, "");
	КонецЕсли;
	CfgCopy = Окружение.ОбъединитьПуть(WorkDir, "cf");
	ExtYax = Окружение.ОбъединитьПуть(WorkDir, "cfe-yaxunit");
	ExtAgent = Окружение.ОбъединитьПуть(WorkDir, "cfe-agent");
	Окружение.КопироватьДерево(CfDir, CfgCopy);
	Окружение.КопироватьДерево(YaxUnitDir, ExtYax);
	Окружение.КопироватьДерево(AgentCfeDir, ExtAgent);
	IbDir = Окружение.ОбъединитьПуть(WorkDir, "ib");
	Текст = "# 1c-live platform checklist
		|
		|ibcmd: " + Ibcmd + "
		|work: " + WorkDir + "
		|
		|Suggested flow (adjust to your platform version):
		|
		|1. Create file IB under `" + IbDir + "`
		|2. Load configuration from `" + CfgCopy + "`
		|3. Load extension `" + ExtYax + "`
		|4. Load extension `" + ExtAgent + "`
		|5. Run YAxUnit suites referenced by the task expect.yaxunit
		|
		|This harness verifies that inputs exist and platform tooling is discoverable.
		|Full automated unit execution is install-specific; treat a successful discovery
		|plus prepared trees as the optional platform gate for now.
		|";
	Окружение.ЗаписатьТекст(Чеклист, Текст);
	Ок = "OK: platform tools found (" + Ibcmd + "); trees prepared under " + WorkDir;
	Сообщить(Ок);
	Сообщить("See " + Чеклист);
	Возврат РезультатШага(0, Ок + Символы.ПС + "See " + Чеклист, "");
КонецФункции

Функция НайтиIbcmd()
	ИзEnv = Окружение.ПеременнаяСреды("IBCMD_PATH");
	Если Окружение.ФайлСуществует(ИзEnv) Тогда
		Возврат Окружение.АбсолютныйПуть(ИзEnv);
	КонецЕсли;
	Корни = Новый Массив;
	Корни.Добавить("C:\Program Files\1cv8");
	Корни.Добавить("C:\Program Files (x86)\1cv8");
	Кандидаты = Новый Массив;
	Для Каждого Корень Из Корни Цикл
		Если Не Окружение.КаталогСуществует(Корень) Тогда
			Продолжить;
		КонецЕсли;
		Версии = НайтиФайлы(Корень, "*");
		Для Каждого Версия Из Версии Цикл
			Если Не Версия.ЭтоКаталог() Тогда
				Продолжить;
			КонецЕсли;
			Ibcmd = Окружение.ОбъединитьПуть(Версия.ПолноеИмя, "bin", "ibcmd.exe");
			Если Окружение.ФайлСуществует(Ibcmd) Тогда
				Кандидаты.Добавить(Ibcmd);
			КонецЕсли;
		КонецЦикла;
	КонецЦикла;
	Кандидаты = Окружение.СортироватьСтроки(Кандидаты);
	Если Кандидаты.Количество() = 0 Тогда
		Возврат "";
	КонецЕсли;
	Возврат Кандидаты[Кандидаты.ВГраница()];
КонецФункции

Функция РезультатШага(Код, Вывод, Ошибки)
	Результат = Новый Структура;
	Результат.Вставить("Код", Код);
	Результат.Вставить("Вывод", Вывод);
	Результат.Вставить("Ошибки", Ошибки);
	Возврат Результат;
КонецФункции
