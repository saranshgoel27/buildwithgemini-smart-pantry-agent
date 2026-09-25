import os
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY environment variable is not set in .env"
        )
    return key


def geocode_address(address: str) -> Dict[str, Any]:
    """Converts a street address or location name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or place name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        A dictionary containing formatted_address, location (latitude and longitude), and place_id.
    """
    key = _get_api_key()
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": key}

    response = httpx.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "OK" or not data.get("results"):
        return {
            "error": f"Geocoding failed for address '{address}': {data.get('status', 'No results')}"
        }

    first_result = data["results"][0]
    loc = first_result["geometry"]["location"]

    return {
        "address_queried": address,
        "formatted_address": first_result.get("formatted_address"),
        "location": {
            "latitude": loc.get("lat"),
            "longitude": loc.get("lng"),
        },
        "place_id": first_result.get("place_id"),
    }


def find_nearby_places(
    location_name: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    place_type: str = "supermarket",
    radius_meters: float = 2000.0,
) -> List[Dict[str, Any]]:
    """Finds nearby places of a given type around a location name (e.g. 'San Francisco', 'Mountain View', or street address) or geographic coordinates using the Places API (New).

    Args:
        location_name: Name of the city, address, or location (e.g., 'San Francisco', 'Mountain View, CA'). If provided, auto-geocodes to lat/lng.
        latitude: Latitude of the center point (if location_name is not provided).
        longitude: Longitude of the center point (if location_name is not provided).
        place_type: Type of place to search for (e.g. 'supermarket', 'grocery_store', 'bakery', 'restaurant').
        radius_meters: Search radius in meters (default 2000 meters / 2km).

    Returns:
        A list of nearby places with key fields: name, address, and location.
    """
    if location_name and (latitude is None or longitude is None):
        geo_result = geocode_address(location_name)
        if "location" in geo_result:
            latitude = geo_result["location"]["latitude"]
            longitude = geo_result["location"]["longitude"]
        else:
            return [{"error": f"Could not geocode location: '{location_name}'"}]

    if latitude is None or longitude is None:
        return [{"error": "Must provide either location_name or latitude and longitude."}]

    key = _get_api_key()
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }

    body = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    response = httpx.post(url, headers=headers, json=body)
    response.raise_for_status()
    data = response.json()

    places = []
    for place in data.get("places", []):
        display_name = place.get("displayName", {}).get("text", "Unknown")
        formatted_address = place.get("formattedAddress", "N/A")
        loc = place.get("location", {})

        places.append({
            "name": display_name,
            "address": formatted_address,
            "location": {
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
            },
            "types": place.get("types", []),
        })

    return places
