"""
Radarr v3 API integration
"""
import requests
from typing import Optional, Tuple


class RadarrIntegration:
    def __init__(self, baseurl: str, api_key: str):
        self.baseurl = baseurl.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-Api-Key": api_key}
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Radarr connection"""
        try:
            url = f"{self.baseurl}/api/v3/system/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)
    
    def find_movie_by_title(self, title: str) -> Optional[dict]:
        """Find movie by title"""
        try:
            url = f"{self.baseurl}/api/v3/movie"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                movies = response.json()
                # Try exact match first
                for movie in movies:
                    if movie.get("title") == title or movie.get("titleSlug") == title:
                        return movie
                # Try fuzzy match
                for movie in movies:
                    if title.lower() in movie.get("title", "").lower():
                        return movie
            return None
        except Exception as e:
            print(f"Error finding movie: {e}")
            return None
    
    def delete_movie(self, movie_id: int, delete_files: bool = True) -> Tuple[bool, str]:
        """Delete movie via Radarr"""
        try:
            url = f"{self.baseurl}/api/v3/movie/{movie_id}"
            params = {"deleteFiles": str(delete_files).lower()}
            response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return True, "Movie deleted successfully"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)

