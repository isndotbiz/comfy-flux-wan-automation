import requests
import json

# PromptSmith API endpoint
PROMPTSMITH_URL = "http://172.23.133.250:8080"

def enhance_prompt(basic_prompt):
    payload = {
        "prompt": f"Enhance this text-to-image prompt: {basic_prompt}",
        "n_predict": 200,
        "temperature": 0.85,
        "top_p": 0.92,
        "stop": ["User:", "\n\n"]
    }
    
    try:
        response = requests.post(f"{PROMPTSMITH_URL}/completion", 
                               json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Example usage
if __name__ == "__main__":
    print("Testing PromptSmith API...")
    enhanced = enhance_prompt("a cat sitting on a windowsill")
    if enhanced:
        print("Enhanced prompt:")
        print(enhanced.get('content', enhanced))
    else:
        print("Failed to get enhanced prompt")
