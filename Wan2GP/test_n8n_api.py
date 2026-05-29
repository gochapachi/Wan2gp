
import os
import sys
import shutil
import urllib.parse
import importlib.metadata
import importlib.util
from unittest.mock import MagicMock, patch

# --- Dynamic Mocking Infrastructure ---

class MockLoader:
    def create_module(self, spec):
        m = MagicMock()
        m.__path__ = [] # Mark as package
        # Default return for any handler query
        m.family_handler.query_family_maps.return_value = ({}, {})
        return m
    
    def exec_module(self, module):
        pass

class MockFinder:
    def find_spec(self, fullname, path, target=None):
        # Allow system modules and strict wgp import
        if fullname in sys.modules:
            return None
        
        # Don't mock the module we are trying to test if it's imported by name (though we load by path)
        if fullname == "wgp":
            return None
            
        # Create a mock spec for everything else
        spec = importlib.util.spec_from_loader(fullname, MockLoader())
        return spec

# Insert our dynamic mocker
sys.meta_path.insert(0, MockFinder())

# --- Specific Mocks (Pre-fill sys.modules for things accessed immediately) ---

# Torch is accessed immediately for logging
mock_torch = MagicMock()
mock_torch.backends.cuda.sdp_kernel = MagicMock()
mock_torch.cuda.get_device_capability.return_value = (8, 0)
sys.modules['torch'] = mock_torch
sys.modules['torch._logging'] = MagicMock()

# Pre-mock fastapi to handle from imports
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['fastapi.concurrency'] = MagicMock() # Also needed for run_in_threadpool

# --- Load wgp.py ---

# Determine the path to wgp.py
current_dir = os.path.dirname(os.path.abspath(__file__))
wgp_path = os.path.join(current_dir, 'd:/Wan2gp/Wan2GP')
sys.path.append(wgp_path)

# Import n8n_generate_api from wgp.py
spec = importlib.util.spec_from_file_location("wgp", "d:/Wan2gp/Wan2GP/wgp.py")
wgp = importlib.util.module_from_spec(spec)

# Mock dependencies inside wgp that need specific behavior or are used in logic
# We need to patch generic mocks with specific ones if needed, or just let them be MagicMocks.
# But wgp.generate_video MUST be our mock.

def mock_generate_video(*args, **kwargs):
    print("[TEST] mock_generate_video called")
    state = kwargs.get('state')
    # Simulate successful generation with spaces in filename to test renaming
    output_filename = os.path.join(os.getcwd(), "outputs", "test video output.mp4")
    # Ensure directory exists for the test
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w") as f:
        f.write("dummy content")
        
    if state and "gen" in state:
        state["gen"]["file_list"].append(output_filename)
    return True

# --- execution ---

if __name__ == "__main__":
    try:
        # Patch importlib.metadata.version mainly for mmgp check
        p1 = patch('importlib.metadata.version', return_value="3.7.6")
        # Patch os.remove to avoid deletion of mocked files
        p2 = patch('os.remove')
        
        with p1, p2:
            # Execute module to define functions
            spec.loader.exec_module(wgp)
            
        # Patch wgp internal references
        wgp.generate_video = mock_generate_video
        
        # Make gr.Error a real exception
        class MockError(Exception): pass
        wgp.gr.Error = MockError
        
        # Populate models_def to avoid early exit
        wgp.models_def = {
            "Wan2.1-T2V-1.3B": {
                "image_outputs": False,
                "audio_only": False,
                "architecture": "t2v"
            }
        }
        wgp.model_types_handlers = {"t2v": MagicMock()}
        
        # Inject mock state
        state = {
            "gen": {
                "file_list": [],
                "audio_file_list": []
            }
        }
        
        print("\n--- Testing n8n_generate_api logic ---")
        
        # Test case 1: Successful generation
        output_url = wgp.n8n_generate_api(
            prompt="test prompt",
            state=state
        )
        print(f"Returned URL: {output_url}")
        
        if "%20" not in output_url and "wan_" in output_url and ".mp4" in output_url:
             print("SUCCESS: File was renamed to clean timestamped filename (preferred behavior).")
        elif "%20" in output_url:
             print("SUCCESS: URL is encoded (acceptable fallback behavior).")
             if "test%20video%20output" in output_url:
                 print("NOTE: Renaming failed, used fallback.")
        else:
            print(f"FAILURE: URL check failed on {output_url}")

        # Test case 2: Fallback scenario (simulate copy failure)
        print("\n--- Testing Fallback Logic ---")
        # Force copy to fail by patching shutil.copy2
        with patch('shutil.copy2', side_effect=Exception("Copy failed")):
            state["gen"]["file_list"] = [] # Reset list
            output_url_fallback = wgp.n8n_generate_api(
                prompt="test prompt fallback",
                state=state
            )
            print(f"Fallback Returned URL: {output_url_fallback}")
            
            if "test%20video%20output.mp4" in output_url_fallback:
                print("SUCCESS: Fallback URL is correctly encoded.")
            else:
                print(f"FAILURE: Fallback URL is NOT correctly encoded: {output_url_fallback}")
             
    except Exception as e:
        print(f"FAILED with unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists("outputs/test video output.mp4"):
            try:
                os.remove("outputs/test video output.mp4")
            except: pass
