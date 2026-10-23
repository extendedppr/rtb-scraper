import os
import datetime
import json
import argparse
import time
import sys
import traceback
from pathlib import Path

import progressbar
import requests
from bs4 import BeautifulSoup

from rtb_scraper.register import register, RegisterObject
from rtb_scraper.settings import (
    DATA_LOCATION,
    LOG_LOCATION,
    RTB_TRIBUNAL_AND_DETERMINATION_DIR,
)
from rtb_scraper.constants import (
    RTB_REFRESH_URL,
    MAIN_TYPES,
    DISPUTE_TYPES,
    COUNTY_ID_MAP,
    PROPERTY_COUNTY_URL,
    POST_HEADERS,
)

from rtb_scraper.utils import (
    download_file,
    _ocrmypdf,
    is_determination_or_tribunal,
    get_post_data,
    read_file,
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


PROGRESS_PATH = Path(DATA_LOCATION) / "scrape_progress.json"


def save_progress(progress):
    temp_path = PROGRESS_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(progress))
    temp_path.replace(PROGRESS_PATH)


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


def legacy_counties():
    response = requests.get(
        "https://ctrapi.rtb.ie/api/Address/GetCountyList", timeout=60
    )
    response.raise_for_status()
    # Dublin postal districts are separate entries in this API.
    return [row["New_name"] for row in response.json()]


def process_property(county_id, source="portal"):
    if source == "legacy":
        url = "https://ctrapi.rtb.ie/api/Address/GetByCounty"
        county = COUNTY_ID_MAP.get(county_id, county_id)
        request_kwargs = {"params": {"County": county}, "timeout": 60 * 10}
    elif source == "portal":
        url = PROPERTY_COUNTY_URL.format(county_id=county_id)
        request_kwargs = {"timeout": 60 * 10}
    else:
        raise ValueError(f"Unknown property source: {source}")

    while True:
        try:
            resp = requests.get(url, **request_kwargs)
            resp.raise_for_status()
            break
        except (requests.ConnectionError, requests.Timeout) as exc:
            print(f"County request failed: {exc}. Retrying in 5 seconds...")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status != 429 and (status is None or status < 500):
                raise
            print(f"County request failed: {exc}. Retrying in 5 seconds...")
        time.sleep(5)

    data = resp.json()
    if isinstance(data, str):
        data = json.loads(data)
    if (
        not isinstance(data, list)
        or not data
        or not all(isinstance(row, dict) for row in data)
    ):
        raise ValueError("RTB returned an empty or invalid county dataset")

    if source == "legacy":
        for row in data:
            row["NoOfBedrooms"] = row["NumBedrooms"] or None

    current_month = datetime.datetime.today().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    register.insert_many(property_objects(data, current_month))

    # Be kind, be patient
    time.sleep(30)


def property_objects(data, current_month):
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
            print(f"Failed to set RegisterObject with data: {prop}")
        else:
            yield rtb_obj


