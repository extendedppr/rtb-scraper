import os
from datetime import datetime

from unittest import TestCase

from rtb_scraper.determination import (
    Determination,
    DeterminationDB,
    extract_determination_data_from_text,
)


class DeterminationTest(TestCase):

    def test_extract_determination_data_from_text_order_date(self):
        data = [
            (
                """Dublin 6.
This Order was made by the Residential Tenancies Board on 29 January 2025.
x
7""",
                datetime(2025, 1, 29, 0, 0),
            ),
            (
                """Dublin 6.
This Order was made by the Residential! Tenancies Board on 29 January 2025.
x
7""",
                datetime(2025, 1, 29, 0, 0),
            ),
        ]

        for text, expected_address in data:
            self.assertEqual(
                extract_determination_data_from_text(text, None).get("order_date"),
                expected_address,
            )

    def test_extract_determination_data_from_text_address(self):

        data = [
            (
                """Residential Tenancies Act 2004, determines that:
In respect of the tenancy of the dwelling at 45 Kerlogue Manor, Rocksborough, Wexford,
Y35 PN7X:
1.
The arrears of rent as at 16 October 2024, the day before the Adjudication Hearing,
are €2,257.98.""",
                "45 Kerlogue Manor, Rocksborough, Wexford, Y35 PN7X",
            ),
            (
                """The Notice of Termination dated 19th July 2024 served by the Applicant Landlord on
the Respondent Tenants in resect of the tenancy of the dwelling located 18 The Walk,
Carrickmines Green, Carrickmines, Dublin 18 is valid.
2.
The Tenant and""",
                "18 The Walk, Carrickmines Green, Carrickmines, Dublin 18",
            ),
            (
                """The Notice of Termination dated 19th July 2024 served by the Applicant Landlord on
the Respondent Tenants in resect of the tenancy of the dwelling located at 17 The Walk,
Carrickmines Green, Carrickmines, Dublin 18 is valid.
2.
The Tenant and""",
                "17 The Walk, Carrickmines Green, Carrickmines, Dublin 18",
            ),
            (
                """in respect of the
tenancy at the dwelling at 4 Parnell Road, Harolds Cross, Dublin 12 is not upheld.""",
                "4 Parnell Road, Harolds Cross, Dublin 12",
            ),
            (
                """tenancy of the
dwelling at Apartment 14, The Maples, Clonshaugh Woods, Dublin 17, D17DX97, is valid.
2.""",
                "Apartment 14, The Maples, Clonshaugh Woods, Dublin 17, D17DX97",
            ),
            (
                """Respondent Tenant,
in respect of the
tenancy of the dwelling 32 Cherry Orchard Court, Ballyfermot, Dublin 10, D10VA06, is valid.
2.""",
                "32 Cherry Orchard Court, Ballyfermot, Dublin 10, D10VA06",
            ),
            (
                """served by the Applicant
Landlord on the Respondent Tenant with regard to the rented dwelling at 76 The Woods,
Ballymacool, Letterkenny, County Donegal is invalid.
This Order was made by the""",
                "76 The Woods, Ballymacool, Letterkenny, County Donegal",
            ),
            (
                """deposit in relation to the dwelling at
Churchtown, Kilrane, Rosslare Harbour, Wexford is not upheld.""",
                "Churchtown, Kilrane, Rosslare Harbour, Wexford",
            ),
            (
                """ the tenancy of the dwelling at 3 The Rise, Heatherside, Arklow, Co Wicklow,
Y14AK26;
*
Th""",
                "3 The Rise, Heatherside, Arklow, Co Wicklow, Y14AK26",
            ),
            (
                """Order, in respect of the tenancy of
the dweiling at Apartment 3, Sorcha Housel, Man Street, Passage West, Cork, T12 A3W9.
This Order was made""",
                "Apartment 3, Sorcha Housel, Man Street, Passage West, Cork, T12 A3W9",
            ),
            (
                """the disputed dwelling at Flat 1, 19 Old
Cabra Road, Dublin 7, DO7 C1F9 is valid.
5.
The """,
                "Flat 1, 19 Old Cabra Road, Dublin 7, DO7 C1F9",
            ),
            (
                """respect of the disputed dwelling
at 26 Ballyduff Park, Lifford, Co. Donegal, F93 XE2W is valid.
3.
The Respondent""",
                "26 Ballyduff Park, Lifford, Co. Donegal, F93 XE2W",
            ),
            (
                """tenancy of the dwelling at117 Ashley Hall, St
Edmunds Park, Lucan, Co. Dublin, K78 E7K7 is invalid.""",
                "117 Ashley Hall, St Edmunds Park, Lucan, Co. Dublin, K78 E7K7",
            ),
            (
                """of the tenancy at, 15 Homestead Court, Quarry Road, Cabra, Dublin 7, is
valid.""",
                "15 Homestead Court, Quarry Road, Cabra, Dublin 7",
            ),
            (
                """respect of the tenancy of the dwelling
at,
139A Walkinstown
Drive,
Dublin
12,
is
valid""",
                "139A Walkinstown Drive, Dublin 12",
            ),
            (
                """ApplicantTenant's tenancy of Gillivan’s Butchers, Lower Main Street,
Moate, Westmeath, N37 X3F6.
This Order was made by""",
                "Gillivan’s Butchers, Lower Main Street, Moate, Westmeath, N37 X3F6",
            ),
            (
                """the
dwelling at at 27 Heatherton Park, South Douglas Road, Cork is valid.""",
                "27 Heatherton Park, South Douglas Road, Cork",
            ),
            (
                """tenancy
ofthe dwelling at 7 Highfields, Ballyshannon, Co Donegal.
This Order was made by the Residential Tenancies Board""",
                "7 Highfields, Ballyshannon, Co Donegal",
            ),
            (
                """The Respondent Landlord shall pay the total sum of €2,000.00 to the Applicant Tenant,
within 28 days of the date of issue of the Determination Order, being damages for breach
of landlord obligations in respect of the standard and maintenance of the dwelling pursuant
to section 12(1){b) of the Act and/or for failure to carry out necessary repairs, in respect of
the tenancy of the dwelling at Ballyyoreen, Roscarbery, Co Cork, P85 KR64.
This Order was made by the Residential Tenancies Board on 15 November 2023.""",
                "Ballyyoreen, Roscarbery, Co Cork, P85 KR64",
            ),
        ]

        for text, expected_address in data:
            self.assertEqual(
                extract_determination_data_from_text(text, None).get("address"),
                expected_address,
            )

        base_resources = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test/test_resources/",
        )

        data = [
            (
                "Determination_Order_200.txt.pdf.txt",
                {
                    "reference_number": "TR1018-003312",
                    "respondent_landlord": "Ken Fennel (Receiver over certain assets of John Trears and Kristen Trears",
                    "applicant_tenant": "Stephen Pascaniuc",
                    "order_date": datetime(2019, 2, 14, 0, 0),
                    "address": "24 Charnwood Park, Clonsilla, Dublin 15",
                },
                "Determination_Order_200.pdf",
            ),
            (
                "Determination_Order_7.txt.pdf.txt",
                {
                    "reference_number": "TR0218-002819",
                    "respondent_landlord": "Stephen Tenant, Receiver Over Certain Assets of Pauline and Brendan Fowler c/o Grant Thornton",
                    "applicant_tenant": "Lauryans Bagonas",
                    "order_date": datetime(2018, 7, 10, 0, 0),
                    "address": "1 An T-Ullghort, Rope Walk, Kilnacloy, Monaghan",
                },
                "Determination_Order_7.pdf",
            ),
            (
                "Determination_Order_96.txt.pdf.txt",
                {
                    "reference_number": "TR0118-002809",
                    "respondent_landlord": "Brian Bourke",
                    "applicant_tenant": "Jason Keating",
                    "order_date": datetime(2018, 8, 30, 0, 0),
                    "address": "the commencement of the tenancy term in",
                },
                "Determination_Order_96.pdf",
            ),
            (
                "TR0221-004752_Determination_Order.txt.pdf.txt",
                {
                    "reference_number": "TR0221-004752",
                    "applicant_tenant": "Tevian Mirrelson",
                    "order_date": datetime(2021, 4, 21, 0, 0),
                    "address": "Apartment 1, 14 Heytesbury Street, Portobello, Dublin 8, DO8H2HO",
                    "respondent_landlord": "Caroline Kennedy",
                },
                "TR0221-004752_Determination_Order.pdf",
            ),
            (
                "TR1020-004471_Determination_Order.txt.pdf.txt",
                {
                    "reference_number": "TR1020-004471",
                    "respondent_tenant": "Taylor Byrne, Dylan Byrne",
                    "order_date": datetime(2021, 5, 19, 0, 0),
                    "address": "",
                    "applicant_landlord": "TestCheckpointerAnn Marie Horan",
                },
                "TR1020-004471_Determination_Order.pdf",
            ),
            (
                "TR0819-003939_Determination_Order.txt.pdf.txt",
                {
                    "reference_number": "TR0819-003939",
                    "respondent_tenant": "Raymond Halpin",
                    "applicant_landlord": "Declan Cleary",
                    "order_date": datetime(2019, 11, 28, 0, 0),
                    "address": "44 Charlemont Estate, Griffith Avenue, Marino, Dublin 9",
                },
                "TR0819-003939_Determination_Order.pdf",
            ),
            (
                "TR0320-004274_Determination_Order.txt.pdf.txt",
                {
                    "reference_number": "TRO320-004274",
                    "respondent_landlord": "Tuath Housing Association",
                    "applicant_tenant": "Marguerite O Driscoll",
                    "order_date": datetime(2021, 1, 28, 0, 0),
                    "address": "31 Meadow Crescent, The Meadows Hollyhill, Cork",
                },
                "TR0320-004274_Determination_Order.pdf",
            ),
            (
                "TR0919-003968_Determination_Order.txt.pdf.txt",
                {
                    "reference_number": "TR0919-003968",
                    "respondent_landlord": "Susannah Denardo",
                    "applicant_tenant": "Audrius Karosas",
                    "order_date": datetime(2020, 1, 9, 0, 0),
                    "address": "12 Jervis Lane Upper, Dublin 1, D01 F2P6, as the used",
                },
                "TR0919-003968_Determination_Order.pdf",
            ),
        ]

        for d in data:
            content = open(os.path.join(base_resources, d[0]), "r").read()
            self.assertEqual(extract_determination_data_from_text(content, d[2]), d[1])

    def test_repr(self):
        determination_obj = Determination(
            address="address",
            applicant_landlord="applicant_landlord",
            applicant_tenant="applicant_tenant",
            order_date=datetime(2024, 1, 1),
            reference_number="reference_number",
            respondent_tenant="respondent_tenant",
            respondent_landlord="respondent_landlord",
            subject="subject",
            source_pdf="a.pdf",
        )
        self.assertEqual(
            str(determination_obj),
            'Determination(address="address", applicant_landlord="applicant_landlord", applicant_tenant="applicant_tenant", order_date="2024-01-01 00:00:00", reference_number="reference_number", respondent_tenant="respondent_tenant", respondent_landlord="respondent_landlord", subject="subject", source_pdf="a.pdf")',
        )


