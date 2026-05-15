import urllib.request
import urllib.error
import threading
import time
import json
import sys

BASE_URL = "http://127.0.0.1:7860"
N8N_ENDPOINT = f"{BASE_URL}/n8n/sync"

def send_request(idx, request_id, prompt, results_list):
    print(f"Thread {idx}: Sending request {request_id}...")
    headers = {'Content-Type': 'application/json'}
    payload = {
        "prompt": prompt,
        "model_type": "ltx2_distilled_gguf_q4_k_m",
        "resolution": "768x432",
        "video_length": 9,
        "num_inference_steps": 1,
        "request_id": request_id
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(N8N_ENDPOINT, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=1200) as response:
            body = response.read().decode('utf-8')
            print(f"Thread {idx}: Finished. Status: {response.status}")
            results_list.append({"thread": idx, "status": response.status, "data": json.loads(body)})
    except urllib.error.HTTPError as e:
        print(f"Thread {idx}: Failed with HTTP {e.code}: {e.read().decode()}")
        results_list.append({"thread": idx, "error": f"HTTP {e.code}"})
    except Exception as e:
        print(f"Thread {idx}: Failed with error: {e}")
        results_list.append({"thread": idx, "error": str(e)})

def test_idempotency_v2():
    print("--- Testing Idempotency (Retry Storm Simulation) ---")
    req_id = f"test_retry_urllib_{int(time.time())}"
    prompt = "A green cube rotating"
    
    results = []
    
    t1 = threading.Thread(target=send_request, args=(1, req_id, prompt, results))
    t2 = threading.Thread(target=send_request, args=(2, req_id, prompt, results))
    
    # Start T1
    t1.start()
    
    # Wait 2 seconds (simulate timeout retry)
    time.sleep(2)
    
    # Start T2 (duplicate)
    t2.start()
    
    t1.join()
    t2.join()
    
    print("\n--- Results ---")
    for res in results:
        print(json.dumps(res, indent=2))
        
    # Validation
    valid_data = [r.get("data", {}) for r in results if "data" in r]
    urls = [d.get("url") for d in valid_data]
    
    if len(urls) == 2 and urls[0] == urls[1]:
         print("\nSUCCESS: Both requests returned the SAME URL.")
         print(f"URL: {urls[0]}")
    else:
         print("\nFAILURE: URLs do not match or requests failed.")
         print(f"URLs found: {urls}")

if __name__ == "__main__":
    try:
        with urllib.request.urlopen(BASE_URL) as r:
            print(f"Server is up: {r.status}")
        test_idempotency_v2()
    except Exception as e:
        print(f"Could not connect to server at {BASE_URL}. Is it running?")
        print(e)
