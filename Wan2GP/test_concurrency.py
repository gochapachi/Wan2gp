
import threading
import requests
import time
import json
import uuid

BASE_URL = "http://127.0.0.1:7860/n8n/sync"

def send_request(request_id, results, index):
    payload = {
        "prompt": "A tiny test video for concurrency",
        "model_type": "alpha2",
        "video_length": 2,
        "num_inference_steps": 1,
        "request_id": request_id
    }
    print(f"[Thread {index}] Sending request for {request_id}...")
    try:
        response = requests.post(BASE_URL, json=payload, timeout=300)
        results[index] = response.json()
        print(f"[Thread {index}] Received response: {results[index]}")
    except Exception as e:
        results[index] = {"error": str(e)}
        print(f"[Thread {index}] Error: {e}")

def run_test():
    # Use the same request_id for all to trigger waiting/caching
    shared_request_id = f"concurrency_test_{uuid.uuid4().hex[:8]}"
    threads = []
    results = [None] * 3

    # Start 3 concurrent requests
    for i in range(3):
        t = threading.Thread(target=send_request, args=(shared_request_id, results, i))
        threads.append(t)
        t.start()
        time.sleep(1) # Small delay to ensure order in logs

    for t in threads:
        t.join()

    print("\n--- Summary of Concurrent Requests ---")
    for i, res in enumerate(results):
        print(f"Request {i}: {res}")

    # Test sequential (cached)
    print("\n--- Testing Sequential Cached Request ---")
    sequential_results = [None]
    send_request(shared_request_id, sequential_results, 0)
    print(f"Sequential Request: {sequential_results[0]}")

if __name__ == "__main__":
    run_test()
