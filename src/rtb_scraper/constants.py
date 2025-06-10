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
    "determination": "https://www.rtb.ie/search-results/listing?collection=adjudication_orders|determination_order",
    "tribunal": "https://www.rtb.ie/search-results/listing?collection=adjudication_orders|tribunal_orders",
}

PAGINATED_URLS = {
    "determination": "https://www.rtb.ie/search-results/listing/P{pn}0?collection=adjudication_orders|determination_orders",
    "tribunal": "https://www.rtb.ie/search-results/listing/P{pn}0?collection=adjudication_orders|tribunal_orders",
}

PROPERTY_COUNTY_URL = "https://portal.rtb.ie/webapi/RegisterSearch/GetRegisteredDwellingDetails?addressLine1=&eircode=&countyId={county_id}"

EIRCODE_PATTERN = re.compile(
    r"([AC-FHKNPRTV-Y]\d{2}|D6W)\s?[0-9AC-FHKNPRTV-Y]{4}",
    re.IGNORECASE
)

BAD_ADDRESS_PREFIXES = [", ", "at ", "situate at ", "known as "]

REPLACE_TEXT_IN_DETERMINATION = [
    ("Decernber", "December"),
    ("tenancy at the dwelling at", "dwelling at"),
    ("dweiling", "dwelling"),
    ("dweiling", "dwelling"),
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
}
