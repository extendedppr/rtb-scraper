from unittest import TestCase

from rtb_scraper.tribunal import Tribunal, TribunalDB


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
