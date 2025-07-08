import os
import re

from bs4 import BeautifulSoup
import pikepdf
import requests
import backoff
import ocrmypdf
import fitz


def clean_string(s) -> str | None:
    """
    Generic clean a messy string up

    Often see messy strings like ": CONTENT   CONTENT,"
    """
    if s is None:
        return None
    s = s.lstrip(":")
    s = re.sub(r"\s*[,.]+\s*$", "", s)
    s = re.sub(r"\s*([,.:;!?])", r"\1", s)
    s = remove_double_spaces(s)
    return s.strip()


@backoff.on_exception(
    backoff.expo, (requests.exceptions.RequestException,), max_tries=5
)
def download_file(url, filepath) -> None:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        if e.response is not None and e.response.status_code == 404:
            print(f"404 Not Found for {url}, skipping.")
            return
        raise
    else:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException),
    max_tries=10,
    jitter=backoff.full_jitter,
)
def fetch_page(url) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def remove_brackets_and_contents(text) -> str:
    return re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}|<.*?>", "", text)


def removeprefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def _ocrmypdf(original_pdf, computed_text_pdf, raw_text_path):
    if os.path.exists(raw_text_path):
        return

    if original_pdf.suffix != ".pdf":
        print(f"Not a pdf: {original_pdf}")
        return

    if not os.path.exists(raw_text_path):

        try:
            ocrmypdf.ocr(
                original_pdf,
                computed_text_pdf,
                language="eng",
                progress_bar=False,
                deskew=True,
            )
        except (
            ocrmypdf.exceptions.PriorOcrFoundError,
            ocrmypdf.exceptions.TaggedPDFError,
        ):
            # Has text in it and didn't run ocr
            with open(raw_text_path, "w") as fh:
                fh.write(get_text_from_text_pdf(original_pdf))
        except pikepdf._core.PdfError:
            print(f"PDF ERROR: {original_pdf}")
        else:
            if os.path.exists(computed_text_pdf):
                with open(raw_text_path, "w") as fh:
                    fh.write(get_text_from_text_pdf(computed_text_pdf))


def get_text_from_text_pdf(fp) -> str:
    doc = fitz.open(fp)
    page_1 = doc[0]
    return page_1.get_text()


def is_determination_or_tribunal(fp) -> str:
    try:
        text = None
        with open(fp, "r") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        return None

    if "Report of Tribunal Reference No" in text:
        return "tribunal"
    if "Determination Order" in text:
        return "determination"


def get_post_data(year, dispute_type, main_type, page_no):

    return {
        "action": "facetwp_refresh",
        "data": {
            "facets": {
                "search": "",
                "adjudication_orders_and_tribunal_orders_date": [str(year)],
                "adjudication_and_tribunal_dispute_type": [dispute_type],
                "adjudication_orders_and_tribunal_orders_post_type": [main_type],
                "pager_numbers": [],
            },
            "frozen_facets": {},
            "http_params": {
                "get": {
                    "_adjudication_orders_and_tribunal_orders_date": str(year),
                    "_adjudication_and_tribunal_dispute_type": dispute_type,
                    "_adjudication_orders_and_tribunal_orders_post_type": main_type,
                    "_paged": str(page_no),
                },
                "uri": "disputes/dispute-outcomes-and-orders/adjudication-and-tribunal-orders",
                "url_vars": {
                    "adjudication_orders_and_tribunal_orders_date": [str(year)],
                    "adjudication_and_tribunal_dispute_type": [dispute_type],
                    "adjudication_orders_and_tribunal_orders_post_type": [main_type],
                },
            },
            "template": "adjudication_orders_and_tribunal_orders_listing",
            "extras": {"sort": "default", "pager": True},
            "soft_refresh": 1,
            "is_bfcache": 1,
            "first_load": 0,
            "paged": str(page_no),
        },
    }


def remove_double_spaces(text):
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def read_file(fp):
    text = None
    with open(fp, "r") as fh:
        text = fh.read()
    return text
