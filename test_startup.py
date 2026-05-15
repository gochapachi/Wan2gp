
import sys
print("Starting import check...")
try:
    import torch
    print(f"Torch ok: {torch.__version__}")
    import gradio
    print(f"Gradio ok: {gradio.__version__}")
    try:
        import mcp
        print(f"MCP ok: {mcp.__version__}")
    except ImportError:
        print("MCP missing!")
    
    from mmgp import offload
    print("mmgp ok")
    
    import triton
    print(f"Triton ok: {triton.__version__}")
except Exception as e:
    print(f"CRASH: {e}")
print("Done.")
