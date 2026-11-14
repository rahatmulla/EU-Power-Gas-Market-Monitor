"""
The timestamps in dataset represent the electricity delivery hours, not necessarily the times when ENTSO-E published those forecasts.

For example, a wind forecast for tomorrow at 15:00 might have been published today at 08:00 or updated later.

If we use a forecast that was updated after our prediction cutoff, our model could accidentally learn from information that wasn't available at prediction time.
Step 6.7 — Inspect ENTSO-E forecast metadata
Let's check whether the underlying ENTSO-E API response contains publication or revision information.
"""


"""Inspect raw ENTSO-E forecast response metadata."""

from pathlib import Path
import os
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

api_key = os.environ["ENTSOE_API_KEY"]

# Germany-Luxembourg bidding zone EIC
DOMAIN = "10Y1001A1001A82H"

start = pd.Timestamp(
    "2024-01-02", tz="Europe/Berlin"
).tz_convert("UTC")

end = pd.Timestamp(
    "2024-01-03", tz="Europe/Berlin"
).tz_convert("UTC")

params = {
    "securityToken": api_key,
    "documentType": "A65",
    "processType": "A01",
    "outBiddingZone_Domain": DOMAIN,
    "periodStart": start.strftime("%Y%m%d%H%M"),
    "periodEnd": end.strftime("%Y%m%d%H%M"),
}

response = requests.get(
    "https://web-api.tp.entsoe.eu/api",
    params=params,
    timeout=60
)

response.raise_for_status()

root = ET.fromstring(response.content)

def local_name(tag):
    return tag.split("}")[-1]

print("Response root:", local_name(root.tag))

for element in root.iter():
    if local_name(element.tag) in {
        "createdDateTime",
        "revisionNumber",
        "documentType",
        "process.processType",
        "mRID"
    }:
        print(local_name(element.tag), ":", element.text)
