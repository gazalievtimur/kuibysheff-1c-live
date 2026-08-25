#!/usr/bin/env python3
"""One-shot generator for the Склад Designer dump + YAxUnit CFE fixture."""

from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF = ROOT / "cf"
CFE = ROOT / "cfe" / "YAxUnit_Tests_Sklad"

NS = (
    'xmlns="http://v8.1c.ru/8.3/MDClasses" '
    'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
    'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
    'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
    'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
    'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
    'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
    'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
    'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
    'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
    'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
    'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
    'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
    'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
    'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
    'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'version="2.20"'
)

# Stable UUIDs for the fixture (not random on each regen).
UID = {
    "cfg": "a1000001-0001-4000-8000-000000000001",
    "lang": "a1000001-0001-4000-8000-000000000002",
    "role": "a1000001-0001-4000-8000-000000000003",
    "enum": "a1000001-0001-4000-8000-000000000010",
    "nomen": "a1000001-0001-4000-8000-000000000020",
    "kontr": "a1000001-0001-4000-8000-000000000021",
    "sklad": "a1000001-0001-4000-8000-000000000022",
    "ceny": "a1000001-0001-4000-8000-000000000030",
    "ostatki": "a1000001-0001-4000-8000-000000000031",
    "prov": "a1000001-0001-4000-8000-000000000040",
    "ceny_mod": "a1000001-0001-4000-8000-000000000041",
    "prihod": "a1000001-0001-4000-8000-000000000050",
    "rashod": "a1000001-0001-4000-8000-000000000051",
    "http": "a1000001-0001-4000-8000-000000000060",
    "form_p": "a1000001-0001-4000-8000-000000000070",
    "form_r": "a1000001-0001-4000-8000-000000000071",
    "cfe": "b2000001-0001-4000-8000-000000000001",
    "tests": "b2000001-0001-4000-8000-000000000010",
}


