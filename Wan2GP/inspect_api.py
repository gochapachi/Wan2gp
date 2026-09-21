import sys
import io
import os

# Force stdout/stderr to utf-8 before any other imports could print
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
except Exception:
    pass

from gradio_client import Client
import json

def inspect():
    try:
        # Use contextlib just in case, though encoding fix should handle it
        client = Client("http://127.0.0.1:7860/")
        api_info = client.view_api(return_format="dict")
        
        with open("d:/Wan2gp/api_spec.json", "w", encoding="utf-8") as f:
            json.dump(api_info, f, indent=2, ensure_ascii=False)
            
        print("API spec written to d:/Wan2gp/api_spec.json")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect()
