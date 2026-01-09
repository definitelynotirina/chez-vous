from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib

from services.geocoding_service import GeocodingService
from services.gemini_service import GeminiService
from services.transport_service import TransportService
from utils.cache import Cache

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:5173")}})

# Initialize services
geocoding_service = GeocodingService()
gemini_service = GeminiService()
transport_service = TransportService()
cache = Cache()

@app.route("/")
def home():
    return jsonify({"message": "Chez-vous API is running"})

@app.route("/api/analyze", methods=["POST"])
def analyze_address():
    data = request.get_json()
    address = data.get("address")

    if not address:
        return jsonify({"error": "Address is required"}), 400

    # Create cache key based on address
    cache_key = f"analysis_{hashlib.md5(address.lower().encode()).hexdigest()}"

    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return jsonify(cached_result)

    # Geocode the address
    geo_data = geocoding_service.geocode_address(address)
    if not geo_data:
        return jsonify({"error": "Address not found in Paris"}), 404

    # Get transport connectivity analysis
    transport_data = transport_service.analyze_connectivity(
        geo_data.get("latitude"),
        geo_data.get("longitude")
    )

    # Prepare data for Gemini analysis
    neighborhood_data = {
        "address": address,
        "arrondissement": geo_data.get("arrondissement"),
        "neighborhood": geo_data.get("neighborhood"),
        "district": geo_data.get("district"),
        "coordinates": {
            "latitude": geo_data.get("latitude"),
            "longitude": geo_data.get("longitude")
        },
        "transport": transport_data
    }

    # Get AI analysis
    analysis = gemini_service.analyze_neighborhood(neighborhood_data)
    if not analysis:
        return jsonify({"error": "Failed to analyze neighborhood"}), 500

    # Build response
    result = {
        "address": address,
        "geo_data": geo_data,
        "transport": transport_data,
        "analysis": analysis
    }

    # Cache the result
    cache.set(cache_key, result)

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
