
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Setup paths
ROOT_DIR = os.getcwd()
outputs_dir = os.path.join(ROOT_DIR, "outputs")
os.makedirs(outputs_dir, exist_ok=True)

# Create dummy file to test
test_file_path = os.path.join(outputs_dir, "test_file.txt")
with open(test_file_path, "w") as f:
    f.write("Hello from test server!")

print(f"Outputs dir: {outputs_dir}")
print(f"Test file created at: {test_file_path}")

app = FastAPI()

# Mount Static Files exactly as in wgp.py
try:
    app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")
    print("Mounted /outputs successfully.")
except Exception as e:
    print(f"Failed to mount /outputs: {e}")
    sys.exit(1)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    print("Starting test server on port 7861...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=7861)
    except Exception as e:
        print(f"Server crash: {e}")
