from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:5173")}})

@app.route("/")
def home():
    return jsonify({"message": "Chez-vous API is running"})

@app.route("/api/analyze", methods=["POST"])
def analyze_address():
    data = request.get_json()
    address = data.get("address")

    if not address:
        return jsonify({"error": "Address is required"}), 400

    # TODO: implement analysis logic
    return jsonify({
        "address": address,
        "status": "pending",
        "message": "Analysis not yet implemented"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
