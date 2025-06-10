import re
import datetime
from typing import Iterable, List, Dict, Optional

from peewee import Model, CharField, SqliteDatabase, DateTimeField

from rtb_scraper.constants import (
    PDF_ADDRESS_MAP,
    BAD_ADDRESS_PREFIXES,
    REPLACE_TEXT_IN_DETERMINATION,
)
from rtb_scraper.settings import DB_LOCATION
from rtb_scraper.utils import clean_string, remove_brackets_and_contents, removeprefix


def extract_data_from_text(
    text: str, source_pdf: Optional[str] = None
) -> Dict[str, str]:

    for to_replace, replacement in REPLACE_TEXT_IN_DETERMINATION:
        text = text.replace(to_replace, replacement)

    start_address_match = r"(?i)(?:(?:the|rented|disputed) (?:dwelling|property)(?: at| located(?: at)?)?|tenancy (?:at|of the dwelling at|of)|property at|located)"

    end_address_match = r"(?=(\.?[,;\s]? (is (invalid|invaild|valid|upheld|not upheld|deemed))|[\,;\s] This Order|\, shall| 2\. | 2\) |, there is| to be paid| on or|, as amended| within |\, at the date| is not| is valid| is abandoned| are invalid|\, up to|\, are not up| was unlawful| the security deposit|\, is dismissed|\, insofar| is withdrawn| is partially upheld| This Order| was made by|\, by way of| to the| has been| is €|\, are valid| was not| and breach|\, plus damages|\, are both| together with the sum| leaving|\, on | was €|\, is in the sum| shall vacate|\, is unenforceable| gave the| its abandon| between the| until such| was an| pursuant to| and €| up to| terminated on| and the payment| is, with| contrary to| are upheld| is therefore| on the grounds| are valid| was invalid| was valid| in breach| having off| is considered|is valid|The enforcement|also known as|\: 1\)|and cannot be|having allowed|due to|having deducted|as and from|by way of|is still ongoing|This\/Order|by the|The Notice|followed by| is in invalid|together with|are not upheld|and specif|in circum|are deemed|and shall pay|and consequently|are abandoned|plus the|carried out|are formally|and for the|is valid|and shall|will end on|having properly|the sum of|with 30 days|and dated|is vaiid|is res|for each| This |in addition| regarding |being rent|remains| cannot |at the date|for the |is invatid|as served|for failing|Also Known|and terminate|by text| remains |provides for|has not been| valid|against the|as served|and with|is abandonded|and for|less the|The Applicant|is lawfully|and a further|because this matter|is statute barred|\: 1|treland|\; \*|3\.The Respondent|The Respondent|isn ot upheld))"

    # treland is likely Ireland, doesn't matter if we stop at it

    patterns = {
        "reference_number": r"Ref: (\w+\-\w+)",
        "respondent_tenant": r"] and (.*)\s\[Respondent Tenants?\]",
        "respondent_landlord": r"]\sand\s(.*)\s\[Respondent Landlords?\]",
        "applicant_landlord": r"matter of\s(.*)\s\[Applicant Landlords?\]",
        "applicant_tenant": r"matte of\s(.*)\s\[Applicant Tenants?\]",
        "order_date": r"This Order was made by the Residential(?:\!)? Tenancies Board on (\d+ \w+ \d+)",
        "address": start_address_match + r"\s*([\s\S]*?)\s*" + end_address_match,
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        if match := re.search(pattern, text):
            if key == "address":

                if address := PDF_ADDRESS_MAP.get(source_pdf):
                    extracted_data[key] = clean_string(
                        remove_brackets_and_contents(address)
                    )
                else:

                    # Split into start and end and if it matches start then remove the starting things
                    if smaller_match := re.search(
                        start_address_match + "(.*)", match.group(1)
                    ):
                        match = smaller_match

                    try:
                        extracted_data[key] = clean_string(
                            remove_brackets_and_contents(match.group(1))
                        )
                    except Exception:
                        extracted_data[key] = None

            else:
                try:
                    extracted_data[key] = clean_string(
                        remove_brackets_and_contents(match.group(1))
                    )
                except Exception:
                    extracted_data[key] = None

    if extracted_data.get("order_date"):
        try:
            extracted_data["order_date"] = datetime.datetime.strptime(
                extracted_data["order_date"], "%d %B %Y"
            )
        except:
            print(f'Bad date: "{extracted_data["order_date"]}"')
            extracted_data["order_date"] = None

    if extracted_data.get("address"):
        extracted_data["address"] = extracted_data["address"]

    # Additional cleaning
    if "address" in extracted_data and extracted_data["address"]:
        address_str = extracted_data["address"]
        for prefix in BAD_ADDRESS_PREFIXES:
            if hasattr(address_str, "removeprefix"):
                address_str = address_str.removeprefix(prefix)
            else:
                address_str = removeprefix(address_str, prefix)
        extracted_data["address"] = address_str

    return extracted_data


class Determination(Model):
    address = CharField(null=True)
    applicant_landlord = CharField(null=True)
    applicant_tenant = CharField(null=True)
    order_date = DateTimeField(null=True)
    reference_number = CharField(null=True)
    respondent_tenant = CharField(null=True)
    respondent_landlord = CharField(null=True)
    subject = CharField()
    source_pdf = CharField()

    class Meta:
        database = SqliteDatabase(DB_LOCATION)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'Determination(address="{self.address}", applicant_landlord="{self.applicant_landlord}", applicant_tenant="{self.applicant_tenant}", order_date="{self.order_date}", reference_number="{self.reference_number}", respondent_tenant="{self.respondent_tenant}", respondent_landlord="{self.respondent_landlord}", subject="{self.subject}", source_pdf="{self.source_pdf}")'


class DeterminationDB:

    def __init__(self) -> None:
        self.create_connection()

    def __len__(self) -> int:
        return Determination.select().count()

    def __iter__(self) -> Iterable[Determination]:
        for chunk in Determination.select().chunk(100):
            for determination in chunk:
                yield determination

    def drop_data(self) -> None:
        Determination.delete().execute()

    def create_connection(self) -> None:
        db = SqliteDatabase(DB_LOCATION)
        db.connect()
        db.create_tables([Determination])

    def filter(
        self,
        address=None,
        applicant_landlord=None,
        applicant_tenant=None,
        order_date=None,
        reference_number=None,
        respondent_tenant=None,
        respondent_landlord=None,
        subject=None,
        source_pdf=None,
        partial=False,
    ) -> List[Determination]:

        filters = {
            "address": address.upper() if address else None,
            "applicant_landlord": (
                applicant_landlord.upper() if applicant_landlord else None
            ),
            "applicant_tenant": applicant_tenant.upper() if applicant_tenant else None,
            "order_date": order_date,
            "reference_number": reference_number.upper() if reference_number else None,
            "respondent_tenant": (
                respondent_tenant.upper() if respondent_tenant else None
            ),
            "respondent_landlord": (
                respondent_landlord.upper() if respondent_landlord else None
            ),
            "subject": subject.upper() if subject else None,
            "source_pdf": source_pdf.upper() if source_pdf else None,
        }

        query = Determination.select()
        for field, value in filters.items():
            if value is not None:
                field_name = getattr(Determination, field)
                if partial:
                    query = query.where(field_name.ilike(f"%{value}%"))
                else:
                    query = query.where(field_name.ilike(value))

        return [determination for determination in query]

    def exists(
        self,
        address=None,
        applicant_landlord=None,
        applicant_tenant=None,
        order_date=None,
        reference_number=None,
        respondent_tenant=None,
        respondent_landlord=None,
        subject=None,
        source_pdf=None,
    ) -> bool:
        return (
            self.filter(
                address=address,
                applicant_landlord=applicant_landlord,
                applicant_tenant=applicant_tenant,
                order_date=order_date,
                reference_number=reference_number,
                respondent_tenant=respondent_tenant,
                respondent_landlord=respondent_landlord,
                subject=subject,
                source_pdf=source_pdf,
            )
            != []
        )

    def insert(self, determination_obj: Determination) -> None:
        if self.exists(
            address=determination_obj.address,
            applicant_landlord=determination_obj.applicant_landlord,
            applicant_tenant=determination_obj.applicant_tenant,
            order_date=determination_obj.order_date,
            reference_number=determination_obj.reference_number,
            respondent_tenant=determination_obj.respondent_tenant,
            respondent_landlord=determination_obj.respondent_landlord,
            subject=determination_obj.subject,
            source_pdf=determination_obj.source_pdf,
        ):
            return

        determination_obj.save()


determinations = DeterminationDB()
