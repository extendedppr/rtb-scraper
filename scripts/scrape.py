import os
import datetime
import json
import argparse
import time
import re
from pathlib import Path

import progressbar
import requests

from rtb_scraper.register import register, RegisterObject
from rtb_scraper.settings import SAVE_DIRS
from rtb_scraper.constants import (
    COUNTY_ID_MAP,
    BASE_URLS,
    PAGINATED_URLS,
    PROPERTY_COUNTY_URL,
)

from rtb_scraper.utils import (
    fetch_page,
    download_file,
    clean_string,
    _ocrmypdf
)

from rtb_scraper.tribunal import tribunals, Tribunal
from rtb_scraper.determination import (
    Determination,
    determinations,
    extract_data_from_text,
)


def process_determination(source_pdf, raw_text_path, subject):
    text = None
    with open(raw_text_path, "r") as fh:
        text = fh.read()

    extracted_data = extract_data_from_text(text, source_pdf=source_pdf)

    determinations.insert(
        Determination(
            address=extracted_data.get("address"),
            applicant_landlord=extracted_data.get("applicant_landlord"),
            applicant_tenant=extracted_data.get("applicant_tenant"),
            order_date=extracted_data.get("order_date"),
            reference_number=extracted_data.get("reference_number"),
            respondent_tenant=extracted_data.get("respondent_tenant"),
            respondent_landlord=extracted_data.get("respondent_landlord"),
            subject=subject,
            source_pdf=source_pdf,
        )
    )


def process_property(county_id):
    url = PROPERTY_COUNTY_URL.format(county_id=county_id)

    resp = requests.get(url, timeout=60 * 10)
    data = json.loads(resp.json())

    current_month = datetime.datetime.today().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    for prop in progressbar.progressbar(data):

        # Happened at some point somehow
        if "AddressLinne2" in prop:
            prop["AddressLine2"] = prop["AddressLinne2"]

        try:
            rtb_obj = RegisterObject(
                address_1=prop["AddressLine1"],
                address_2=prop["AddressLine2"],
                address_3=prop["AddressLine3"],
                address_4=prop["AddressLine4"],
                address_5=prop["AddressLine5"],
                eircode=prop["Eircode"],
                county=prop["County"],
                bedrooms=prop["NoOfBedrooms"],
                month_seen=current_month,
            )
        except KeyError:
            print(f"Failed to set RegisterObject with data: {data}")
        else:
            register.insert(rtb_obj)

    # Be kind, be patient
    time.sleep(30)


def get_page_items(scrape_type):
    print('Cannot give ETA. Will be however many pages there are here: https://www.rtb.ie/search-results/listing?collection=adjudication_orders|tribunal_orders')

    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    for idx, page_no in enumerate(range(10_000)):

        bar.update(idx)

        # Be kind, be patient
        time.sleep(5)

        url = (
            BASE_URLS[scrape_type]
            if page_no == 0
            else PAGINATED_URLS[scrape_type].format(pn=page_no)
        )
        soup = fetch_page(url)
        download_cards = soup.find_all("p", {"class": "download-card__title"})

        if not download_cards:
            print("Finished")
            break

        for item in [p for p in download_cards if scrape_type.title() in p.string]:
            yield (item)


