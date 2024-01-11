import requests
import json
import os


class MarketSearchAPI:
    base_url = "https://devapi.ai/"
    print(os.environ.get("PERSONAL_ACCESS_TOKEN"))

    def search_quote(self, query):

        endpoint = "api/v1/markets/quote"
        url = self.base_url + endpoint
        headers = {
            'Authorization': f'Bearer 361|NX2UmDOOgbKslnDaML5wwdpcTQSqWrgRWAIVE8iA',
        }
        params = {
            'ticker': query
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                result = response.json()
                return result["body"]
            else:
                print(f"Erreur {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Erreur de connexion : {e}")
            return None



