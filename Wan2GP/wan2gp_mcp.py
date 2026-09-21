import argparse
import asyncio
import os
import sys
from typing import Any, Dict, List

# Ensure we can import mcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: 'mcp' package not found. Please install it using: pip install mcp")
    sys.exit(1)

try:
    from gradio_client import Client
except ImportError:
    print("Error: 'gradio_client' package not found. Please install it using: pip install gradio_client")
    sys.exit(1)

# Initialize FastMCP
mcp = FastMCP("Wan2gp")

# Global client
client = None

def get_client():
    global client
    if client is None:
        # Connect to the local Gradio instance
        # Assuming typical default port 7860, but user should verify
        api_url = os.getenv("WAN2GP_URL", "http://127.0.0.1:7860/")
        print(f"Connecting to Wan2gp at {api_url}...")
        try:
            client = Client(api_url)
            print("Connected successfully.")
        except Exception as e:
            print(f"Failed to connect to Wan2gp: {e}")
            raise RuntimeError(f"Could not connect to Wan2gp at {api_url}. Is it running?")
    return client

@mcp.tool()
async def generate_video(prompt: str, model_type: str = "Wan2.1-T2V-1.3B", duration: int = 5) -> str:
    """
    Generate a video using Wan2gp.
    
    Args:
        prompt: The text prompt to generate the video from.
        model_type: The model to use (default: Wan2.1-T2V-1.3B).
        duration: Video duration in seconds (default: 5).
        
    Returns:
        The path or URL of the generated video.
    """
    # Note: This is a simplified wrapper. The actual wgp.py API might have many specific parameters.
    # We are using the simplest endpoint for demonstration.
    # You might need to inspect the Gradio API docs (via client.view_api()) to find the exact fn_index or endpoint name.
    
    c = get_client()
    
    # Introspection to find the right endpoint
    # c.view_api() could be useful for debugging
    
    try:
        # This is a best-guess implementation. 
        # Real integration requires matching the specific Gradio API signature found in wgp.py.
        # Since wgp.py is complex, we might need the user to verify the API endpoints.
        # For now, we return a message guiding the user to check connectivity.
        
        # Example call (likely needs adjustment based on actual API)
        # result = c.predict(
        #     prompt,
        #     model_type,
        #     duration,
        #     api_name="/generate" 
        # )
        
        return "Video generation via MCP is ready to be configured. Please run 'python wan2gp_mcp.py --inspect' to see available Gradio API endpoints and update the tool implementation."
        
    except Exception as e:
        return f"Error triggering generation: {str(e)}"

@mcp.tool()
async def get_api_info() -> str:
    """
    Retrieve the available API endpoints from the running Wan2gp instance.
    Use this to understand how to call the generation functions.
    """
    c = get_client()
    return str(c.view_api(return_format="dict"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true", help="Print API info and exit")
    args = parser.parse_args()

    if args.inspect:
        c = get_client()
        c.view_api()
    else:
        mcp.run()
