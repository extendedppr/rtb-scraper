import os
import datetime
import json
import argparse
import time
from pathlib import Path

import progressbar
import requests
from bs4 import BeautifulSoup

from rtb_scraper.register import register, RegisterObject
from rtb_scraper.settings import RTB_TRIBUNAL_AND_DETERMINATION_DIR
from rtb_scraper.constants import (
    RTB_REFRESH_URL,
    MAIN_TYPES,
    DISPUTE_TYPES,
    COUNTY_ID_MAP,
    PROPERTY_COUNTY_URL,
    POST_HEADERS
)

from rtb_scraper.utils import (
    download_file,
    _ocrmypdf,
    is_determination_or_tribunal,
    get_post_data,
    read_file
)

from rtb_scraper.tribunal import (
    tribunals,
    extract_tribunal_data_from_text,
    Tribunal,
)
from rtb_scraper.determination import (
    Determination,
    determinations,
    extract_determination_data_from_text,
)


def process_tribunal(fp, raw_text_path, subject_of_dispute, source_pdf):
    if fp.suffix != ".pdf":
        print(f"Not a pdf: {fp}")
        return

    if not os.path.exists(raw_text_path):
        print(f"No text file: {raw_text_path}")
        return

    text = read_file(raw_text_path)

    data = extract_tribunal_data_from_text(text)

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


def process_determination(source_pdf, raw_text_path, subject):

    text = read_file(raw_text_path)

    extracted_data = extract_determination_data_from_text(text, source_pdf=source_pdf)

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


def get_page_items():
    print("Cannot give ETA. Just wait a day or two")

    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    for main_type in MAIN_TYPES:
        print(f'\nStart scraping: {main_type}')

        for dispute_type in DISPUTE_TYPES:
            print(f'\nDispute type: {dispute_type}')

            for year in list(range(2015, datetime.datetime.now().year + 1)):
                print(f'\nYear: {year}')

                # Arbitrary 500 since it breaks before it gets to it
                for idx, page_no in enumerate(range(1, 500)):

                    bar.update(idx)

                    data = get_post_data(year, dispute_type, main_type, page_no)

                    response = requests.post(RTB_REFRESH_URL, headers=POST_HEADERS, json=data)

                    data = response.json()
                    soup = BeautifulSoup(data["template"], "html.parser")

                    download_cards = soup.find_all("article")

                    if not download_cards:
                        # Finished
                        break

                    # Be kind, be patient
                    time.sleep(5)

                    for item in download_cards:
                        yield (main_type, dispute_type, item)


def scrape(scrape_type):
    if scrape_type == "property":
        for county_id, county in COUNTY_ID_MAP.items():
            print(f"Processing: {county}")
            process_property(county_id)
    elif scrape_type == 'tribunal_and_determination':
        for _, subject_of_dispute, item in get_page_items():

            for link in item.find_all("a"):

                url = link["href"]

                filename = url.split("/")[-1]

                if tribunals.exists(source_pdf=filename) or determinations.exists(
                    source_pdf=filename
                ):
                    continue

                original_pdf = Path(
                    os.path.join(RTB_TRIBUNAL_AND_DETERMINATION_DIR, filename)
                )
                computed_text_pdf = original_pdf.with_suffix(".txt.pdf")
                raw_text_path = computed_text_pdf.with_name(
                    computed_text_pdf.name + ".txt"
                )

                if not os.path.exists(raw_text_path):
                    download_file(url, original_pdf)
                    if not os.path.exists(original_pdf):
                        print(f"Does not exist: {original_pdf}")
                        continue

                _ocrmypdf(original_pdf, computed_text_pdf, raw_text_path)

                if not os.path.exists(raw_text_path):
                    print(f"Text path does not exist: {raw_text_path}")
                    continue

                determination_or_tribunal = is_determination_or_tribunal(raw_text_path)
                if determination_or_tribunal == "tribunal":
                    process_tribunal(
                        original_pdf, raw_text_path, subject_of_dispute, filename
                    )
                elif determination_or_tribunal == 'determination':
                    process_determination(
                        filename, raw_text_path, subject_of_dispute
                    )
                else:
                    print(f'Not a tribunal or determination: {raw_text_path}')
                    continue

                for path in (original_pdf, computed_text_pdf):
                    if os.path.exists(path):
                        os.remove(path)


def main():

    parser = argparse.ArgumentParser(
        description="Scrape RTB determinations, tribunal orders, or property registrations"
    )
    parser.add_argument(
        "type",
        choices=["tribunal_and_determination", "property"],
        help="Type of data to scrape: 'tribunal_and_determination', or 'property'",
    )

    args = parser.parse_args()

    scrape(args.type)


if __name__ == "__main__":
    main()
