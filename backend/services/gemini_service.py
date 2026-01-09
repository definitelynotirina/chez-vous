import google.generativeai as genai
import os
import json
from typing import Dict, Optional
from ratelimit import limits, sleep_and_retry

class GeminiService:
    """
    Handles AI analysis using Google Gemini API (free tier)
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Free tier: 15 requests per minute
        self.rpm_limit = int(os.getenv("GEMINI_RPM_LIMIT", 15))

    @sleep_and_retry
    @limits(calls=15, period=60)
    def analyze_neighborhood(self, neighborhood_data: Dict) -> Optional[Dict]:
        """
        Returns structured analysis or None on error.
        """
        prompt = self._build_analysis_prompt(neighborhood_data)

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Try to parse JSON response
            # Gemini sometimes wraps JSON in markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            return json.loads(result_text)

        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return None

    def _build_analysis_prompt(self, data: Dict) -> str:
        """
        Build a structured prompt for Gemini to analyze the neighborhood.
        """
        arrondissement = data.get("arrondissement", "Unknown")
        address = data.get("address", "Unknown address")

        prompt = f"""You are analyzing a Paris neighborhood for someone looking for accommodation.

Address: {address}
Arrondissement: {arrondissement}

Based on your knowledge of Paris neighborhoods, provide a comprehensive analysis in JSON format with the following structure:

{{
  "overview": {{
    "description": "2-3 sentence overview of the neighborhood character",
    "three_word_summary": "Three words that capture the essence (e.g., 'Historic, Vibrant, Charming')"
  }},
  "ratings": {{
    "safety": {{"score": 1-5, "justification": "brief explanation"}},
    "walkability": {{"score": 1-5, "justification": "brief explanation"}},
    "nightlife": {{"score": 1-5, "justification": "brief explanation"}},
    "family_friendly": {{"score": 1-5, "justification": "brief explanation"}},
    "food_scene": {{"score": 1-5, "justification": "brief explanation"}},
    "quietness": {{"score": 1-5, "justification": "brief explanation"}},
    "tourist_density": {{"score": 1-5, "justification": "1=few tourists, 5=very touristy"}}
  }},
  "highlights": [
    "Key characteristic 1",
    "Key characteristic 2",
    "Key characteristic 3",
    "Key characteristic 4"
  ],
  "recommendations": {{
    "cafes": ["Café name 1 - why it's good", "Café name 2 - why it's good"],
    "restaurants": ["Restaurant 1 - cuisine type and why", "Restaurant 2 - cuisine type and why"],
    "activities": ["Activity 1 with brief description", "Activity 2 with brief description"]
  }},
  "nearby_landmarks": [
    {{"name": "Landmark name", "travel_time": "e.g., 15 min walk or 20 min metro"}},
    {{"name": "Another landmark", "travel_time": "estimated time"}}
  ]
}}

Return ONLY valid JSON, no additional text."""

        return prompt

    def compare_addresses(self, address1_analysis: Dict, address2_analysis: Dict) -> Optional[Dict]:
        """
        Compare two addresses and provide recommendation.
        """
        prompt = f"""Compare these two Paris neighborhoods for someone choosing accommodation:

Address 1 Analysis:
{json.dumps(address1_analysis, indent=2)}

Address 2 Analysis:
{json.dumps(address2_analysis, indent=2)}

Provide a comparison in JSON format:

{{
  "better_for": {{
    "families": "address1 or address2 with brief reason",
    "nightlife": "address1 or address2 with brief reason",
    "safety": "address1 or address2 with brief reason",
    "budget": "address1 or address2 with brief reason",
    "tourists": "address1 or address2 with brief reason",
    "quiet_living": "address1 or address2 with brief reason"
  }},
  "overall_recommendation": "Which address is better overall and why (2-3 sentences)"
}}

Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text

            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            return json.loads(result_text)

        except Exception as e:
            print(f"Gemini comparison error: {e}")
            return None
