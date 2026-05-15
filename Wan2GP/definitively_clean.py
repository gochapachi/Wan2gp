import os
import subprocess
import time

def kill_python():
    print("Killing python processes...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
    except:
        pass
    time.sleep(2)

def clean_logs():
    logs = ["wgp_critical_crash.log", "wgp_debug_app.log", "wgp_debug_ui.log", "wgp_debug_startup.log", "startup.lock"]
    for log in logs:
        path = os.path.join(r"D:\Wan2gp\Wan2GP", log)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Deleted {log}")
            except Exception as e:
                print(f"Failed to delete {log}: {e}")

if __name__ == "__main__":
    kill_python()
    clean_logs()
