import sys
import os
from pathlib import Path


TEST_ENV = False
if "pytest" in sys.modules:
    TEST_ENV = True

LOG_LOCATION = (
    str(
        Path(os.getenv("XDG_STATE_HOME") or Path.home() / ".local" / "state")
        / "rtb-scraper"
        / "rtb_scraper.log"
    )
    if not TEST_ENV
    else "/tmp/log/rtb_scraper/rtb_scraper.log"
)
DATA_LOCATION = (
    (
        os.getenv("RTB_DATA_LOCATION")
        or str(
            Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share")
            / "rtb-scraper"
        )
    )
    if not TEST_ENV
    else "/tmp/var/lib/rtb_scraper/"
)


RTB_TRIBUNAL_AND_DETERMINATION_DIR = os.path.join(
    DATA_LOCATION, "rtb_tribunals_and_determinations"
)
RTB_PROPERTY_DIR = os.path.join(DATA_LOCATION, "rtb_property")

DB_LOCATION = os.path.join(DATA_LOCATION, "db.sqlite3")


os.makedirs(DATA_LOCATION, exist_ok=True)
os.makedirs(RTB_TRIBUNAL_AND_DETERMINATION_DIR, exist_ok=True)
os.makedirs(RTB_PROPERTY_DIR, exist_ok=True)
