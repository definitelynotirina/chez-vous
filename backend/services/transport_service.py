import requests
import math
from typing import Dict, List, Optional, Tuple

class TransportService:
    """
    Analyzes public transport connectivity for Paris addresses.
    Uses OpenStreetMap Overpass API for station data.
    """

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    # Major Paris landmarks with coordinates
    LANDMARKS = {
        "Eiffel Tower": (48.8584, 2.2945),
        "Louvre": (48.8606, 2.3376),
        "Sacré-Cœur": (48.8867, 2.3431),
        "Arc de Triomphe": (48.8738, 2.2950),
        "Notre-Dame": (48.8530, 2.3499),
        "Champs-Élysées": (48.8698, 2.3078)
    }

    # Metro lines that run late (past midnight on weekends)
    LATE_NIGHT_LINES = ["1", "2", "4", "6", "14"]

    def __init__(self):
        self.headers = {
            "User-Agent": "Chez-vous/1.0 (Paris neighborhood finder)"
        }

    def analyze_connectivity(self, latitude: float, longitude: float) -> Dict:
        """
        Complete transport analysis for a location.
        Returns nearby stations, travel times to landmarks, and connectivity score.
        """
        nearby_stations = self._get_nearby_stations(latitude, longitude)
        landmark_times = self._calculate_landmark_times(latitude, longitude, nearby_stations)
        connectivity_score = self._calculate_connectivity_score(nearby_stations, landmark_times)

        return {
            "nearby_stations": nearby_stations,
            "landmark_travel_times": landmark_times,
            "connectivity_score": connectivity_score,
            "has_late_night_service": self._has_late_night_service(nearby_stations)
        }

    def _get_nearby_stations(self, lat: float, lon: float, radius: int = 500) -> List[Dict]:
        """
        Find metro, RER, and tram stations within radius (meters).
        """
        query = f"""
        [out:json];
        (
          node["railway"="station"]["station"="subway"](around:{radius},{lat},{lon});
          node["railway"="station"]["station"="light_rail"](around:{radius},{lat},{lon});
          node["railway"="stop"]["public_transport"="stop_position"](around:{radius},{lat},{lon});
        );
        out body;
        """

        try:
            response = requests.post(
                self.OVERPASS_URL,
                data=query,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                return []

            data = response.json()
            stations = []

            for element in data.get("elements", []):
                station_lat = element.get("lat")
                station_lon = element.get("lon")
                tags = element.get("tags", {})

                name = tags.get("name", "Unknown Station")
                lines = self._extract_lines(tags)

                if station_lat and station_lon:
                    distance = self._calculate_distance(lat, lon, station_lat, station_lon)
                    walk_time = self._calculate_walk_time(distance)

                    stations.append({
                        "name": name,
                        "lines": lines,
                        "distance_meters": round(distance),
                        "walk_time_minutes": walk_time,
                        "transport_type": self._get_transport_type(tags)
                    })

            # Remove duplicates and sort by distance
            stations = self._deduplicate_stations(stations)
            stations.sort(key=lambda x: x["distance_meters"])

            return stations[:10]  # Return closest 10 stations

        except Exception as e:
            print(f"Error fetching stations: {e}")
            return []

    def _extract_lines(self, tags: Dict) -> List[str]:
        """Extract metro/RER line numbers from station tags."""
        lines = []

        # Check various tag formats
        if "ref" in tags:
            lines.append(tags["ref"])
        if "line" in tags:
            lines.append(tags["line"])
        if "lines" in tags:
            lines.extend(tags["lines"].split(";"))

        # Clean up line numbers
        lines = [line.strip() for line in lines if line.strip()]
        return list(set(lines))  # Remove duplicates

    def _get_transport_type(self, tags: Dict) -> str:
        """Determine if station is metro, RER, tram, etc."""
        if tags.get("station") == "subway":
            return "Metro"
        elif tags.get("station") == "light_rail":
            return "Tram"
        elif "RER" in tags.get("name", ""):
            return "RER"
        else:
            return "Metro"

    def _calculate_landmark_times(self, lat: float, lon: float, stations: List[Dict]) -> List[Dict]:
        """
        Calculate estimated travel times to major landmarks.
        Returns list with landmark name and time estimate.
        """
        times = []

        for landmark_name, (landmark_lat, landmark_lon) in self.LANDMARKS.items():
            distance = self._calculate_distance(lat, lon, landmark_lat, landmark_lon)

            # If very close, just walk
            if distance < 1500:  # 1.5km
                walk_time = self._calculate_walk_time(distance)
                times.append({
                    "landmark": landmark_name,
                    "time": f"{walk_time} min walk",
                    "estimated_minutes": walk_time
                })
            else:
                # Estimate metro travel
                # Rough estimate: 10 min walk to station + distance/600m per min on metro
                metro_time = 10 + int(distance / 600)
                times.append({
                    "landmark": landmark_name,
                    "time": f"{metro_time} min metro",
                    "estimated_minutes": metro_time
                })

        return times

    def _calculate_connectivity_score(self, stations: List[Dict], landmark_times: List[Dict]) -> int:
        """
        Calculate connectivity score (1-5) based on:
        - Number of nearby stations
        - Number of different lines accessible
        - Average time to landmarks
        """
        score = 0

        # Station count (max 2 points)
        if len(stations) >= 5:
            score += 2
        elif len(stations) >= 3:
            score += 1.5
        elif len(stations) >= 1:
            score += 1

        # Line diversity (max 2 points)
        all_lines = set()
        for station in stations:
            all_lines.update(station.get("lines", []))

        if len(all_lines) >= 5:
            score += 2
        elif len(all_lines) >= 3:
            score += 1.5
        elif len(all_lines) >= 1:
            score += 1

        # Average landmark time (max 1 point)
        avg_time = sum(t["estimated_minutes"] for t in landmark_times) / len(landmark_times)
        if avg_time <= 15:
            score += 1
        elif avg_time <= 25:
            score += 0.5

        return min(5, round(score))

    def _has_late_night_service(self, stations: List[Dict]) -> bool:
        """Check if any nearby station has late-night metro service."""
        for station in stations:
            for line in station.get("lines", []):
                if line in self.LATE_NIGHT_LINES:
                    return True
        return False

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in meters using Haversine formula."""
        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def _calculate_walk_time(self, distance_meters: float) -> int:
        """Calculate walking time. Average speed: 5 km/h = 83.3 m/min."""
        return max(1, round(distance_meters / 83.3))

    def _deduplicate_stations(self, stations: List[Dict]) -> List[Dict]:
        """Remove duplicate stations (same name, different entries)."""
        seen = {}
        for station in stations:
            name = station["name"]
            if name not in seen or station["distance_meters"] < seen[name]["distance_meters"]:
                seen[name] = station
        return list(seen.values())
