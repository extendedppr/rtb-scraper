import re


COUNTY_ID_MAP = {
    "3b4cd92b-c49b-e811-a870-000d3a274eca": "Carlow",
    "1b4cd92b-c49b-e811-a870-000d3a274eca": "Cavan",
    "2d4cd92b-c49b-e811-a870-000d3a274eca": "Clare",
    "2b4cd92b-c49b-e811-a870-000d3a274eca": "Cork",
    "274cd92b-c49b-e811-a870-000d3a274eca": "Donegal",
    "1d4cd92b-c49b-e811-a870-000d3a274eca": "Dublin",
    "154cd92b-c49b-e811-a870-000d3a274eca": "Galway",
    "454cd92b-c49b-e811-a870-000d3a274eca": "Kerry",
    "394cd92b-c49b-e811-a870-000d3a274eca": "Kildare",
    "1f4cd92b-c49b-e811-a870-000d3a274eca": "Kilkenny",
    "214cd92b-c49b-e811-a870-000d3a274eca": "Laois",
    "354cd92b-c49b-e811-a870-000d3a274eca": "Leitrim",
    "174cd92b-c49b-e811-a870-000d3a274eca": "Limerick",
    "474cd92b-c49b-e811-a870-000d3a274eca": "Longford",
    "434cd92b-c49b-e811-a870-000d3a274eca": "Louth",
    "334cd92b-c49b-e811-a870-000d3a274eca": "Mayo",
    "3d4cd92b-c49b-e811-a870-000d3a274eca": "Meath",
    "414cd92b-c49b-e811-a870-000d3a274eca": "Monaghan",
    "374cd92b-c49b-e811-a870-000d3a274eca": "Offaly",
    "254cd92b-c49b-e811-a870-000d3a274eca": "Roscommon",
    "2f4cd92b-c49b-e811-a870-000d3a274eca": "Sligo",
    "3f4cd92b-c49b-e811-a870-000d3a274eca": "Tipperary",
    "314cd92b-c49b-e811-a870-000d3a274eca": "Waterford",
    "234cd92b-c49b-e811-a870-000d3a274eca": "Westmeath",
    "294cd92b-c49b-e811-a870-000d3a274eca": "Wexford",
    "194cd92b-c49b-e811-a870-000d3a274eca": "Wicklow",
}

BASE_URLS = {
    "tribunal": "https://rtb.ie/disputes/dispute-outcomes-and-orders/adjudication-and-tribunal-orders/?_adjudication_orders_and_tribunal_orders_date={year}&_paged={page_no}",
    "enforcement": "https://rtb.ie/disputes/dispute-outcomes-and-orders/court-decisions-enforcement-orders/?_court_decisions_enforcement_of_orders_date={year}&_paged={page_no}",
}

PAGINATED_URLS = {
    "determination": "https://www.rtb.ie/search-results/listing/P{pn}0?collection=adjudication_orders|determination_orders",
    "tribunal": "https://www.rtb.ie/search-results/listing/P{pn}0?collection=adjudication_orders|tribunal_orders",
}

PROPERTY_COUNTY_URL = "https://portal.rtb.ie/webapi/RegisterSearch/GetRegisteredDwellingDetails?addressLine1=&eircode=&countyId={county_id}"

EIRCODE_PATTERN = re.compile(
    r"([AC-FHKNPRTV-Y]\d{2}|D6W)\s?[0-9AC-FHKNPRTV-Y]{4}", re.IGNORECASE
)

BAD_ADDRESS_PREFIXES = [", ", "at ", "situate at ", "known as "]

GENERAL_REPLACE_TEXT = [
    ("Decernber", "December"),
    ("treland", "Ireland"),
    ("!reland", "Ireland"),
    ("tenancy at the dwelling at", "dwelling at"),
    ("dweiling", "dwelling"),
    ("dwelling in excess", ""),  # otherwise might confuse for address
    ("“the dwelling”", ""),  # otherwise might confuse for address
    ("dwelling was", ""),  # otherwise might confuse for address
    ("tfreland", "Ireland"),
    ("Fiat", "Flat"),
    ("¥", "Y"),
    ("  ", " "),
    ("\n", " "),
]

