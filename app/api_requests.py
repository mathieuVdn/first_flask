import requests
import json
import os
from flask import render_template, flash


class MarketSearchAPI:
    base_url = "https://devapi.ai/"
    print("test", os.getenv("PERSONAL_ACCESS_TOKEN"))

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
                if response["success"]:
                    flash(f'error: Search requested for symbol {query} failed')
                    return None
                else:
                    result = response.json()
                    return result["body"]
            else:
                print(f"Erreur {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Erreur de connexion : {e}")
            return None



