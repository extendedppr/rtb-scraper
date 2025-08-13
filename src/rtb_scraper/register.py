from typing import Iterable, List, Optional, Union

from peewee import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    SqliteDatabase,
    fn,
    SQL,
)

from rtb_scraper.settings import DB_LOCATION
from rtb_scraper.constants import EIRCODE_PATTERN


class RegisterObject(Model):
    address_1 = CharField()
    address_2 = CharField(null=True)
    address_3 = CharField(null=True)
    address_4 = CharField(null=True)
    address_5 = CharField(null=True)
    eircode = CharField(null=True)
    county = CharField()
    bedrooms = IntegerField(null=True)
    month_seen = DateTimeField(null=True, default=None)
    searchable_address = CharField()

    class Meta:
        database = SqliteDatabase(DB_LOCATION)

    def save(self, *args, **kwargs):
        self.searchable_address = self.compute_searchable_address()
        print(f"Searchable: {self.searchable_address}")
        return super(RegisterObject, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'RegisterObject(address_1="{self.address_1}", address_2="{self.address_2}", address_3="{self.address_3}", address_4="{self.address_4}", address_5="{self.address_5}", eircode="{self.eircode}", county="{self.county}", bedrooms="{self.bedrooms}", month_seen="{self.month_seen}", searchable_address="{self.compute_searchable_address()}")'

    def compute_searchable_address(self) -> str:
        print(self.address)
        return self.address.replace(" ", "").replace(",", "").lower()

    @property
    def address(self) -> str:
        address_list = [
            self.address_1,
            self.address_2,
            self.address_3,
            self.address_4,
            self.address_5,
        ]
        return ", ".join(filter(None, address_list))


class RegisterDB:
    def __init__(self) -> None:
        self.create_connection()

    def __len__(self) -> int:
        return RegisterObject.select().count()

    def __iter__(self) -> Iterable[RegisterObject]:
        return RegisterObject.select().iterator(chunk_size=100)

    def drop_data(self) -> None:
        RegisterObject.delete().execute()

    def create_connection(self) -> None:
        db = SqliteDatabase(DB_LOCATION)
        db.connect()
        db.create_tables([RegisterObject])

    def exists(
        self,
        eircode: Optional[Union[str, CharField]] = None,
        address_1: Optional[Union[str, CharField]] = None,
        address_2: Optional[Union[str, CharField]] = None,
        address_3: Optional[Union[str, CharField]] = None,
        address_4: Optional[Union[str, CharField]] = None,
        address_5: Optional[Union[str, CharField]] = None,
        month_seen: Optional[Union[str, CharField]] = None,
    ) -> bool:
        if eircode and month_seen:
            return (
                RegisterObject.select()
                .where(
                    RegisterObject.eircode == eircode,
                    RegisterObject.month_seen == month_seen,
                )
                .exists()
            )

        return (
            self.filter(
                eircode=eircode,
                address_1=address_1,
                address_2=address_2,
                address_3=address_3,
                address_4=address_4,
                address_5=address_5,
                month_seen=month_seen,
            )
            != []
        )

    def insert(self, rtb_obj: RegisterObject) -> None:
        if self.exists(
            address_1=rtb_obj.address_1,
            address_2=rtb_obj.address_2,
            address_3=rtb_obj.address_3,
            address_4=rtb_obj.address_4,
            address_5=rtb_obj.address_5,
            month_seen=rtb_obj.month_seen,
            eircode=rtb_obj.eircode,
        ):
            return

        if rtb_obj.eircode:
            if not EIRCODE_PATTERN.match(str(rtb_obj.eircode)):
                print(f"Bad eircode: {rtb_obj.eircode}")

        rtb_obj.save()

    def filter(
        self,
        address: Optional[str] = None,
        address_1: Optional[Union[str, CharField]] = None,
        address_2: Optional[Union[str, CharField]] = None,
        address_3: Optional[Union[str, CharField]] = None,
        address_4: Optional[Union[str, CharField]] = None,
        address_5: Optional[Union[str, CharField]] = None,
        month_seen: Optional[Union[str, DateTimeField]] = None,
        eircode: Optional[Union[str, CharField]] = None,
        county: Optional[str] = None,
        bedrooms: Optional[int] = None,
        partial: bool = False,
        collapse: bool = True,
    ) -> List[RegisterObject]:
        filters = {
            "eircode": eircode if eircode else None,
            "county": county if county else None,
            "bedrooms": bedrooms,
            "address_1": address_1 if address_1 else None,
            "address_2": address_2 if address_2 else None,
            "address_3": address_3 if address_3 else None,
            "address_4": address_4 if address_4 else None,
            "address_5": address_5 if address_5 else None,
            "month_seen": month_seen if month_seen else None,
        }

        query = RegisterObject.select()

        for field, value in filters.items():
            if value is not None:
                field_name = getattr(RegisterObject, field)
                if partial:
                    query = query.where(field_name.ilike(f"%{value}%"))
                else:
                    query = query.where(field_name.ilike(value))

        if address:
            address = address.replace(" ", "").replace(",", "").lower()
            query = query.where(RegisterObject.searchable_address.ilike(f"%{address}%"))

        objs = [obj for obj in query]

        if collapse:
            seen_addresses = set()

            rtb_objs = []
            for item in objs:
                if collapse and item.address in seen_addresses:
                    continue
                seen_addresses.add(item.address)
                rtb_objs.append(item)

            return rtb_objs

        return objs


register = RegisterDB()
