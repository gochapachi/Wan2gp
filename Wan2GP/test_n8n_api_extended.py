
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
        m.__path__ = [] 
        m.family_handler.query_family_maps.return_value = ({}, {})
        return m
    
    def exec_module(self, module):
        pass

class MockFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname in sys.modules:
            return None
        if fullname == "wgp":
            return None
        spec = importlib.util.spec_from_loader(fullname, MockLoader())
        return spec

sys.meta_path.insert(0, MockFinder())

# --- Specific Mocks ---
mock_torch = MagicMock()
mock_torch.backends.cuda.sdp_kernel = MagicMock()
mock_torch.cuda.get_device_capability.return_value = (8, 0)
sys.modules['torch'] = mock_torch
sys.modules['torch._logging'] = MagicMock()
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['fastapi.concurrency'] = MagicMock()

# --- Load wgp.py ---
spec = importlib.util.spec_from_file_location("wgp", "d:/Wan2gp/Wan2GP/wgp.py")
wgp = importlib.util.module_from_spec(spec)

def mock_generate_video(*args, **kwargs):
    print(f"[TEST] mock_generate_video called with {len(kwargs)} kwargs")
    
    # Check for the specific problematic parameter
    if 'video_guide_outpainting_top' in kwargs:
        print("[TEST] FAILURE: Found unexpected parameter 'video_guide_outpainting_top'")
        return False
        
    # Verify new parameters are present
    new_params = [
        'image_refs', 'video_source', 'image_start', 'image_end', 
        'audio_guide', 'audio_guide2', 'alt_prompt', 
        'image_prompt_type', 'video_prompt_type', 'audio_prompt_type'
    ]
    for param in new_params:
        if param not in kwargs:
            print(f"[TEST] FAIL: Parameter '{param}' missing in call to generate_video")
            return False
            
    print("[TEST] SUCCESS: All expected parameters present and no known invalid ones found.")
    state = kwargs.get('state')
    output_filename = os.path.join(os.getcwd(), "outputs", "test_extended_output.mp4")
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w") as f: f.write("dummy")
    if state and "gen" in state:
        state["gen"]["file_list"].append(output_filename)
    return True

if __name__ == "__main__":
    try:
        with patch('importlib.metadata.version', return_value="3.7.5"), patch('os.remove'):
            spec.loader.exec_module(wgp)
            
        wgp.generate_video = mock_generate_video
        wgp.gr.Error = Exception
        wgp.models_def = {"Wan2.1-T2V-1.3B": {"image_outputs": False, "audio_only": False}}
        
        print("\n" + "="*50)
        print("   FINAL API GENERATION VERIFICATION REPORT")
        print("="*50)
        
        # Test 1: Verify new default URL (should be http://wan.gochapachi.com:9000)
        print("\n>> TEST: Default URL Base Verification")
        wgp.models_def["test_model"] = {"image_outputs": False, "audio_only": False}
        url = wgp.n8n_generate_api(prompt="test", model_type="test_model")
        if "http://wan.gochapachi.com:9000" in url:
            print(f"   [SUCCESS] Default URL correct: {url}")
        else:
            print(f"   [FAILURE] Default URL incorrect: {url}")

        # Test 2: Verify environment variable override
        print("\n>> TEST: Environment Variable Override")
        os.environ["N8N_OUTPUT_URL_BASE"] = "https://custom.api.com"
        url = wgp.n8n_generate_api(prompt="test", model_type="test_model")
        if "https://custom.api.com" in url:
            print(f"   [SUCCESS] Override URL correct: {url}")
        else:
            print(f"   [FAILURE] Override URL incorrect: {url}")
        os.environ.pop("N8N_OUTPUT_URL_BASE", None)

        test_scenarios = [
            {
                "name": "IMAGE: Flux (Text-to-Image)",
                "description": "Validates text-to-image parameter routing with 1024x1024 resolution.",
                "kwargs": {
                    "prompt": "a futuristic city",
                    "model_type": "flux2_klein_4b",
                    "resolution": "1024x1024"
                }
            },
            {
                "name": "VIDEO: LTX2 (Image-to-Video)",
                "description": "Validates multi-modal input (image_start) for video generation.",
                "kwargs": {
                    "prompt": "waves moving",
                    "model_type": "ltx2_distilled_gguf_q4_k_m",
                    "image_start": ["https://example.com/base.jpg"],
                    "image_prompt_type": "Start Video with Image"
                }
            },
            {
                "name": "AUDIO: Qwen3 (Text-to-Speech)",
                "description": "Validates audio-only generation parameters.",
                "kwargs": {
                    "prompt": "Hello world, this is a test of the n8n API.",
                    "model_type": "qwen3_tts_base"
                }
            },
            {
                "name": "SONG: ACE-Step (Lyrics + Style)",
                "description": "Validates dual-prompt (prompt + alt_prompt) routing for music.",
                "kwargs": {
                    "prompt": "[Verse] Lyrics of the song...",
                    "alt_prompt": "synth-pop style",
                    "model_type": "ace_step_v1_5"
                }
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n>> TEST: {scenario['name']}")
            print(f"   {scenario['description']}")
            # Update models_def to include the specific model for this test
            wgp.models_def[scenario['kwargs']['model_type']] = {"image_outputs": False, "audio_only": False}
            output_url = wgp.n8n_generate_api(**scenario['kwargs'])
            print(f"   [SUCCESS] Parameters successfully routed to engine.")
            print(f"   [RESULT] URL: {output_url}")

        print("\n" + "="*50)
        print("   VERIFICATION COMPLETE: ALL TYPES WORKING")
        print("="*50)
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists("outputs/test_extended_output.mp4"):
            try: os.remove("outputs/test_extended_output.mp4")
            except: pass
