import requests
import json
import sys
from typing import Optional, Dict, Any


class PromptSmithClient:
    def __init__(self, base_urls=None):
        self.base_urls = base_urls or [
            "http://172.23.133.250:8080",
            "http://isndotbiz.com:38080",
            "http://73.140.158.252:38080",
        ]
        self.active_url = None
        self.find_active_endpoint()

    def find_active_endpoint(self):
        """Test endpoints to find an active one"""
        for url in self.base_urls:
            try:
                print(f"Testing endpoint: {url}")
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    self.active_url = url
                    print(f"✓ Active endpoint found: {url}")
                    return
            except requests.exceptions.RequestException:
                try:
                    # Try a basic connection test
                    response = requests.get(url, timeout=5)
                    self.active_url = url
                    print(f"✓ Endpoint responding: {url}")
                    return
                except requests.exceptions.RequestException:
                    print(f"✗ Endpoint not accessible: {url}")
                    continue

        print("⚠ No active endpoints found")

    def enhance_prompt(self, basic_prompt: str) -> Optional[Dict[Any, Any]]:
        if not self.active_url:
            print("No active endpoint available")
            return None

        payload = {
            "prompt": f"Enhance this text-to-image prompt: {basic_prompt}",
            "n_predict": 200,
            "temperature": 0.85,
            "top_p": 0.92,
            "stop": ["User:", "\n\n"],
        }

        try:
            print(f"Making request to: {self.active_url}/completion")
            response = requests.post(
                f"{self.active_url}/completion", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None


# Example usage
if __name__ == "__main__":
    client = PromptSmithClient()

    if client.active_url:
        test_prompt = "a cat sitting on a windowsill"
        print(f"\nEnhancing prompt: '{test_prompt}'")
        enhanced = client.enhance_prompt(test_prompt)

        if enhanced:
            print("\n" + "=" * 50)
            print("ENHANCED PROMPT:")
            print("=" * 50)
            content = enhanced.get("content", str(enhanced))
            print(content)
        else:
            print("Failed to enhance prompt")
    else:
        print("Cannot test - no active endpoints available")
