import json

def analyze():
    try:
        with open("d:/Wan2gp/api_spec.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Found {len(data.get('named_endpoints', {}))} named endpoints.")
        print(f"Found {len(data.get('unnamed_endpoints', {}))} unnamed endpoints.")
        
        for name, details in data.get('named_endpoints', {}).items():
            print(f"\n--- Endpoint: {name} ---")
            params = details.get('parameters', [])
            print("Parameters:")
            for p in params:
                label = p.get('label', 'No Label')
                component = p.get('component', 'Unknown')
                print(f"  - {label} ({component})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
