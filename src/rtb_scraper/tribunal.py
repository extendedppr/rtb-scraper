import copy
from typing import Iterable, List

from peewee import Model, CharField, SqliteDatabase

from rtb_scraper.settings import DB_LOCATION
from rtb_scraper.utils import clean_string, remove_double_spaces
from rtb_scraper.constants import GENERAL_REPLACE_TEXT, TRIBUNAL_REGEXES


def extract_tribunal_data_from_text(text):
    clean_text = copy.copy(text)
    for to_replace, replacement in GENERAL_REPLACE_TEXT:
        clean_text = clean_text.replace(to_replace, replacement)
    clean_text = remove_double_spaces(clean_text)

    data = {}
    for regex in TRIBUNAL_REGEXES:
        if match := regex.search(clean_text):
            match_data = {k: clean_string(v) for k, v in match.groupdict().items()}
            data.update(match_data)

    # Names often are like "First Last ("
    # Names often are like "First O' Last"

    def clean_field(data, field, keywords):
        for keyword in keywords:
            value = data.get(field, "")
            if keyword in value:
                data[field] = clean_string(value[: value.find(keyword)])
                break

    clean_field(
        data, "landlord", ["Applicant", "Receiver", "(Acting", "(acting", "acting"]
    )
    clean_field(data, "tenant", ["(otherwise"])

    return data


class Tribunal(Model):

    tribunal_ref_no = CharField(null=True)
    case_ref_no = CharField(null=True)
    tenant = CharField(null=True)
    landlord = CharField(null=True)
    address = CharField(null=True)
    applicant = CharField(null=True)
    subject = CharField(null=True)
    source_pdf = CharField(null=True)

    class Meta:
        database = SqliteDatabase(DB_LOCATION)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'Tribunal(address="{self.address}", applicant="{self.applicant}", landlord="{self.landlord}", tenant="{self.tenant}", case_ref_no="{self.case_ref_no}", tribunal_ref_no="{self.tribunal_ref_no}", subject="{self.subject}", source_pdf="{self.source_pdf}")'

    @property
    def landlords(self) -> List[str]:
        return (
            [i.strip() for i in str(self.landlord).split(",")] if self.landlord else []
        )

    @property
    def tenants(self) -> List[str]:
        return [i.strip() for i in str(self.tenant).split(",")] if self.tenant else []


class TribunalDB:

    def __init__(self) -> None:
        self.create_connection()

    def __len__(self) -> int:
        return Tribunal.select().count()

    def __iter__(self) -> Iterable[Tribunal]:
        return Tribunal.select().iterator(chunk_size=100)

    def drop_data(self) -> None:
        Tribunal.delete().execute()

    def create_connection(self) -> None:
        db = SqliteDatabase(DB_LOCATION)
        db.connect()
        db.create_tables([Tribunal])

    def filter(
        self,
        tribunal_ref_no=None,
        case_ref_no=None,
        tenant=None,
        landlord=None,
        address=None,
        applicant=None,
        subject=None,
        source_pdf=None,
        partial=False,
    ) -> list:

        filters = {
            "tribunal_ref_no": tribunal_ref_no.upper() if tribunal_ref_no else None,
            "case_ref_no": case_ref_no.upper() if case_ref_no else None,
            "tenant": tenant.upper() if tenant else None,
            "landlord": landlord.upper() if landlord else None,
            "address": address.upper() if address else None,
            "applicant": applicant.upper() if applicant else None,
            "subject": subject.upper() if subject else None,
            "source_pdf": source_pdf.upper() if source_pdf else None,
        }

        query = Tribunal.select()

        for field, value in filters.items():
            if value is not None:
                field_name = getattr(Tribunal, field)
                if partial:
                    query = query.where(field_name.ilike(f"%{value}%"))
                else:
                    query = query.where(field_name.ilike(value))

        return [tribunal for tribunal in query]

    def exists(
        self,
        tribunal_ref_no=None,
        case_ref_no=None,
        tenant=None,
        landlord=None,
        address=None,
        applicant=None,
        subject=None,
        source_pdf=None,
    ) -> bool:
        return (
            self.filter(
                tribunal_ref_no=tribunal_ref_no,
                case_ref_no=case_ref_no,
                tenant=tenant,
                landlord=landlord,
                address=address,
                applicant=applicant,
                subject=subject,
                source_pdf=source_pdf,
            )
            != []
        )

    def insert(self, tribunal_obj: Tribunal) -> None:
        if self.exists(
            tribunal_ref_no=tribunal_obj.tribunal_ref_no,
            case_ref_no=tribunal_obj.case_ref_no,
            tenant=clean_string(tribunal_obj.tenant),
            landlord=clean_string(tribunal_obj.landlord),
            address=clean_string(tribunal_obj.address),
            applicant=clean_string(tribunal_obj.applicant),
            subject=tribunal_obj.subject,
            source_pdf=tribunal_obj.source_pdf,
        ):
            return

        tribunal_obj.save()


tribunals = TribunalDB()
