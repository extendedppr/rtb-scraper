# RTB Scraper

Scrape and interpret the RTB database, including registries, tribunal reports and determination orders.

Tribunal reports are pdfs that are parsed directly from embedded text so those are more accurate.

Determination orders are scanned pdfs so they are converted to text using OCR and then parsed, they can have issues but are fairly rare.


## Scraping data

It will take a while to download but just put it on a box and leave it be (tribunals and determinations take long, not properties as much).

The registered property data does not include properties that have been taken off the RTB. With frequent scraping you can track but you can't go back in time.

```bash
poetry run scrape property  # choices are: property / tribunal / determination
```


### Why the register should be scraped frequently

By scraping the register frequently the db will be able to tell you in what month a property was on the register. The RTB doesn't give historical data so the intention here is to keep an up to date version and also historical data in a way you can query when a property was introduced to the register.


## Installation

```bash
poetry install
```


## Usage

All searches, partial or not, are case insensitive. Make sure you have scraped data before using.

```python

from rtb_scraper.register import register
from rtb_scraper.tribunal import tribunals
from rtb_scraper.determination import determinations

# partial=True means that any non None value given is treated as a fuzzy match rather than a non exact match

tribunal_results = tribunals.filter(
    address="12",
    landlord="john",
    tribunal_ref_no=None,
    case_ref_no=None,
    tenant=None,
    applicant=None,
    subject=None,
    partial=True
)
print(tribunal_results)
# [Tribunal(address="26 Acorn Downs, Newbridge, Kildare, W12DR13", applicant="Tenant", landlord="John Dunne", tenant="Aisling O'Sullivan", case_ref_no="0624-96940", tribunal_ref_no="TR0824-007944", subject="Deposit retention", source_pdf="TR0824-007944_-_DR0624-96940_Tribunal_Report.pdf"), Tribunal(address="102 Evergreen Road, Cork, T12F3CY", applicant="None", landlord="John Buckley", tenant="Rebecca Kenny", case_ref_no="1223-91570", tribunal_ref_no="TR0224-007219", subject="Rent arrears and overholding", source_pdf="TR0224-007219_Tribunal_Report.pdf"), ... ]

determination_results = determinations.filter(
    address="12",
    applicant_landlord="john",
    applicant_tenant=None,
    order_date=None,
    reference_number=None,
    respondent_tenant=None,
    respondent_landlord=None,
    subject=None,
    partial=True
)
print(determination_results)
# [Determination(address="79 Royston,  Kimmage Rd West, Dublin 12, D12K602", applicant_landlord="John Joseph Walsh, Jacqueline Hamilton Walsh", applicant_tenant="None", order_date="2024-03-13 00:00:00", reference_number="DR0823-87891", respondent_tenant="Michelle Walsh", respondent_landlord="None", subject="Validity of notice of termination", source_pdf="D.O_._0823-87891_.pdf"), Determination(address="12A The Birches, Kilnacourt Woods, Portarlington, Co. Laois", applicant_landlord="John McGeachy", applicant_tenant="None", order_date="2024-02-28 00:00:00", reference_number="DR0823-88415", respondent_tenant="None", respondent_landlord="None", subject="Rent arrears", source_pdf="D.O_._0823-88415_.pdf"), ... ]

register_results = register.filter(
    address="123",
    eircode=None,
    county="louth",
    bedrooms=None,
    partial=True
)
print(register_results)
# [RegisterObject(address_1="123 Castleross", address_2="Castletown Road", address_3="Dundalk", address_4="", address_5="", eircode="A91W4A8", county="Louth", bedrooms="3", month_seen="2025-04-01 00:00:00"), RegisterObject(address_1="123 Clonmore", address_2="Hale Street", address_3="Ardee", address_4="", address_5="", eircode="A92CX66", county="Louth", bedrooms="3", month_seen="2025-04-01 00:00:00"), ... ]
```


## Test

```bash
poetry install --verbose --with test
poetry run pytest
```
