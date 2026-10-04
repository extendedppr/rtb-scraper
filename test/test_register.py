import datetime

from unittest import TestCase
from unittest.mock import patch

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
                month_seen=datetime.datetime(2024, 1, 1),
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
                month_seen=datetime.datetime(2024, 1, 1),
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
        self.assertEqual(len(rtb.filter(exclude_address_substrs=["a01"])), 1)

    def test_insert_many(self):
        rtb = RegisterDB()
        month = datetime.datetime(2024, 1, 1)

        def objects():
            # More than one SQL batch, followed by duplicates across batches.
            for i in list(range(205)) + [0, 100, 204]:
                yield RegisterObject(
                    address_1=f"{i} Main Street",
                    address_2="Dublin",
                    county="Dublin",
                    eircode="D01AAAA",
                    month_seen=month,
                )

        rtb.insert_many(objects())
        rtb.insert_many(objects())
        self.assertEqual(len(rtb), 205)
        result = rtb.filter(address="100 Main Street, Dublin")[0]
        self.assertEqual(result.searchable_address, "100mainstreetdublin")
        self.assertIsNone(result.bedrooms)
        self.assertIsNone(result.address_3)

        rtb.insert_many(
            [
                RegisterObject(
                    address_1="100 Main Street",
                    address_2="Dublin",
                    county="Dublin",
                    eircode="D01AAAA",
                    month_seen=datetime.datetime(2024, 2, 1),
                )
            ]
        )
        self.assertEqual(len(rtb), 206)

    def test_insert_many_empty_and_invalid_eircode(self):
        rtb = RegisterDB()
        rtb.insert_many(iter(()))
        self.assertEqual(len(rtb), 0)
        with patch("builtins.print") as output:
            rtb.insert_many(
                [
                    RegisterObject(
                        address_1="Main Street",
                        county="Dublin",
                        eircode="invalid",
                    )
                ]
            )
        output.assert_called_once_with("Bad eircode: invalid")
        self.assertEqual(len(rtb), 1)

    def test_connection_uses_model_transaction(self):
        rtb = RegisterDB()
        db = RegisterObject._meta.database
        with db.atomic() as transaction:
            rtb.insert_many([RegisterObject(address_1="Main Street", county="Dublin")])
            self.assertEqual(len(rtb), 1)
            transaction.rollback()
        self.assertEqual(len(rtb), 0)
