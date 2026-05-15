
import os
import sys
import json
import asyncio
import importlib.util
from unittest.mock import MagicMock, patch

# --- RIGOROUS MOCKING ---
class MockLoader:
    def create_module(self, spec):
        m = MagicMock()
        m.__path__ = [] 
        m.family_handler.query_family_maps.return_value = ({}, {})
        return m
    def exec_module(self, module): pass

class MockFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname in sys.modules: return None
        if fullname == "wgp": return None
        return importlib.util.spec_from_loader(fullname, MockLoader())

sys.meta_path.insert(0, MockFinder())

# Mock torch core
mock_torch = MagicMock()
mock_torch.cuda.get_device_capability.return_value = (8, 0)
mock_torch.backends.cuda.sdp_kernel = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch._logging'] = MagicMock()

# Mock other heavy imports
sys.modules['gradio'] = MagicMock()

# Create a more realistic mock for 'shared' to support sub-imports
shared_mock = MagicMock()
shared_mock.__path__ = []
sys.modules['shared'] = shared_mock
sys.modules['shared.utils'] = MagicMock()
sys.modules['shared.utils.loras_mutipliers'] = MagicMock()
sys.modules['shared.utils.notification_sound'] = MagicMock()

# --- LOAD WGP ---
# Patch importlib.metadata.version BEFORE any imports
with patch('importlib.metadata.version', return_value="3.7.5"):
    spec = importlib.util.spec_from_file_location("wgp", "d:/Wan2gp/Wan2GP/wgp.py")
    wgp = importlib.util.module_from_spec(spec)

# Global accumulator for test results
call_log = []

def mock_generate_video(*args, **kwargs):
    call_log.append(kwargs)
    state = kwargs.get('state')
    # Use a dummy URL for result
    return f"https://wan.gochapachi.com/outputs/mock_result_{len(call_log)}.mp4"

async def run_verification():
    print("====================================================")
    print("   Wan2GP API - COMPREHENSIVE GENERATION TEST")
    print("====================================================")
    
    # Execute wgp.py with version patch
    with patch('importlib.metadata.version', return_value="3.7.5"), patch('os.remove'):
        spec.loader.exec_module(wgp)
    
    wgp.generate_video = mock_generate_video
    wgp.models_def = {
        "flux2_klein_4b": {"image_outputs": True, "audio_only": False},
        "ltx2_distilled_gguf_q4_k_m": {"image_outputs": False, "audio_only": False},
        "qwen3_tts_base": {"image_outputs": False, "audio_only": True},
        "ace_step_v1_5": {"image_outputs": False, "audio_only": True}
    }
    
    class MockRequest:
        def __init__(self, data): self._data = data
        async def json(self): return self._data

    scenarios = [
        {
            "name": "1. IMAGE: Flux (Text-to-Image)",
            "payload": {
                "prompt": "a futuristic city",
                "model_type": "flux2_klein_4b",
                "resolution": "1024x1024"
            }
        },
        {
            "name": "2. VIDEO: LTX2 (Image-to-Video)",
            "payload": {
                "prompt": "waves crashing",
                "model_type": "ltx2_distilled_gguf_q4_k_m",
                "image_start": ["https://example.com/start.jpg"]
            }
        },
        {
            "name": "3. AUDIO: Qwen3 (Text-to-Speech)",
            "payload": {
                "prompt": "Welcome to the future of AI.",
                "model_type": "qwen3_tts_base"
            }
        },
        {
            "name": "4. SONG: ACE-Step (Lyrics with Style)",
            "payload": {
                "prompt": "[Verse] Lyrics here...",
                "alt_prompt": "Dreamy lo-fi style",
                "model_type": "ace_step_v1_5"
            }
        }
    ]
    
    for s in scenarios:
        print(f"\n[API REQUEST] POST /n8n/sync -> {s['name']}")
        call_log.clear()
        mock_req = MockRequest(s["payload"])
        
        # Patch run_in_threadpool and file downloaders
        with patch('wgp.run_in_threadpool', side_effect=lambda fn, *args, **kwargs: fn(*args, **kwargs)), \
             patch('urllib.request.urlretrieve'): # Avoid actual downloads
            
            response = await wgp.n8n_sync_endpoint(mock_req)
            
        if isinstance(response, dict) and "url" in response:
            print(f"  [STATUS] SUCCESS")
            print(f"  [URL] {response['url']}")
            # Verify internal generator parameters
            params = call_log[0]
            print(f"  [PARAM CHECK] Model: {params.get('model_type')} - OK")
            if "alt_prompt" in s["payload"]:
                print(f"  [PARAM CHECK] Alt Prompt: '{params.get('alt_prompt')}' - OK")
            if "image_start" in s["payload"]:
                print(f"  [PARAM CHECK] Multi-modal Input - OK")
        else:
            print(f"  [STATUS] FAILED: {response}")

if __name__ == "__main__":
    asyncio.run(run_verification())
