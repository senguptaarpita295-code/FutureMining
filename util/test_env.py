import urllib.request

try:
    with urllib.request.urlopen("http://localhost:11434", timeout=3) as res:
        print(" Ollama is running and connected successfully!")
except Exception as e:
    print(" Ollama connection failed:", e)