def get_page_items(processed_pdfs=None, progress=None, full_refresh=False):
    if processed_pdfs is None:
        processed_pdfs = set()
    print("Cannot give ETA")

    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    for main_type in MAIN_TYPES:
        print(f"\nStart scraping: {main_type}")

        for dispute_type in DISPUTE_TYPES:
            print(f"\nDispute type: {dispute_type}")

            for year in list(range(2015, datetime.datetime.now().year + 1)):
                print(f"\nYear: {year}")

                # Always rescan the current year for new orders.
                historical = year < datetime.datetime.now().year
                progress_key = f"{main_type}|{dispute_type}|{year}"
                state = progress.get(progress_key, {}) if progress is not None else {}
                if (
                    historical
                    and state.get("complete")
                    and state.get("verified")
                    and not full_refresh
                ):
                    print(f"Checkpoint: skipping {progress_key}", flush=True)
                    continue

                start_page = 1
                if historical and not full_refresh and not state.get("complete"):
                    start_page = max(1, state.get("next_page", 1) - 1)
                    if state.get("next_page"):
                        print(
                            f"Checkpoint: resuming {progress_key} at page {start_page}",
                            flush=True,
                        )
                if historical and full_refresh and progress is not None:
                    progress[progress_key] = {"next_page": 1}
                    save_progress(progress)
                can_advance = True
                expected_total_pages = None

                # Arbitrary 500 since it breaks before it gets to it
                for page_no in range(start_page, 500):
                    data = get_post_data(year, dispute_type, main_type, page_no)
                    try:
                        response = requests.post(
                            RTB_REFRESH_URL, headers=POST_HEADERS, json=data, timeout=60
                        )
                        response.raise_for_status()
                        payload = response.json()
                        template = payload["template"]
                        pager = payload["settings"]["pager"]
                        total_pages = pager["total_pages"]
                        if (
                            pager["page"] != page_no
                            or not isinstance(total_pages, int)
                            or total_pages < 0
                        ):
                            raise ValueError(f"Invalid pagination: {pager}")
                        if expected_total_pages is None:
                            expected_total_pages = total_pages
                        elif total_pages != expected_total_pages:
                            if historical and progress is not None:
                                progress[progress_key] = {"next_page": 1}
                                save_progress(progress)
                            raise ValueError(f"Page count changed: {pager}")
                    except Exception as exc:
                        raise RuntimeError(
                            f"Listing failed: {main_type}, {dispute_type}, "
                            f"year {year}, page {page_no}: {exc}"
                        ) from exc

                    bar.update(page_no - 1)
                    soup = BeautifulSoup(template, "html.parser")

                    download_cards = soup.find_all("article")

                    if not download_cards:
                        if page_no != 1 or total_pages != 0:
                            if historical and progress is not None:
                                progress[progress_key] = {"next_page": 1}
                                save_progress(progress)
                            raise RuntimeError(
                                f"Unexpected empty listing: {progress_key}, page {page_no}"
                            )
                        # An empty first page is cheap to recheck next run.
                        break
                    if page_no > total_pages:
                        raise RuntimeError(
                            f"Invalid page count: {progress_key}, page {page_no} of {total_pages}"
                        )

                    time.sleep(1)
                    for item in download_cards:
                        yield (main_type, dispute_type, item)

                    if historical and progress is not None and can_advance:
                        can_advance = all(
                            item.find("a", href=True) is not None
                            and all(
                                link["href"].split("/")[-1].casefold()
                                in processed_pdfs
                                for link in item.find_all("a", href=True)
                            )
                            for item in download_cards
                        )
                        if can_advance:
                            progress[progress_key] = (
                                {"complete": True, "verified": True}
                                if page_no == total_pages
                                else {"next_page": page_no + 1}
                            )
                            save_progress(progress)

                    if page_no == total_pages:
                        break


def scrape(scrape_type, property_source="portal", full_refresh=False):
    if scrape_type == "property":
        if property_source == "legacy":
            print(
                "WARNING: legacy RTB data; freshness and completeness are unverified. "
                "month_seen records retrieval month, not confirmed registration currency."
            )
            counties = [(name, name) for name in legacy_counties()]
        else:
            counties = COUNTY_ID_MAP.items()
        for county_id, county in counties:
            print(f"Processing: {county}")
            process_property(county_id, source=property_source)
    elif scrape_type == "tribunal_and_determination":
        progress = json.loads(PROGRESS_PATH.read_text()) if PROGRESS_PATH.exists() else {}
        processed_pdfs = {
            filename.casefold()
            for model in (Tribunal, Determination)
            for (filename,) in model.select(model.source_pdf).tuples()
            if filename
        }
        for _, subject_of_dispute, item in get_page_items(
            processed_pdfs, progress, full_refresh
        ):
            for link in item.find_all("a"):
                url = link["href"]

                filename = url.split("/")[-1]

                if filename.casefold() in processed_pdfs:
                    continue

                print(f"Processing PDF: {filename}", flush=True)

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
                elif determination_or_tribunal == "determination":
                    process_determination(filename, raw_text_path, subject_of_dispute)
                else:
                    print(f"Not a tribunal or determination: {raw_text_path}")
                    continue

                processed_pdfs.add(filename.casefold())

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

    parser.add_argument(
        "--property-source",
        choices=["portal", "legacy"],
        default="portal",
        help="County API to use (legacy data freshness and completeness are unverified)",
    )
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Recheck completed historical dispute listings",
    )
    args = parser.parse_args()

    try:
        scrape(
            args.type,
            property_source=args.property_source,
            full_refresh=args.full_refresh,
        )
    except BaseException:
        print(file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        log_path = Path(LOG_LOCATION)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as log:
            traceback.print_exc(file=log)
        print(f"\nScrape failed; details saved to {log_path}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
