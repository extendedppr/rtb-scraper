import shelve
import os
import re
import io

from bs4 import BeautifulSoup
import requests
import orjson
import backoff
import ocrmypdf
import fitz


def clean_string(s) -> str:
    return s.strip().rstrip(",").replace(" ,", ",").rstrip(".").strip() if s else s


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
            return None
        else:
            raise
    else:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


def save_subject(fn, subjects, save_dir) -> None:
    with shelve.open(os.path.join(save_dir, "subjects")) as db:
        db[fn] = subjects


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


def is_bad_json_file(fp) -> bool:
    try:
        print(fp)
        with open(fp, "w") as fh:
            orjson.loads(fh.read())
    except (orjson.JSONDecodeError, UnicodeDecodeError, io.UnsupportedOperation):
        return False
    else:
        return True


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
        else:
            if os.path.exists(computed_text_pdf):
                with open(raw_text_path, "w") as fh:
                    fh.write(get_text_from_text_pdf(computed_text_pdf))


def get_text_from_text_pdf(fp):
    doc = fitz.open(fp)
    page_1 = doc[0]
    return page_1.get_text()