def _syn(text: str) -> str:
    return (
        f"<Synonym>\n\t\t\t\t<v8:item>\n\t\t\t\t\t"
        f"<v8:lang>ru</v8:lang>\n\t\t\t\t\t"
        f"<v8:content>{text}</v8:content>\n\t\t\t\t"
        f"</v8:item>\n\t\t\t</Synonym>"
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")


def _gen_types(prefix: str, name: str) -> str:
    cats = [
        ("Object", "Object"),
        ("Ref", "Ref"),
        ("Selection", "Selection"),
        ("List", "List"),
        ("Manager", "Manager"),
    ]
    lines = []
    for cat, suffix in cats:
        tid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{prefix}.{name}.{suffix}.t"))
        vid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{prefix}.{name}.{suffix}.v"))
        lines.append(
            f'\t\t\t<xr:GeneratedType name="{prefix}{suffix}.{name}" category="{cat}">\n'
            f"\t\t\t\t<xr:TypeId>{tid}</xr:TypeId>\n"
            f"\t\t\t\t<xr:ValueId>{vid}</xr:ValueId>\n"
            f"\t\t\t</xr:GeneratedType>"
        )
    return "\n".join(lines)


def write_configuration() -> None:
    child = "\n".join(
        [
            "\t\t\t<Language>Русский</Language>",
            "\t\t\t<Role>ПолныеПрава</Role>",
            "\t\t\t<CommonModule>ПроведениеДокументов</CommonModule>",
            "\t\t\t<CommonModule>РаботаСЦенами</CommonModule>",
            "\t\t\t<HTTPService>ОбменСкладом</HTTPService>",
            "\t\t\t<Catalog>Номенклатура</Catalog>",
            "\t\t\t<Catalog>Контрагенты</Catalog>",
            "\t\t\t<Catalog>Склады</Catalog>",
            "\t\t\t<Document>ПриходТовара</Document>",
            "\t\t\t<Document>РасходТовара</Document>",
            "\t\t\t<Enum>ВидыНоменклатуры</Enum>",
            "\t\t\t<InformationRegister>ЦеныНоменклатуры</InformationRegister>",
            "\t\t\t<AccumulationRegister>ОстаткиТоваров</AccumulationRegister>",
        ]
    )
    _write(
        CF / "Configuration.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Configuration uuid="{UID["cfg"]}">
\t\t<InternalInfo/>
\t\t<Properties>
\t\t\t<Name>Склад</Name>
\t\t\t{_syn("Склад (live fixture)")}
\t\t\t<Comment>Kuibysheff 1c-live fixture — original toy warehouse CF</Comment>
\t\t\t<ConfigurationExtensionCompatibilityMode>Version8_3_23</ConfigurationExtensionCompatibilityMode>
\t\t\t<DefaultRunMode>ManagedApplication</DefaultRunMode>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<ScriptVariant>Russian</ScriptVariant>
\t\t\t<DefaultRoles>
\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Role.ПолныеПрава</xr:Item>
\t\t\t</DefaultRoles>
\t\t\t<Vendor>Kuibysheff Live</Vendor>
\t\t\t<Version>1.0.0</Version>
\t\t\t<DefaultLanguage>Language.Русский</DefaultLanguage>
\t\t\t<CompatibilityMode>Version8_3_23</CompatibilityMode>
\t\t</Properties>
\t\t<ChildObjects>
{child}
\t\t</ChildObjects>
\t</Configuration>
</MetaDataObject>
""",
    )


def write_language() -> None:
    _write(
        CF / "Languages" / "Русский.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Language uuid="{UID["lang"]}">
\t\t<Properties>
\t\t\t<Name>Русский</Name>
\t\t\t{_syn("Русский")}
\t\t\t<LanguageCode>ru</LanguageCode>
\t\t</Properties>
\t</Language>
</MetaDataObject>
""",
    )


def write_role() -> None:
    _write(
        CF / "Roles" / "ПолныеПрава.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Role uuid="{UID["role"]}">
\t\t<Properties>
\t\t\t<Name>ПолныеПрава</Name>
\t\t\t{_syn("Полные права")}
\t\t</Properties>
\t</Role>
</MetaDataObject>
""",
    )


def write_enum() -> None:
    _write(
        CF / "Enums" / "ВидыНоменклатуры.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Enum uuid="{UID["enum"]}">
\t\t<InternalInfo>
{_gen_types("Enum", "ВидыНоменклатуры")}
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>ВидыНоменклатуры</Name>
\t\t\t{_syn("Виды номенклатуры")}
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<EnumValue uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'enum.товар')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Товар</Name>
\t\t\t\t\t{_syn("Товар")}
\t\t\t\t</Properties>
\t\t\t</EnumValue>
\t\t\t<EnumValue uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'enum.услуга')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Услуга</Name>
\t\t\t\t\t{_syn("Услуга")}
\t\t\t\t</Properties>
\t\t\t</EnumValue>
\t\t</ChildObjects>
\t</Enum>
</MetaDataObject>
""",
    )


def write_catalog(name: str, synonym: str, uid: str, extra_attrs: str = "") -> None:
    _write(
        CF / "Catalogs" / f"{name}.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Catalog uuid="{uid}">
\t\t<InternalInfo>
{_gen_types("Catalog", name)}
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>{name}</Name>
\t\t\t{_syn(synonym)}
\t\t\t<Hierarchical>false</Hierarchical>
\t\t\t<CodeLength>9</CodeLength>
\t\t\t<DescriptionLength>100</DescriptionLength>
\t\t\t<CodeType>String</CodeType>
\t\t\t<Autonumbering>true</Autonumbering>
\t\t\t<DefaultPresentation>AsDescription</DefaultPresentation>
\t\t</Properties>
\t\t<ChildObjects>
{extra_attrs}
\t\t</ChildObjects>
\t</Catalog>
</MetaDataObject>
""",
    )


def write_nomen_attrs() -> str:
    return f"""\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'nomen.артикул')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Артикул</Name>
\t\t\t\t\t{_syn("Артикул")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t\t\t<v8:Length>50</v8:Length>
\t\t\t\t\t\t</v8:StringQualifiers>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Attribute>
\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'nomen.вид')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>ВидНоменклатуры</Name>
\t\t\t\t\t{_syn("Вид номенклатуры")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:EnumRef.ВидыНоменклатуры</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Attribute>"""


def write_info_register() -> None:
    _write(
        CF / "InformationRegisters" / "ЦеныНоменклатуры.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<InformationRegister uuid="{UID["ceny"]}">
\t\t<InternalInfo>
{_gen_types("InformationRegister", "ЦеныНоменклатуры")}
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>ЦеныНоменклатуры</Name>
\t\t\t{_syn("Цены номенклатуры")}
\t\t\t<InformationRegisterPeriodicity>Day</InformationRegisterPeriodicity>
\t\t\t<WriteMode>Independent</WriteMode>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Dimension uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'ceny.dim.nomen')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Номенклатура</Name>
\t\t\t\t\t{_syn("Номенклатура")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Dimension>
\t\t\t<Resource uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'ceny.res.цена')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Цена</Name>
\t\t\t\t\t{_syn("Цена")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t\t\t<v8:FractionDigits>2</v8:FractionDigits>
\t\t\t\t\t\t</v8:NumberQualifiers>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Resource>
\t\t</ChildObjects>
\t</InformationRegister>
</MetaDataObject>
""",
    )


def write_accum_register() -> None:
    _write(
        CF / "AccumulationRegisters" / "ОстаткиТоваров.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<AccumulationRegister uuid="{UID["ostatki"]}">
\t\t<InternalInfo>
{_gen_types("AccumulationRegister", "ОстаткиТоваров")}
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>ОстаткиТоваров</Name>
\t\t\t{_syn("Остатки товаров")}
\t\t\t<RegisterType>Balance</RegisterType>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Dimension uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'ost.dim.nomen')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Номенклатура</Name>
\t\t\t\t\t{_syn("Номенклатура")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Dimension>
\t\t\t<Dimension uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'ost.dim.sklad')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Склад</Name>
\t\t\t\t\t{_syn("Склад")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Склады</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Dimension>
\t\t\t<Resource uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'ost.res.qty')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Количество</Name>
\t\t\t\t\t{_syn("Количество")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t\t\t<v8:FractionDigits>3</v8:FractionDigits>
\t\t\t\t\t\t</v8:NumberQualifiers>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Resource>
\t\t</ChildObjects>
\t</AccumulationRegister>
</MetaDataObject>
""",
    )


def write_common_module(name: str, uid: str, server: bool = True) -> None:
    _write(
        CF / "CommonModules" / f"{name}.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<CommonModule uuid="{uid}">
\t\t<Properties>
\t\t\t<Name>{name}</Name>
\t\t\t{_syn(name)}
\t\t\t<Server>{str(server).lower()}</Server>
\t\t\t<ClientManagedApplication>false</ClientManagedApplication>
\t\t\t<ExternalConnection>false</ExternalConnection>
\t\t\t<ClientOrdinaryApplication>false</ClientOrdinaryApplication>
\t\t\t<ServerCall>true</ServerCall>
\t\t\t<Global>false</Global>
\t\t\t<Privileged>false</Privileged>
\t\t\t<ReturnValuesReuse>DontUse</ReturnValuesReuse>
\t\t</Properties>
\t</CommonModule>
</MetaDataObject>
""",
    )


def write_document(name: str, uid: str, form_uid: str, register_records: str) -> None:
    _write(
        CF / "Documents" / f"{name}.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Document uuid="{uid}">
\t\t<InternalInfo>
{_gen_types("Document", name)}
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>{name}</Name>
\t\t\t{_syn(name)}
\t\t\t<NumberType>String</NumberType>
\t\t\t<NumberLength>11</NumberLength>
\t\t\t<NumberAllowedLength>Variable</NumberAllowedLength>
\t\t\t<Posting>Allow</Posting>
\t\t\t<RealTimePosting>Allow</RealTimePosting>
\t\t\t<RegisterRecordsDeletion>AutoDelete</RegisterRecordsDeletion>
\t\t\t<RegisterRecordsWritingOnPost>WriteSelected</RegisterRecordsWritingOnPost>
\t\t\t<PostInPrivilegedMode>true</PostInPrivilegedMode>
\t\t\t<UnpostInPrivilegedMode>true</UnpostInPrivilegedMode>
\t\t\t<RegisterRecords>
{register_records}
\t\t\t</RegisterRecords>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.склад')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Склад</Name>
\t\t\t\t\t{_syn("Склад")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Склады</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<FillChecking>ShowError</FillChecking>
\t\t\t\t</Properties>
\t\t\t</Attribute>
\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.контрагент')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Контрагент</Name>
\t\t\t\t\t{_syn("Контрагент")}
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Контрагенты</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t</Properties>
\t\t\t</Attribute>
\t\t\t<Form>ФормаДокумента</Form>
\t\t\t<TabularSection uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч')}">
\t\t\t\t<InternalInfo>
\t\t\t\t\t<xr:GeneratedType name="DocumentTabularSection.{name}.Товары" category="TabularSection">
\t\t\t\t\t\t<xr:TypeId>{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.t')}</xr:TypeId>
\t\t\t\t\t\t<xr:ValueId>{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.v')}</xr:ValueId>
\t\t\t\t\t</xr:GeneratedType>
\t\t\t\t\t<xr:GeneratedType name="DocumentTabularSectionRow.{name}.Товары" category="TabularSectionRow">
\t\t\t\t\t\t<xr:TypeId>{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.row.t')}</xr:TypeId>
\t\t\t\t\t\t<xr:ValueId>{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.row.v')}</xr:ValueId>
\t\t\t\t\t</xr:GeneratedType>
\t\t\t\t</InternalInfo>
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Товары</Name>
\t\t\t\t\t{_syn("Товары")}
\t\t\t\t</Properties>
\t\t\t\t<ChildObjects>
\t\t\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.nomen')}">
\t\t\t\t\t\t<Properties>
\t\t\t\t\t\t\t<Name>Номенклатура</Name>
\t\t\t\t\t\t\t{_syn("Номенклатура")}
\t\t\t\t\t\t\t<Type>
\t\t\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
\t\t\t\t\t\t\t</Type>
\t\t\t\t\t\t</Properties>
\t\t\t\t\t</Attribute>
\t\t\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.qty')}">
\t\t\t\t\t\t<Properties>
\t\t\t\t\t\t\t<Name>Количество</Name>
\t\t\t\t\t\t\t{_syn("Количество")}
\t\t\t\t\t\t\t<Type>
\t\t\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t\t\t\t\t<v8:FractionDigits>3</v8:FractionDigits>
\t\t\t\t\t\t\t\t</v8:NumberQualifiers>
\t\t\t\t\t\t\t</Type>
\t\t\t\t\t\t</Properties>
\t\t\t\t\t</Attribute>
\t\t\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.цена')}">
\t\t\t\t\t\t<Properties>
\t\t\t\t\t\t\t<Name>Цена</Name>
\t\t\t\t\t\t\t{_syn("Цена")}
\t\t\t\t\t\t\t<Type>
\t\t\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t\t\t\t\t<v8:FractionDigits>2</v8:FractionDigits>
\t\t\t\t\t\t\t\t</v8:NumberQualifiers>
\t\t\t\t\t\t\t</Type>
\t\t\t\t\t\t</Properties>
\t\t\t\t\t</Attribute>
\t\t\t\t\t<Attribute uuid="{uuid.uuid5(uuid.NAMESPACE_URL, name + '.тч.сумма')}">
\t\t\t\t\t\t<Properties>
\t\t\t\t\t\t\t<Name>Сумма</Name>
\t\t\t\t\t\t\t{_syn("Сумма")}
\t\t\t\t\t\t\t<Type>
\t\t\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t\t\t\t\t<v8:FractionDigits>2</v8:FractionDigits>
\t\t\t\t\t\t\t\t</v8:NumberQualifiers>
\t\t\t\t\t\t\t</Type>
\t\t\t\t\t\t</Properties>
\t\t\t\t\t</Attribute>
\t\t\t\t</ChildObjects>
\t\t\t</TabularSection>
\t\t</ChildObjects>
\t</Document>
</MetaDataObject>
""",
    )
    _write(
        CF / "Documents" / name / "Forms" / "ФормаДокумента.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Form uuid="{form_uid}">
\t\t<Properties>
\t\t\t<Name>ФормаДокумента</Name>
\t\t\t{_syn("Форма документа")}
\t\t\t<FormType>Managed</FormType>
\t\t</Properties>
\t</Form>
</MetaDataObject>
""",
    )


def write_http_service() -> None:
    _write(
        CF / "HTTPServices" / "ОбменСкладом.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<HTTPService uuid="{UID["http"]}">
\t\t<Properties>
\t\t\t<Name>ОбменСкладом</Name>
\t\t\t{_syn("Обмен складом")}
\t\t\t<RootURL>warehouse</RootURL>
\t\t\t<ReuseSessions>AutoUse</ReuseSessions>
\t\t\t<SessionMaxAge>20</SessionMaxAge>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<URLTemplate uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'http.остатки')}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Остатки</Name>
\t\t\t\t\t{_syn("Остатки")}
\t\t\t\t\t<Template>/остатки</Template>
\t\t\t\t</Properties>
\t\t\t\t<ChildObjects>
\t\t\t\t\t<Method uuid="{uuid.uuid5(uuid.NAMESPACE_URL, 'http.остатки.get')}">
\t\t\t\t\t\t<Properties>
\t\t\t\t\t\t\t<Name>GET</Name>
\t\t\t\t\t\t\t{_syn("GET")}
\t\t\t\t\t\t\t<HTTPMethod>GET</HTTPMethod>
\t\t\t\t\t\t\t<Handler>ОстаткиGET</Handler>
\t\t\t\t\t\t</Properties>
\t\t\t\t\t</Method>
\t\t\t\t</ChildObjects>
\t\t\t</URLTemplate>
\t\t</ChildObjects>
\t</HTTPService>
</MetaDataObject>
""",
    )


def write_bsl_modules() -> None:
    # Planted bug: posting without negative-stock check.
    _write(
        CF / "Documents" / "РасходТовара" / "Ext" / "ObjectModule.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Модуль объекта документа РасходТовара (фикстура 1c-live).
// DEFECT: нет проверки Количество > 0 в ПередЗаписью.
// DEFECT: проведение не контролирует отрицательные остатки.
////////////////////////////////////////////////////////////////////////////////

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)

\t// TODO(live): запретить запись, если в ТЧ Товары есть строки с Количество <= 0.
\t// Сейчас проверка отсутствует намеренно (задача cfe-qty-check-01).

КонецПроцедуры

Процедура ОбработкаПроведения(Отказ, РежимПроведения)

\tДвижения.ОстаткиТоваров.Записывать = Истина;
\tДвижения.ОстаткиТоваров.Очистить();

\tДля Каждого СтрокаТовара Из Товары Цикл

\t\t// TODO(live): перед списанием проверить остаток по ОстаткиТоваров
\t\t// (Номенклатура + Склад). Задача cfe-negative-stock-01.
\t\tДвижение = Движения.ОстаткиТоваров.Добавить();
\t\tДвижение.ВидДвижения = ВидДвиженияНакопления.Расход;
\t\tДвижение.Период = Дата;
\t\tДвижение.Номенклатура = СтрокаТовара.Номенклатура;
\t\tДвижение.Склад = Склад;
\t\tДвижение.Количество = СтрокаТовара.Количество;

\tКонецЦикла;

\tПроведениеДокументов.ДополнитьДвиженияРасхода(ЭтотОбъект, Отказ);

КонецПроцедуры
""",
    )

    _write(
        CF / "Documents" / "ПриходТовара" / "Ext" / "ObjectModule.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Модуль объекта документа ПриходТовара (фикстура 1c-live).
////////////////////////////////////////////////////////////////////////////////

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)

\t// На сервере сумма сейчас не пересчитывается — только на клиенте формы.
\t// DEFECT / задача cfe-form-sum (будущая): пересчёт Сумма = Количество * Цена здесь.

КонецПроцедуры

Процедура ОбработкаПроведения(Отказ, РежимПроведения)

\tДвижения.ОстаткиТоваров.Записывать = Истина;
\tДвижения.ОстаткиТоваров.Очистить();

\tДля Каждого СтрокаТовара Из Товары Цикл

\t\tДвижение = Движения.ОстаткиТоваров.Добавить();
\t\tДвижение.ВидДвижения = ВидДвиженияНакопления.Приход;
\t\tДвижение.Период = Дата;
\t\tДвижение.Номенклатура = СтрокаТовара.Номенклатура;
\t\tДвижение.Склад = Склад;
\t\tДвижение.Количество = СтрокаТовара.Количество;

\tКонецЦикла;

КонецПроцедуры
""",
    )

    _write(
        CF / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Клиентский модуль формы ПриходТовара.
// DEFECT: пересчёт Суммы только на клиенте.
////////////////////////////////////////////////////////////////////////////////

&НаКлиенте
Процедура ТоварыКоличествоПриИзменении(Элемент)

\tСтрока = Элементы.Товары.ТекущиеДанные;
\tЕсли Строка = Неопределено Тогда
\t\tВозврат;
\tКонецЕсли;
\tСтрока.Сумма = Строка.Количество * Строка.Цена;

КонецПроцедуры

&НаКлиенте
Процедура ТоварыЦенаПриИзменении(Элемент)

\tСтрока = Элементы.Товары.ТекущиеДанные;
\tЕсли Строка = Неопределено Тогда
\t\tВозврат;
\tКонецЕсли;
\tСтрока.Сумма = Строка.Количество * Строка.Цена;

КонецПроцедуры
""",
    )

    _write(
        CF / "Documents" / "РасходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Клиентский модуль формы РасходТовара.
// DEFECT: цена не подставляется из РаботаСЦенами / ЦеныНоменклатуры.
////////////////////////////////////////////////////////////////////////////////

&НаКлиенте
Процедура ТоварыНоменклатураПриИзменении(Элемент)

\t// TODO(live): вызвать сервер и заполнить Цену через РаботаСЦенами.ЦенаНоменклатуры.
\tСтрока = Элементы.Товары.ТекущиеДанные;
\tЕсли Строка = Неопределено Тогда
\t\tВозврат;
\tКонецЕсли;
\tСтрока.Сумма = Строка.Количество * Строка.Цена;

КонецПроцедуры

&НаКлиенте
Процедура ТоварыКоличествоПриИзменении(Элемент)

\tСтрока = Элементы.Товары.ТекущиеДанные;
\tЕсли Строка = Неопределено Тогда
\t\tВозврат;
\tКонецЕсли;
\tСтрока.Сумма = Строка.Количество * Строка.Цена;

КонецПроцедуры
""",
    )

    _write(
        CF / "CommonModules" / "ПроведениеДокументов" / "Ext" / "Module.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Общий модуль ПроведениеДокументов (сервер).
////////////////////////////////////////////////////////////////////////////////

Процедура ДополнитьДвиженияРасхода(ДокументОбъект, Отказ) Экспорт

\t// Хук для расширения. Сейчас пустой.
\tЕсли ДокументОбъект = Неопределено Тогда
\t\tОтказ = Истина;
\tКонецЕсли;

КонецПроцедуры
""",
    )

    _write(
        CF / "CommonModules" / "РаботаСЦенами" / "Ext" / "Module.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// Общий модуль РаботаСЦенами (сервер).
// Есть API, но форма РасходТовара его не вызывает.
////////////////////////////////////////////////////////////////////////////////

Функция ЦенаНоменклатуры(Номенклатура, ДатаЦены = Неопределено) Экспорт

\tЕсли Не ЗначениеЗаполнено(Номенклатура) Тогда
\t\tВозврат 0;
\tКонецЕсли;

\tЕсли ДатаЦены = Неопределено Тогда
\t\tДатаЦены = ТекущаяДатаСеанса();
\tКонецЕсли;

\tЗапрос = Новый Запрос;
\tЗапрос.Текст =
\t"ВЫБРАТЬ ПЕРВЫЕ 1
\t|\tЦеныНоменклатуры.Цена КАК Цена
\t|ИЗ
\t|\tРегистрСведений.ЦеныНоменклатуры.СрезПоследних(&ДатаЦены, Номенклатура = &Номенклатура) КАК ЦеныНоменклатуры";
\tЗапрос.УстановитьПараметр("ДатаЦены", ДатаЦены);
\tЗапрос.УстановитьПараметр("Номенклатура", Номенклатура);

\tРезультат = Запрос.Выполнить();
\tВыборка = Результат.Выбрать();
\tЕсли Выборка.Следующий() Тогда
\t\tВозврат Выборка.Цена;
\tКонецЕсли;

\tВозврат 0;

КонецФункции
""",
    )

    # Planted bug: no warehouse filter.
    _write(
        CF / "HTTPServices" / "ОбменСкладом" / "Ext" / "Module.bsl",
        """////////////////////////////////////////////////////////////////////////////////
// HTTP-сервис ОбменСкладом.
// DEFECT: ОстаткиGET не фильтрует по складу (задача cfe-http-filter-01).
////////////////////////////////////////////////////////////////////////////////

Функция ОстаткиGET(Запрос)

\tОтвет = Новый HTTPСервисОтвет(200);
\tОтвет.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");

\t// TODO(live): читать query-параметр "склад" и отбирать ОстаткиТоваров по Склад.
\tЗапросОстатков = Новый Запрос;
\tЗапросОстатков.Текст =
\t"ВЫБРАТЬ
\t|\tОстаткиТоваровОстатки.Номенклатура КАК Номенклатура,
\t|\tОстаткиТоваровОстатки.Склад КАК Склад,
\t|\tОстаткиТоваровОстатки.КоличествоОстаток КАК Количество
\t|ИЗ
\t|\tРегистрНакопления.ОстаткиТоваров.Остатки КАК ОстаткиТоваровОстатки";

\tРезультат = ЗапросОстатков.Выполнить().Выгрузить();
\tОтвет.УстановитьТелоИзСтроки(СформироватьJSONОстатков(Результат));
\tВозврат Ответ;

КонецФункции

Функция СформироватьJSONОстатков(ТаблицаОстатков)

\t// Упрощённая сериализация для фикстуры.
\tЧасти = Новый Массив;
\tДля Каждого Строка Из ТаблицаОстатков Цикл
\t\tЧасти.Добавить(СтрШаблон(
\t\t\t"{""nomenclature"":""%1"",""warehouse"":""%2"",""qty"":%3}",
\t\t\tСтрока(Строка.Номенклатура),
\t\t\tСтрока(Строка.Склад),
\t\t\tФормат(Строка.Количество, "ЧГ=0")));
\tКонецЦикла;
\tВозврат "[" + СтрСоединить(Части, ",") + "]";

КонецФункции
""",
    )


def write_yaxunit_cfe() -> None:
    _write(
        CFE / "Configuration.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<Configuration uuid="{UID["cfe"]}">
\t\t<InternalInfo/>
\t\t<Properties>
\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>
\t\t\t<Name>YAxUnit_Tests_Sklad</Name>
\t\t\t{_syn("YAxUnit Tests Склад")}
\t\t\t<ConfigurationExtensionPurpose>Customization</ConfigurationExtensionPurpose>
\t\t\t<KeepMappingToExtendedConfigurationObjectsByIDs>true</KeepMappingToExtendedConfigurationObjectsByIDs>
\t\t\t<NamePrefix>СкладТест_</NamePrefix>
\t\t\t<ConfigurationExtensionCompatibilityMode>Version8_3_23</ConfigurationExtensionCompatibilityMode>
\t\t\t<ScriptVariant>Russian</ScriptVariant>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<CommonModule>СкладТест_РасходТовара</CommonModule>
\t\t\t<CommonModule>СкладТест_HTTP</CommonModule>
\t\t</ChildObjects>
\t</Configuration>
</MetaDataObject>
""",
    )

    for mod_name, body in (
        (
            "СкладТест_РасходТовара",
            """// YAxUnit-style acceptance checks for РасходТовара (fixture).
// Loaded only when -RequirePlatform is set.

Процедура Тест_КоличествоНоль_НеЗаписывается() Экспорт
\t// Ожидание после CFE агента: ПередЗаписью отказывает запись при Количество <= 0.
КонецПроцедуры

Процедура Тест_ОтрицательныеОстатки_НеПроводится() Экспорт
\t// Ожидание: проведение в минус по ОстаткиТоваров запрещено.
КонецПроцедуры
""",
        ),
        (
            "СкладТест_HTTP",
            """// YAxUnit-style acceptance checks for ОбменСкладом.

Процедура Тест_ФильтрПоСкладу() Экспорт
\t// Ожидание: GET /остатки?склад=... возвращает только строки выбранного склада.
КонецПроцедуры
""",
        ),
    ):
        mod_uid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"cfe.{mod_name}"))
        _write(
            CFE / "CommonModules" / f"{mod_name}.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS}>
\t<CommonModule uuid="{mod_uid}">
\t\t<Properties>
\t\t\t<Name>{mod_name}</Name>
\t\t\t{_syn(mod_name)}
\t\t\t<Server>true</Server>
\t\t\t<ServerCall>true</ServerCall>
\t\t\t<Global>false</Global>
\t\t</Properties>
\t</CommonModule>
</MetaDataObject>
""",
        )
        _write(CFE / "CommonModules" / mod_name / "Ext" / "Module.bsl", body)


def main() -> None:
    write_configuration()
    write_language()
    write_role()
    write_enum()
    write_catalog("Номенклатура", "Номенклатура", UID["nomen"], write_nomen_attrs())
    write_catalog("Контрагенты", "Контрагенты", UID["kontr"])
    write_catalog("Склады", "Склады", UID["sklad"])
    write_info_register()
    write_accum_register()
    write_common_module("ПроведениеДокументов", UID["prov"])
    write_common_module("РаботаСЦенами", UID["ceny_mod"])
    rr = (
        '\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">'
        "AccumulationRegister.ОстаткиТоваров</xr:Item>"
    )
    write_document("ПриходТовара", UID["prihod"], UID["form_p"], rr)
    write_document("РасходТовара", UID["rashod"], UID["form_r"], rr)
    write_http_service()
    write_bsl_modules()
    write_yaxunit_cfe()
    print(f"OK: fixture written under {CF} and {CFE}")


if __name__ == "__main__":
    main()
