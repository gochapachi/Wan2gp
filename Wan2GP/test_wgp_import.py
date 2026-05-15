
import sys
import os

# Put Wan2GP in path
sys.path.append(os.getcwd())

print("BEFORE IMPORT", flush=True)
try:
    import wgp
    print("AFTER IMPORT", flush=True)
    if hasattr(wgp, "main"):
        print("Main function found!", flush=True)
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

print("Test complete.")
