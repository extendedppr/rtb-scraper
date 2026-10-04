# RTB Scraper

Scrape and interpret the RTB database, including registries, tribunal reports and determination orders.

Tribunal reports are pdfs that are parsed directly from embedded text so those are more accurate.

Determination orders are scanned pdfs so they are converted to text using OCR and then parsed, they can have issues but are fairly rare.


## Scraping data

It will take a while to download but just put it on a box and leave it be (tribunals and determinations take long, not properties as much).

The registered property data does not include properties that have been taken off the RTB. With frequent scraping you can track but you can't go back in time.

```bash
poetry run scrape property  # choices are: property / tribunal_and_determination
```


### Why the register should be scraped frequently

By scraping the register frequently the db will be able to tell you in what month a property was on the register. The RTB doesn't give historical data so the intention here is to keep an up to date version and also historical data in a way you can query when a property was introduced to the register.


## Installation

```bash
poetry install
```


## Usage

```bash
poetry run search property --address-substr-csv "13,grand canal"
poetry run search determination --address-substr-csv "grand canal,dublin"
poetry run search tribunal_and_determination --address-substr-csv "dublin" --exclude-address-substr-csv "apartment"
poetry run search tribunal_and_determination --landlord "smith" --tenant "alex"
```

## Test

```bash
poetry install --verbose --with test
poetry run pytest
```
