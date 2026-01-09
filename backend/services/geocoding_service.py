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
        Convert a Paris address to coordinates and extract arrondissement info.
        Returns dict with lat, lon, arrondissement, full_address or None if not found.
        """
        # Add Paris, France to ensure we're searching in Paris
        search_query = f"{address}, Paris, France"

        params = {
            "q": search_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )

            # Respect Nominatim's usage policy (max 1 req/sec)
            time.sleep(1)

            if response.status_code == 200:
                results = response.json()

                if not results:
                    return None

                result = results[0]
                address_details = result.get("address", {})

                # Extract arrondissement from postcode (75001 -> 1st arrondissement)
                postcode = address_details.get("postcode", "")
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
