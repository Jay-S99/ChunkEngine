import requests
from config import Config

class Embedder:
    def __init__(self):
        self.api_url = Config.EMBEDDING_API_URL
        self.api_key = Config.EMBEDDING_API_KEY
        self.model = Config.EMBEDDING_MODEL_NAME

    def embed(self, texts):
        if not texts:
            print("Brak tekstów do osadzenia.")
            return []

        try:
            payload = {
                "model": self.model,
                "input": texts
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=60)

            
            print("Wysyłam do:", self.api_url)
            
            resp.raise_for_status()

            data = resp.json()
            return [item["embedding"] for item in data.get("data", [])]
        except Exception as e:
            print("Błąd podczas generowania embeddingów:", e)
            return []
# Debug#print("Payload:", payload)
            #print("Odpowiedź RAW:", resp.text)
