import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("API Key tidak ditemukan di .env!")
    exit(1)

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

data = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hai"}],
    "max_tokens": 10
}

req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'))

try:
    with urllib.request.urlopen(req) as response:
        headers = response.headers
        remaining_requests = headers.get('x-ratelimit-remaining-requests', 'N/A')
        remaining_tokens = headers.get('x-ratelimit-remaining-tokens', 'N/A')
        reset_requests = headers.get('x-ratelimit-reset-requests', 'N/A')
        reset_tokens = headers.get('x-ratelimit-reset-tokens', 'N/A')
        
        print("=== INFO LIMIT API GROQ ANDA ===")
        print(f"Model: llama-3.1-8b-instant\n")
        print(f"Sisa Request Hari Ini (RPD) : {remaining_requests} request")
        print(f"Sisa Token Menit Ini (TPM)  : {remaining_tokens} token")
        print(f"Token Reset dalam           : {reset_tokens}")
        print(f"Request Reset dalam         : {reset_requests}")
except urllib.error.HTTPError as e:
    print(f"Error API: {e.code}")
    print("Headers:", e.headers)
except Exception as e:
    print(f"Error: {e}")
