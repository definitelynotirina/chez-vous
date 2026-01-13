import requests
from bs4 import BeautifulSoup
import time
import os
from typing import List, Dict
from datetime import datetime

class RedditScraper:
    """
    Scrapes r/paris for neighborhood insights and resident experiences.
    PRIMARY source for authentic word-of-mouth about neighborhoods.
    Uses web scraping (no API credentials needed).
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        self.base_url = "https://www.reddit.com"

    def get_neighborhood_insights(self, arrondissement: int, neighborhood_name: str = None) -> Dict:
        """
        Search r/paris for posts about a specific arrondissement/neighborhood.
        Returns compiled insights from real residents.
        """
        if not arrondissement:
            return {"posts": [], "summary": "No arrondissement data available"}

        # Build search queries
        queries = self._build_search_queries(arrondissement, neighborhood_name)

        all_posts = []
        for query in queries:
            posts = self._search_posts(query, limit=10)
            all_posts.extend(posts)

        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post["id"] not in seen_ids:
                seen_ids.add(post["id"])
                unique_posts.append(post)

        return {
            "posts": unique_posts[:15],  # Top 15 most relevant posts
            "total_found": len(unique_posts),
            "queries_used": queries
        }

    def _build_search_queries(self, arrondissement: int, neighborhood_name: str = None) -> List[str]:
        """
        Build search queries targeting neighborhood discussions.
        Focus on: living experiences, safety, vibe, recommendations.
        """
        arr_variations = [
            f"{arrondissement}",
            f"{arrondissement}th",
            f"{arrondissement}e",
            f"75{arrondissement:02d}"  # Postal code format
        ]

        queries = []

        # Direct arrondissement queries
        for arr in arr_variations:
            queries.append(f"living {arr} arrondissement")
            queries.append(f"moving to {arr} arrondissement")
            queries.append(f"{arr} arrondissement safe")
            queries.append(f"{arr} arrondissement neighborhood")

        # If specific neighborhood name provided, add those queries
        if neighborhood_name:
            queries.append(f"living in {neighborhood_name}")
            queries.append(f"{neighborhood_name} neighborhood")
            queries.append(f"moving to {neighborhood_name}")

        return queries[:3]  # Limit to top 3 queries for faster response

    def _search_posts(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search r/paris for posts matching the query using web scraping.
        Extract title, body, score, and comments.
        """
        posts = []

        try:
            # Build Reddit search URL
            search_url = f"{self.base_url}/r/paris/search.json"
            params = {
                "q": query,
                "restrict_sr": "on",
                "sort": "relevance",
                "limit": limit
            }

            # Make request with delay to respect rate limits
            time.sleep(0.5)  # Reduced delay for faster responses
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                print(f"Reddit API returned status {response.status_code}")
                return posts

            data = response.json()

            for post_data in data.get("data", {}).get("children", []):
                post = post_data.get("data", {})

                # Extract basic post info
                posts.append({
                    "id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "text": post.get("selftext", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "url": f"{self.base_url}{post.get('permalink', '')}",
                    "created": datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d") if post.get("created_utc") else "Unknown",
                    "top_comments": []  # We'll skip comments for simplicity
                })

        except Exception as e:
            print(f"Reddit search error for '{query}': {e}")

        return posts

    def format_for_gemini(self, reddit_data: Dict) -> str:
        """
        Format Reddit insights into a readable text block for Gemini analysis.
        """
        if not reddit_data.get("posts"):
            return "No Reddit discussions found for this neighborhood."

        formatted = "REDDIT INSIGHTS (Real resident experiences from r/paris):\n\n"

        for i, post in enumerate(reddit_data["posts"][:10], 1):
            formatted += f"{i}. {post['title']}\n"

            if post.get("text"):
                # Truncate long posts
                text = post["text"][:300]
                if len(post["text"]) > 300:
                    text += "..."
                formatted += f"   Post: {text}\n"

            if post.get("top_comments"):
                formatted += "   Top comments:\n"
                for comment in post["top_comments"]:
                    comment_text = comment["text"][:200]
                    if len(comment["text"]) > 200:
                        comment_text += "..."
                    formatted += f"   - {comment_text}\n"

            formatted += f"   (Score: {post['score']}, Comments: {post['num_comments']})\n\n"

        return formatted
