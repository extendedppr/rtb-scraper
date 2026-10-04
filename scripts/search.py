import argparse
from itertools import groupby

from peewee import fn
from tabulate import tabulate

from rtb_scraper.register import RegisterObject
from rtb_scraper.determination import Determination
from rtb_scraper.tribunal import Tribunal


def address_substr_csv(value):
    return [part.replace(" ", "").lower() for part in value.split(",") if part.strip()]


def search(
    kind="property",
    address_substrs=(),
    exclude_address_substrs=(),
    tenant=None,
    landlord=None,
):
    if kind == "property" and (tenant is not None or landlord is not None):
        raise ValueError("Tenant and landlord names are only available for disputes")
    if kind == "property":
        models = [RegisterObject]
    else:
        models = {
            "determination": [Determination],
            "tribunal": [Tribunal],
            "tribunal_and_determination": [Tribunal, Determination],
        }[kind]

    for model in models:
        field = model.searchable_address if kind == "property" else model.address
        address = fn.REPLACE(fn.LOWER(fn.COALESCE(field, "")), " ", "")
        query = model.select()
        for value in address_substrs:
            query = query.where(fn.INSTR(address, value) > 0)
        for value in exclude_address_substrs:
            query = query.where(fn.INSTR(address, value) == 0)
        for role, name in (("tenant", tenant), ("landlord", landlord)):
            if name is None:
                continue
            if model is Tribunal:
                condition = fn.INSTR(fn.LOWER(getattr(model, role)), name.lower()) > 0
            else:
                applicant = getattr(model, "applicant_" + role)
                respondent = getattr(model, "respondent_" + role)
                condition = (fn.INSTR(fn.LOWER(applicant), name.lower()) > 0) | (
                    fn.INSTR(fn.LOWER(respondent), name.lower()) > 0
                )
            query = query.where(condition)
        yield from query.order_by(field, model.id).iterator()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind",
        nargs="?",
        default="property",
        choices=("property", "determination", "tribunal", "tribunal_and_determination"),
        help="Dataset to search (default: property)",
    )
    parser.add_argument(
        "--address-substr-csv",
        type=address_substr_csv,
        default=[],
        help="Comma-separated address parts that must all match",
    )
    parser.add_argument(
        "--exclude-address-substr-csv",
        type=address_substr_csv,
        default=[],
        help="Comma-separated address parts to exclude",
    )
    parser.add_argument(
        "--tenant", help="Tenant name substring (disputes only, case-insensitive)"
    )
    parser.add_argument(
        "--landlord", help="Landlord name substring (disputes only, case-insensitive)"
    )
    args = parser.parse_args(argv)
    if args.kind == "property" and (
        args.tenant is not None or args.landlord is not None
    ):
        parser.error("--tenant and --landlord require a dispute dataset")
    found = False
    records = search(
        args.kind,
        args.address_substr_csv,
        args.exclude_address_substr_csv,
        tenant=args.tenant,
        landlord=args.landlord,
    )
    for model, matches in groupby(records, key=type):
        fields = [
            field.name
            for field in model._meta.sorted_fields
            if field.name not in ("id", "searchable_address")
        ]
        rows = [[getattr(record, field) for field in fields] for record in matches]
        print(model.__name__)
        print(tabulate(rows, headers=fields, disable_numparse=True))
        found = True
    if not found:
        print("No matching records.")


if __name__ == "__main__":
    main()