class DeterminationDBTest(TestCase):

    def setUp(self):
        determination_db = DeterminationDB()
        determination_db.drop_data()

    def test_insert(self):
        determination_db = DeterminationDB()
        self.assertEqual(len(determination_db), 0)
        determination_obj = Determination(
            address="address",
            applicant_landlord="applicant_landlord",
            applicant_tenant="applicant_tenant",
            order_date=datetime(2024, 1, 1),
            reference_number="reference_number",
            respondent_tenant="respondent_tenant",
            respondent_landlord="respondent_landlord",
            subject="subject",
            source_pdf="a.pdf",
        )
        determination_db.insert(determination_obj)
        self.assertEqual(len(determination_db), 1)
        determination_db.insert(determination_obj)
        self.assertEqual(len(determination_db), 1)

    def test_filter(self):
        determination_db = DeterminationDB()
        determination_db.insert(
            Determination(
                address="address",
                applicant_landlord="applicant_landlord",
                applicant_tenant="applicant_tenant",
                order_date=datetime(2024, 1, 2),
                reference_number="reference_number",
                respondent_tenant="respondent_tenant",
                respondent_landlord="respondent_landlord",
                subject="subject",
                source_pdf="a.pdf",
            )
        )
        determination_db.insert(
            Determination(
                address="15a somewhere",
                applicant_landlord="John",
                applicant_tenant="Mary",
                order_date=datetime(2024, 1, 1),
                reference_number="1111",
                respondent_tenant="Ben",
                respondent_landlord="Simon",
                subject="someting",
                source_pdf="a.pdf",
            )
        )
        self.assertEqual(len(determination_db), 2)
        self.assertEqual(len(determination_db.filter()), 2)
        self.assertEqual(len(determination_db.filter(address="s", partial=True)), 2)
        self.assertEqual(
            len(determination_db.filter(address="somewhere", partial=True)), 1
        )
        self.assertEqual(
            len(determination_db.filter(address="somewhere", partial=False)), 0
        )

        self.assertEqual(
            len(determination_db.filter(order_date=datetime(2024, 1, 1), partial=True)),
            1,
        )
