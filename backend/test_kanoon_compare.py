import requests
import json
import sys

def test_compare(left_id, right_id):
    url = f"http://localhost:8000/api/kanoon/compare?left={left_id}&right={right_id}"
    print(f"Testing comparison: {left_id} vs {right_id}")
    try:
        resp = requests.get(url, timeout=120) # Long timeout for processing
        if resp.status_code == 200:
            print("Success!")
            data = resp.json()
            # Save to file for inspection
            filename = f"comparison_{left_id}_{right_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Saved result to {filename}")
            
            # Verify SWOT is gone
            comparison = data.get('comparison', {})
            if 'swot' in comparison:
                print("FAILURE: 'swot' field still present in comparison!")
            else:
                print("Verified: 'swot' field is absent.")
                
        else:
            print(f"Failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # IDs from user
    # 7614885 vs 76449328
    test_compare("7614885", "76449328")
