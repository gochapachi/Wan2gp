import sys
import os
sys.path.append(os.getcwd())
print("STARTING TEST", flush=True)
try:
    import wgp
    print(f"IMPORT SUCCESS. wan_app: {wgp.wan_app}", flush=True)
except Exception as e:
    print(f"FAILED: {e}", flush=True)
    import traceback
    traceback.print_exc()