PDF_ADDRESS_MAP = {
    "D.O_._0924-99345_.pdf": "15 Chapel Square, Old Chapel Lane, Castleisland, County Kerry, V92 WY63",
    "D.O_._0424-95266_.pdf": "Apartment 36, Clifden House, Handsfield Station Quarter, Station Road, Dublin 15",
    "D.O_._0724-97685_.pdf": "",
    "D.O_._0824-98314_.pdf": "Flat 1, 19 Old Cabra Road, Dublin 7, DO7 C1F9",
    "D.O_._0821-72184_.pdf": "Apartment 8, Block D, 78 Reuben Street, Herberion, Rialto, Dublin 8",
    "D.O_._1021-73577_.pdf": "45 The Grange, Letterkenny, Co. Donegal, F92PX2X",
    "D.O_._0721-71188_.pdf": "23 Whites Villas, Dalkey, Dublin A96EDO0",
    "D.O_._1121-73752_.pdf": "7 Fairfield Close, Adamstown, Co. Wexford, Y21HK72",
    "D.O_._0224-93148_.pdf": "Banna Springs, Banna East, Ardfert, Co. Kerry",
    "TR0221-004752_Determination_Order.pdf": "Apartment 1, 14 Heytesbury Street, Portobello, Dublin 8, DO8H2HO",
    "TR1020-004471_Determination_Order.pdf": "",
    "TR0819-003939_Determination_Order.pdf": "44 Charlemont Estate, Griffith Avenue, Marino, Dublin 9",
    "TR0423-006171-DR0922-80030_Determination_Order.pdf": "193 Mellowes Road, Finglas, Dublin 11 D11P2R4",
}

