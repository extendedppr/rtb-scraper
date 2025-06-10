import sys
import os


TEST_ENV = False
if "pytest" in sys.modules:
    TEST_ENV = True

LOG_LOCATION = (
    "/var/log/rtb_scraper/rtb_scraper.log"
    if not TEST_ENV
    else "/tmp/log/rtb_scraper/rtb_scraper.log"
)
DATA_LOCATION = (
    os.getenv("DATA_LOCATION", "/var/lib/rtb")
    if not TEST_ENV
    else "/tmp/var/lib/rtb_scraper/"
)


RTB_DETERMINATION_ORDERS_DIR = os.path.join(DATA_LOCATION, "rtb_determinations")
RTB_TRIBUNALS_DIR = os.path.join(DATA_LOCATION, "rtb_tribunals")
RTB_PROPERTY_DIR = os.path.join(DATA_LOCATION, "rtb_property")

DB_LOCATION = os.path.join(DATA_LOCATION, "db.sqlite3")

os.makedirs(DATA_LOCATION, exist_ok=True)
os.makedirs(RTB_DETERMINATION_ORDERS_DIR, exist_ok=True)
os.makedirs(RTB_TRIBUNALS_DIR, exist_ok=True)
os.makedirs(RTB_PROPERTY_DIR, exist_ok=True)

SAVE_DIRS = {
    "determination": RTB_DETERMINATION_ORDERS_DIR,
    "tribunal": RTB_TRIBUNALS_DIR,
    "property": RTB_PROPERTY_DIR,
}
