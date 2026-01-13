import requests
import time
from typing import Optional, Dict

class GeocodingService:

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.headers = {
            "User-Agent": "Chez-vous/1.0 (Paris neighborhood finder)"
        }

    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocode any Paris address format using Nominatim with Paris bounds.
        Handles: postcodes, streets, full addresses, with/without "Paris" or "France", any order.
        """
        cleaned = address.strip()

        # Paris bounding box (limits search to Paris region)
        paris_bbox = "2.224122,48.815573,2.469920,48.902145"

        params = {
            "q": cleaned,
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            "bounded": 1,
            "viewbox": paris_bbox,
            "countrycodes": "fr"
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )

            time.sleep(1)  # Respect rate limit

            if response.status_code != 200:
                print(f"Nominatim returned status {response.status_code}")
                return None

            results = response.json()

            if not results:
                print(f"No results found for: {cleaned}")
                return None

            # Find best Paris result
            for result in results:
                address_details = result.get("address", {})

                city = address_details.get("city", "").lower()
                town = address_details.get("town", "").lower()
                municipality = address_details.get("municipality", "").lower()
                postcode = address_details.get("postcode", "")

                # Verify it's actually in Paris
                is_paris = (
                    "paris" in city or
                    "paris" in town or
                    "paris" in municipality or
                    (postcode and postcode.startswith("75"))
                )

                if is_paris:
                    arrondissement = self._extract_arrondissement(postcode)

                    return {
                        "latitude": float(result["lat"]),
                        "longitude": float(result["lon"]),
                        "arrondissement": arrondissement,
                        "postcode": postcode,
                        "full_address": result.get("display_name", ""),
                        "neighborhood": address_details.get("suburb") or address_details.get("neighbourhood"),
                        "district": address_details.get("city_district")
                    }

            print(f"Results found but none in Paris for: {cleaned}")
            return None

        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def _extract_arrondissement(self, postcode: str) -> Optional[int]:
        """
        Extract arrondissement number from Paris postcode.
        75001 -> 1, 75020 -> 20, etc.
        """
        if not postcode or not postcode.startswith("75"):
            return None

        try:
            arr_num = int(postcode[3:])
            return arr_num if 1 <= arr_num <= 20 else None
        except (ValueError, IndexError):
            return None
