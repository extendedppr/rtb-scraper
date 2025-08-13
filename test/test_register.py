import datetime

from unittest import TestCase

from rtb_scraper.register import RegisterObject, RegisterDB


class RegisterObjectTest(TestCase):

    def test_address(self):
        rtb_obj = RegisterObject(
            address_1="a1",
            address_2="a2",
            address_3="a3",
            address_4="a4",
            address_5="a5",
            eircode="eir",
            county="dublin",
            bedrooms=2,
        )
        self.assertEqual(rtb_obj.address, "a1, a2, a3, a4, a5")


class RegisterDBTest(TestCase):

    def setUp(self):
        rtb = RegisterDB()
        rtb.drop_data()

    def test_insert(self):
        rtb = RegisterDB()
        self.assertEqual(len(rtb), 0)
        rtb.insert(
            RegisterObject(
                address_1="a1",
                address_2="a2",
                address_3="a3",
                address_4="a4",
                address_5="a5",
                eircode="D01AAAA",
                county="dublin",
                bedrooms=2,
            )
        )
        self.assertEqual(len(rtb), 1)
        rtb.insert(
            RegisterObject(
                address_1="a1",
                address_2="a2",
                address_3="a3",
                address_4="a4",
                address_5="a5",
                eircode="D01AAAA",
                county="dublin",
                bedrooms=2,
            )
        )
        self.assertEqual(len(rtb), 1)

    def test_filter(self):
        rtb = RegisterDB()
        rtb.insert(
            RegisterObject(
                address_1="a1",
                address_2="a2",
                address_3="a3",
                address_4="a4",
                address_5="a5",
                eircode="D01AAAA",
                county="dublin",
                bedrooms=2,
                month_seen=datetime.datetime(2024, 1, 1),
            )
        )
        rtb.insert(
            RegisterObject(
                address_1="a01",
                address_2="a02",
                address_3="a03",
                address_4="a04",
                address_5="a05",
                eircode="D02AAAA",
                county="dublin",
                bedrooms=3,
            )
        )

        self.assertEqual(len(rtb.filter()), 2)
        self.assertEqual(len(rtb.filter(address_1="a1")), 1)
        self.assertEqual(len(rtb.filter(address_1="a9")), 0)
        self.assertEqual(len(rtb.filter(address_1="a", partial=True)), 2)
        self.assertEqual(len(rtb.filter(bedrooms=3)), 1)
        self.assertEqual(len(rtb.filter(month_seen=datetime.datetime(2024, 1, 1))), 1)
        self.assertEqual(len(rtb.filter(address="a1 a2", partial=True)), 1)
