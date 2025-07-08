import os
from unittest import TestCase

from rtb_scraper.tribunal import Tribunal, TribunalDB, extract_tribunal_data_from_text


class TribunalUtil(TestCase):

    def test_extract_data_from_text(self):
        # TODO: find an applicant tenant

        base_resources = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test/test_resources/",
        )

        data = [
            (
                "TR0824-007885-DR0524-95719_original_report.txt.pdf.txt",
                {
                    "address": "Apartment 190, The Hermitage, Dublin 13, D13W9RX",
                    "applicant": "Tenant",
                    "case_ref_no": "0524-95719",
                    "landlord": "Shannon Homes",
                    "tenant": "Jennifer Reilly",
                    "tribunal_ref_no": "TR0824-007885",
                },
                "TR0824-007885-DR0524-95719_original_report.pdf",
            ),
            (
                "TR0817-002570-DR0517-34518_Tribunal_Report.txt.pdf.txt",
                {
                    "address": "24 Priory Way, St. Raphael's Manor, Celbridge, Kildare, W23Y827",
                    "applicant": "landlords",
                    "case_ref_no": "0517-34518",
                    "landlord": "Lorcan Tyrrell",
                    "tenant": "Gráinne O'Grady, Julia Puchtinger",
                    "tribunal_ref_no": "TR0817-002570",
                },
                "TR0817-002570-DR0517-34518_Tribunal_Report.pdf",
            ),
        ]

        for d in data:
            content = open(os.path.join(base_resources, d[0]), "r").read()
            self.assertEqual(extract_tribunal_data_from_text(content), d[1])


class TribunalTest(TestCase):

    def test_repr(self):
        tribunal_obj = Tribunal(
            tribunal_ref_no="tribunal_ref_no",
            case_ref_no="case_ref_no",
            tenant="tenant",
            landlord="landlord",
            address="address",
            applicant="applicant",
            subject="subject",
            source_pdf="a.pdf",
        )
        self.assertEqual(
            str(tribunal_obj),
            'Tribunal(address="address", applicant="applicant", landlord="landlord", tenant="tenant", case_ref_no="case_ref_no", tribunal_ref_no="tribunal_ref_no", subject="subject", source_pdf="a.pdf")',
        )


class TribunalDBTest(TestCase):

    def setUp(self):
        tribunal_db = TribunalDB()
        tribunal_db.drop_data()

    def test_insert(self):
        tribunal_db = TribunalDB()
        self.assertEqual(len(tribunal_db), 0)
        tribunal_obj = Tribunal(
            tribunal_ref_no="tribunal_ref_no",
            case_ref_no="case_ref_no",
            tenant="tenant",
            landlord="landlord",
            address="address",
            applicant="applicant",
            subject="subject",
        )
        tribunal_db.insert(tribunal_obj)
        self.assertEqual(len(tribunal_db), 1)
        tribunal_db.insert(tribunal_obj)
        self.assertEqual(len(tribunal_db), 1)

    def test_filter(self):
        tribunal_db = TribunalDB()
        tribunal_db.insert(
            Tribunal(
                tribunal_ref_no="tribunal_ref_no",
                case_ref_no="case_ref_no",
                tenant="tenant",
                landlord="landlord",
                address="address",
                applicant="applicant",
                subject="subject",
            )
        )
        tribunal_db.insert(
            Tribunal(
                tribunal_ref_no="1111",
                case_ref_no="2222",
                tenant="Bob",
                landlord="Jane",
                address="15a somewhere",
                applicant="tenant",
                subject="some subject",
            )
        )
        self.assertEqual(len(tribunal_db.filter()), 2)
        self.assertEqual(len(tribunal_db.filter(tribunal_ref_no="1111")), 1)
        self.assertEqual(len(tribunal_db.filter(tribunal_ref_no="111")), 0)