def process_tribunal(fp, raw_text_path, subject_of_dispute, source_pdf):
    if fp.suffix != ".pdf":
        print(f"Not a pdf: {fp}")
        return

    text = None
    with open(raw_text_path, "r") as fh:
        text = fh.read()

    regexes = [
        re.compile(
            r"Tribunal\sReference\sNo:\s(?P<tribunal_ref_no>[^\s/]+)\s/\sCase\sRef\sNo:\s(?P<case_ref_no>[^\s]+)\s*",
            re.VERBOSE,
        ),
        re.compile(r"Tenant:\s*(?P<tenant>[^\n]+)\s*", re.VERBOSE),
        re.compile(r"Landlord:\s*(?P<landlord>[^\n]+)\s*", re.VERBOSE),
        re.compile(
            r"Address\sof\sRented\sDwelling:\s*(?P<address>[^\n]+)\s*",
            re.VERBOSE,
        ),
        re.compile(r"Applicant\s(?P<applicant>\w+)", re.VERBOSE),
    ]

    data = {}

    for regex in regexes:
        if match := regex.search(text):
            match_data = {k: clean_string(v) for k, v in match.groupdict().items()}
            data.update(match_data)

    if "Applicant" in data.get("landlord", ""):
        data["landlord"] = clean_string(
            data["landlord"][: data["landlord"].find("Applicant")]
        )
    if "Receiver" in data.get("landlord", ""):
        data["landlord"] = clean_string(
            data["landlord"][: data["landlord"].find("Receiver")]
        )
    if "(Acting" in data.get("landlord", ""):
        data["landlord"] = clean_string(
            data["landlord"][: data["landlord"].find("(Acting")]
        )
    if "(acting" in data.get("landlord", ""):
        data["landlord"] = clean_string(
            data["landlord"][: data["landlord"].find("(acting")]
        )
    if "acting" in data.get("landlord", ""):
        data["landlord"] = clean_string(
            data["landlord"][: data["landlord"].find("acting")]
        )

    if "(otherwise" in data.get("tenant", ""):
        data["tenant"] = clean_string(
            data["tenant"][: data["tenant"].find("(otherwise")]
        )

    tribunals.insert(
        Tribunal(
            tribunal_ref_no=data.get("tribunal_ref_no", None),
            case_ref_no=data.get("case_ref_no", None),
            tenant=data.get("tenant", None),
            landlord=data.get("landlord", None),
            address=data.get("address", None),
            applicant=data.get("applicant", None),
            subject=subject_of_dispute,
            source_pdf=source_pdf,
        )
    )


def scrape(scrape_type):
    if scrape_type == "property":
        for county_id, county in COUNTY_ID_MAP.items():
            print(f"Processing: {county}")
            process_property(county_id)
    else:
        for item in get_page_items(scrape_type):
            subject_of_dispute = item.parent.parent.parent.find_all(
                "p", {"class": "card-list__text"}
            )[-1].text.strip()

            url = item.parent.parent.get("href")

            filename = url.split("/")[-1]

            scrapers = {
                "determination": determinations,
                "tribunal": tribunals,
            }
            scraper = scrapers[scrape_type]
            if scraper.exists(source_pdf=filename):
                continue

            original_pdf = Path(os.path.join(SAVE_DIRS[scrape_type], filename))
            computed_text_pdf = original_pdf.with_suffix(".txt.pdf")
            raw_text_path = computed_text_pdf.with_name(computed_text_pdf.name + ".txt")

            if not os.path.exists(raw_text_path):
                download_file(url, original_pdf)
                if not os.path.exists(original_pdf):
                    print(f"Does not exist: {original_pdf}")
                    continue

            _ocrmypdf(original_pdf, computed_text_pdf, raw_text_path)

            if scrape_type == 'determination':
                process_determination(filename, raw_text_path, subject_of_dispute)
            elif scrape_type == "tribunal":
                process_tribunal(
                    original_pdf, raw_text_path, subject_of_dispute, filename
                )
            else:
                print(f"Unknown scrape_type: {scrape_type}")

            for path in (original_pdf, computed_text_pdf):
                if os.path.exists(path):
                    os.remove(path)

            # Be kind, be patient
            time.sleep(5)


def main():

    parser = argparse.ArgumentParser(
        description="Scrape RTB Determination, Tribunal Orders, or property"
    )
    parser.add_argument(
        "type",
        choices=["determination", "tribunal", "property"],
        help="Type of data to scrape: 'determination', 'tribunal', or 'property'",
    )

    args = parser.parse_args()

    scrape(args.type)


if __name__ == "__main__":
    main()