# TODO: PDF_ADDRESS_MAP to fix
"""
)|D.O_._1020-65960_.pdf
a|TR0224-007210-DR1123-90923_DO_-_Redacted.pdf
to|D.O_._0519-54120_.pdf
”)|D.O_._0121-67531_.pdf
”)|D.O_._0321-68514_.pdf
”)|D.O_._0221-67658_.pdf
’)|D.O_._1120-66140_.pdf
’)|D.O_._0321-68582_.pdf
’)|D.O_._0922-79897_.pdf
to|D.O_._0219-51688_.pdf
to|D.O_._0620-62445_.pdf
”)|D.O_._0820-64218_.pdf
”)|D.O_._0220-60516_.pdf
’)|D.O_._0920-64982_.pdf
”)|D.O_._1120-66216_.pdf
”)|D.O_._1121-74136_.pdf
”)|TR1222-005845-DR0822-79210_Determination_Order.pdf
in|TR0124-007090-DR1023-89713_Determination_Order.pdf
”)|TR0124-007083-DR1023-89825_Determination_Order.pdf
”)|TR0923-006754-DO.pdf
”)|TR0924-007986_-_DR0224-93217_Determination_Order.pdf
”)|TR0619-003817_Determination_Order.pdf
”)|TR0322-005329-DR0921-72426_Determination_Order.pdf
”)|TR0424-007477_Determination_Order.pdf
”)|TR1023-006809-DR0723-87167_Determination_Order.pdf
”)|TR1123-006935-DO.pdf
”)|TR0324-007274-DO_1.pdf
’)|TR1124-008202_-_DR0424-95219_Determination_Order.pdf
”)|TR0924-007975-DR0624-96735_DO.pdf
”)|TR1024-008108-DR0524-96140_Determination_Order.pdf
in|TR0920-004438_Determination_Order.pdf
”)|TR0123-005921-DR1022-80500_Determination_Order.pdf
”)|TR0124-007139-DR1123-90415_Determination_Order.pdf
”)|TR0224-007241-DR0124-92327_Determination_Order.pdf
”)|TR0523-006255-DR0323-83341_Determination_Order.pdf
’)|TR1023-006791-DO_1_.pdf
’)|DR0922-80236_Determination_Order.pdf
”)|TR1024-008115-DR0723-87062_Determination_Order.pdf
”)|TR0123-005909-DR0922-80160_Determination_Order.pdf
’)|TR0324-007330_Tribunal_Report_DO.pdf
”)|TR1123-006906-DR0823-88170_Determination_Order.pdf
”)|TR1124-008210-DR0724-97738_Determination_Order.pdf
’)|TR0320-004254_Determination_Order.pdf
”)|TR0323-006080-DR0123-82259_Determination_Order_1.pdf
”)|TR0619-003781_Determination_Order.pdf
”)|TR0424-007433-DR1123-90867_Determination_Order.pdf
”)|TR1123-006919-DR0923-88521_Determination_Order.pdf
”)|TR0623-006319-DR0922-80170_Amended_Determination_Order.pdf
’)|TR0223-006016_DR0123-82195_Determination_Order.pdf
”)|TR0223-005998-DR0922-79788_Determination_Order.pdf
”)|TR0323-006043_DR1222-81901_Determination_Order.pdf
’)|TR1024-008106-DR0824-98254_Determination_Order.pdf
”);|D.O_._0920-64921_.pdf
. 3|D.O_._0422-76785_.pdf
’,)|D.O_._0221-67659_0321-68738_.pdf
and|TR0719-003885_Determination_Order.pdf
. 3|TR1020-004473_Determination_Order.pdf
and in|0118-39894.pdf
served|TR0824-007838_-_DR0324-94466_DO.pdf
and the|D.O_._1218-50510_.pdf
contrary|D.O_._0521-69553_.pdf
and that|0218-40989.pdf
Apt 16 (|D.O_._0418-43178_.pdf
such sum|TR0921-005099-DR0621-70254_DO.pdf
€1800.00|TR0523-006256-DR0123-82207_Determination_Order.pdf
in regard|D.O_._0919-57013_1019-58010_.pdf
of €1,000|D.O_._0224-93148_.pdf
is upheld|D.O_._0720-63132_0720-63446_.pdf
is upheld|D.O_._1021-73166_.pdf
is upheld|D.O_._0923-89256_.pdf
is upheld|D.O_._0919-56804_.pdf
is vacated|D.O_._0923-89198_.pdf
is vacated|D.O_._0320-61299_.pdf
of €712.44|D.O_._0719-55823_.pdf
of €363.20|TR0822-005684_DR1121-73750_Determination_Order.pdf
a dwelling|TR0922-005731-DR0122-74753_Determination_Order.pdf
in relation|TR0222-005298-DR0419-53913_DO.pdf
as required|TR0423-006156-DR0323-83771_Determination_Order_1.pdf
in breach of|D.O_._0220-60522_.pdf
on behalf of|D.O_._0122-74768_.pdf
the dwelling|D.O_._0220-60752_0717-35821_.pdf
is currently|TR0321-004845_Determination_Order.pdf
the dwelling|TR1021-005136-DR0521-69890_DO.pdf
is not upheld|D.O_._0724-97292_.pdf
of €17,928.00|D.O_._1123-91275_.pdf
is not upheld|TR0523-006293_Determination_Order.pdf
is not upheld|TR0324-007299-DR0124-92260_Determination_Order.pdf
is not upheld|TR0323-006097-DR1222-81774_Determination_Order.pdf
is not upheld|TR1024-008088_-_DR0824-98087_Determination_Order.pdf
arising out of|D.O_._1223-92003_.pdf
having deduced|D.O_._1018-49736_1018-49737_.pdf
and facilitate|D.O_._0624-96906_.pdf
and facilitate|D.O_._0824-98203_.pdf
and in allowing|D.O_._1117-38858_.pdf
05 January 2018|0118-40074.pdf
damages of €1,000|TR0524-007494_Determination_Order.pdf
is Mr Gavin Lennon|TR0221-004671_Determination_Order.pdf
is deemed abandoned|D.O_._0222-75646_0722-78631_.pdf
on 5th October 2022|DR1022-80323_Determination_Order.pdf
16/02/2024 and served|D.O_._0424-94920_.pdf
on 12th November 2021|D.O_._0222-75362_.pdf
and €50 for breach of|D.O_._0320-60969_.pdf
and €2,000 in damages|TR0220-004179_Determination_Order.pdf
without the consent of|1117-39038.pdf
and unjustly depriving|D.O_._0319-53085_.pdf
after the service of a|D.O_._0818-47507_.pdf
and in failing to allow|D.O_._0121-67315_.pdf
; and damages of €1,000|TR0919-004016_Determination_Order.pdf
served on 9 October 2018|D.O_._1018-49331_.pdf
since 27 September, 2017|TR0118-002796_Determination_Order.pdf
commencing on the date of|D.O_._0623-86430_.pdf
without written permission|D.O_._1018-49275_.pdf
beyond normal wear and tear|TR0423-006171-DR0922-80030_Determination_Order.pdf
on or before 31 January 2023|TR0121-004610_DR0720-63014_Determination_Order.pdf
in breach of Section 12 {ii)|1017-38426_DO.pdf
in breach of her obligations|D.O_._1220-66789_.pdf
is €1,100 per month, payable|D.O_._0719-56135_.pdf
as a result of the failure of|D.O_._0818-47718_.pdf
as it falls due, with respect|D.O_._0921-72553_.pdf
without the written consent of|D.O_._1019-57572_.pdf
the said dwelling, the terms of|TR1024-008118_-_DR0624-96551_Determination_Order.pdf
constitute a substantial change|TR0319-003654_Determination_Order.pdf
under section 12 of the Act and|TR1023-006779-DR0723-87281_Determination_Order.pdf
the said dwelling, the terms of|TR0724-007692_-_DR0124-92303_Determination_Order.pdf
by breach of tenant obligations|D.O_._0824-98265_.pdf
and the Tribunal does not uphold|DR0223-83113_Determination_Order.pdf
less rent arrears of €3,000 owed|TR0319-003645_Determination_Order.pdf
pursuant to Section 12 of the Act|TR0124-007111-DR1123-90384_Determination_Order.pdf
and damages of €900 for breach of|TR0420-004312_Determination_Order.pdf
in excess of normal wear and tear|D.O_._0321-68640_.pdf
in excess of normal wear and tear|D.O_._0618-45444_.pdf
in excess of normal wear and tear|D.O_._0621-70021_.pdf
in excess of normal wear and tear|D.O_._1020-65237_.pdf
in excess of normal wear and tear|D.O_._1120-66487_.pdf
contrary to section 56 of the Act|D.O_._1019-57764_.pdf
in excess of normal wear and tear|D.O_._0720-63033_.pdf
contrary to section 56 of the Act|TR1117-002686_-DR_0617-35184_Determination_Order.pdf
in excess of normal wear and tear|D.O_._0819-56424_.pdf
in excess of normal wear and tear|D.O_._0719-56155_.pdf
in breach of section 12 of the Act|TR0723-006500-DR0423-84767_Determination_Order.pdf
in line with the standard required|D.O_._0724-97888_.pdf
and breach of landlord obligations|D.O_._1019-57805_.pdf
for breaches of Tenant obligations|D.O_._0624-96734_0524-95736_.pdf
"""


