"""Get All Campaigns stream"""

import json
from typing import Any, Dict, List, Optional

import requests
import singer

from tap_apple_search_ads import api
from tap_apple_search_ads.api.auth import RequestHeadersValue

logger = singer.get_logger()

DEFAULT_URL = "https://api.searchads.apple.com/api/v5/campaigns"

PROPERTIES_TO_SERIALIZE = {
    "budgetOrders",
    "countriesOrRegions",
    "countryOrRegionServingStateReasons",
    "locInvoiceDetails",
    "servingStateReasons",
    "supplySources",
}


def sync(headers: RequestHeadersValue) -> List[Dict[str, Any]]:
    logger.info("Sync: campaigns")
    response = requests.get(DEFAULT_URL, headers=headers)
    api.utils.check_response(response)
    campaigns = response.json()["data"]
    logger.info("Synced [%s] campaings", len(campaigns))
    return campaigns


def to_schema(record: Dict[str, Any]) -> Dict[str, Any]:
    budgetAmount = record.pop("budgetAmount") or {}

    record["budgetAmount_currency"] = budgetAmount.get("currency")
    record["budgetAmount_amount"] = budgetAmount.get("amount")

    dailyBudgetAmount = record.pop("dailyBudgetAmount") or {}

    record["dailyBudgetAmount_currency"] = dailyBudgetAmount.get("currency")
    record["dailyBudgetAmount_amount"] = dailyBudgetAmount.get("amount")

    for key in PROPERTIES_TO_SERIALIZE:
        value = record.pop(key)
        record[key] = serialize(value)

    return record


def serialize(value: Any) -> Optional[str]:
    if value is None:
        return None

    value_str = json.dumps(value)

    return value_str
