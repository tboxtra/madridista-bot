import os
import requests
import json

class TwitterClient:
    def __init__(self):
        self.api_key = os.getenv("TWITTERAPI_KEY")
        self.base_url = "https://api.twitterapi.io"
        
        if not self.api_key:
            raise RuntimeError("Missing required TwitterAPI.io key: TWITTERAPI_KEY")

    def post(self, text: str) -> str:
        """
        Posts a tweet using TwitterAPI.io. Returns the tweet ID string on success.
        """
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text
        }
        
        try:
            print(f"🔍 Debug: POSTing to {self.base_url}/api/tweet")
            print(f"🔍 Debug: Headers: {headers}")
            print(f"🔍 Debug: Payload: {payload}")
            
            response = requests.post(
                f"{self.base_url}/v2/tweets",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"🔍 Debug: Response status: {response.status_code}")
            print(f"🔍 Debug: Response headers: {dict(response.headers)}")
            print(f"🔍 Debug: Response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return str(result.get("data", {}).get("id", "unknown"))
            else:
                raise RuntimeError(f"TwitterAPI.io error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error posting tweet: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from TwitterAPI.io: {e}")