DISPUTE_TYPES = [
    "rent-arrears",
    "overholding",
    "breach-of-landlord-obligations",
    "validity-of-notice-of-termination",
    "other",
    "rent-arrears-and-overholding",
    "deposit-retention",
    "standard-and-maintenance-of-dwelling",
    "breach-of-tenant-obligations",
    "antisocial-behaviour",
    "unlawful-termination-of-tenancy",
    "damage-in-excess-of-normal-wear-and-tear",
    "rent-more-than-market-rate",
    "breach-of-fixed-term-lease",
]

MAIN_TYPES = ["adjudication-order", "tribunal-order"]


POST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "Origin": "https://rtb.ie",
}


DETERMINATION_ORDER_DATE_REPLACEMENTS = {
    ("duly", "july"),
    ("218", "2018"),
    ("Septemeber", "September"),
    ("Aprii", "April"),
    ("Novernber", "November"),
    ("dune", "june"),
}


TRIBUNAL_REGEXES = [
    re.compile(
        r"Tribunal\sReference\sNo:\s(?P<tribunal_ref_no>[^\s/]+)\s/\sCase\sRef\sNo:\s(?P<case_ref_no>[^\s]+)\s*",
        re.VERBOSE,
    ),
    re.compile(r"Tenant:\s*(?P<tenant>.*?)\s+(Respondent|Address)"),
    re.compile(r"Landlord:\s*(?P<landlord>.*?)\s+(Respondent|Address)"),
    re.compile(
        r"Address of Rented Dwelling:\s*(?P<address>.*?)\s*Tribunal:",
    ),
    re.compile(r"Applicant\s(?P<applicant>\w+)"),
]

RTB_REFRESH_URL = "https://rtb.ie/wp-json/facetwp/v1/refresh"
