"""
Sonarr v3 API integration
"""
import requests
from typing import Optional, Tuple


class SonarrIntegration:
    def __init__(self, baseurl: str, api_key: str):
        self.baseurl = baseurl.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-Api-Key": api_key}
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Sonarr connection"""
        try:
            url = f"{self.baseurl}/api/v3/system/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)
    
    def find_series_by_tvdb_id(self, tvdb_id: int) -> Optional[dict]:
        """Find series by TVDB ID"""
        try:
            url = f"{self.baseurl}/api/v3/series"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                series_list = response.json()
                for series in series_list:
                    if series.get("tvdbId") == tvdb_id:
                        return series
            return None
        except Exception as e:
            print(f"Error finding series: {e}")
            return None
    
    def find_series_by_title(self, title: str) -> Optional[dict]:
        """Find series by title"""
        try:
            url = f"{self.baseurl}/api/v3/series"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                series_list = response.json()
                # Try exact match first
                for series in series_list:
                    if series.get("title") == title or series.get("titleSlug") == title:
                        return series
                # Try fuzzy match
                for series in series_list:
                    if title.lower() in series.get("title", "").lower():
                        return series
            return None
        except Exception as e:
            print(f"Error finding series: {e}")
            return None
    
    def delete_series(self, series_id: int, delete_files: bool = True) -> Tuple[bool, str]:
        """Delete series via Sonarr"""
        try:
            url = f"{self.baseurl}/api/v3/series/{series_id}"
            params = {"deleteFiles": str(delete_files).lower()}
            response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return True, "Series deleted successfully"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)

