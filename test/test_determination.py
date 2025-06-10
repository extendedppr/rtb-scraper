from datetime import datetime

from unittest import TestCase

from rtb_scraper.determination import (
    Determination,
    DeterminationDB,
    extract_data_from_text,
)


class DeterminationTest(TestCase):

    def test_extract_data_from_text_order_date(self):
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
                extract_data_from_text(text).get("order_date"), expected_address
            )

    def test_extract_data_from_text_address(self):

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
                extract_data_from_text(text).get("address"), expected_address
            )

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
