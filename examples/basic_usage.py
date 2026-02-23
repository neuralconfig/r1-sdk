"""
Basic usage example for the R1 SDK.

Demonstrates how to authenticate, list venues, and query access points.
"""

import logging
from r1_sdk import R1Client
from r1_sdk.exceptions import APIError, ResourceNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create client from config.ini (or use R1Client.from_env() for env vars)
    client = R1Client.from_config()

    logger.info("Successfully authenticated with R1 API")

    # List venues
    venues = client.venues.list(page_size=10)
    venue_list = venues.get('data', [])

    if not venue_list:
        logger.info("No venues found")
        return

    logger.info(f"Found {len(venue_list)} venues")
    first_venue = venue_list[0]
    venue_id = first_venue['id']
    logger.info(f"First venue: {first_venue['name']} (ID: {venue_id})")

    # Get venue details
    venue = client.venues.get(venue_id)
    logger.info(f"Venue: {venue.get('name')}")

    # List APs in venue
    aps = client.aps.list({"venueId": venue_id, "pageSize": 10, "page": 0})
    ap_list = aps.get('data', [])
    logger.info(f"Found {len(ap_list)} APs in venue")

    for ap in ap_list:
        logger.info(f"  AP: {ap.get('name', 'Unnamed')} (Model: {ap.get('model')}, MAC: {ap.get('apMac')})")

    # List WLANs
    wlans = client.wlans.list({"pageSize": 10, "page": 0})
    wlan_list = wlans.get('data', [])
    logger.info(f"Found {len(wlan_list)} WLANs")


if __name__ == "__main__":
    try:
        main()
    except APIError as e:
        logger.error(f"API Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
