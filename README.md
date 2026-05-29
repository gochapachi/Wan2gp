# Wan2GP — Custom Fork with n8n API Integration

> **Fork of [deepbeepmeep/Wan2GP](https://github.com/deepbeepmeep/Wan2GP)** with custom n8n/REST API endpoints, VPS tunnel support, and remote generation capabilities.

For the full upstream documentation, see [Wan2GP/README.md](Wan2GP/README.md).

---

## 🚀 What This Fork Adds

- **REST API Endpoints** — Generate videos/images/audio programmatically via HTTP
- **n8n Integration** — Purpose-built sync endpoint for [n8n](https://n8n.io) workflow automation
- **VPS Tunnel Support** — Cloudflared and FRP tunnel scripts for remote access
- **FastAPI + Uvicorn** — Production-grade ASGI server replacing default Gradio launcher
- **Static File Serving** — Direct download of generated outputs via `/outputs/` URL path

---

## 📡 API Endpoints

The API server starts automatically when you launch `wgp.py`. By default it listens on `0.0.0.0:7860`.

### `GET /n8n/models` — List Available Models

Returns all loaded generative models.

**Request:**
```bash
curl http://localhost:7860/n8n/models
```

**Response:**
```json
{
  "models": [
    {
      "id": "Wan2.1-T2V-1.3B",
      "name": "Wan 2.1 Text to Video 1.3B",
      "family": "wan",
      "resolution": "832x480"
    },
    {
      "id": "LTX2-22B-Distilled",
      "name": "LTX-2.3 22B Distilled",
      "family": "ltx2",
      "resolution": "unknown"
    }
  ]
}
```

---

### `POST /n8n/sync` — Generate Video/Image/Audio (Synchronous)

The main generation endpoint. Sends a generation request and waits for the result. Supports idempotency via `request_id`.

**Request:**
```bash
curl -X POST http://localhost:7860/n8n/sync \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A serene mountain lake at sunrise with mist rising from the water",
    "model_type": "Wan2.1-T2V-1.3B",
    "resolution": "832x480",
    "video_length": 81,
    "num_inference_steps": 20
  }'
```

**Response (success):**
```json
{
  "url": "https://your-server.com/outputs/wan_1748550000_1234.mp4"
}
```

**Response (error):**
```json
{
  "error": "Generation failed: Model not found"
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | **(required)** | Text description for generation |
| `model_type` | string | `"Wan2.1-T2V-1.3B"` | Model ID (get valid IDs from `/n8n/models`) |
| `resolution` | string | `"832x480"` | Output resolution (`WIDTHxHEIGHT`) |
| `video_length` | int | `81` | Number of frames to generate |
| `num_inference_steps` | int | `20` | Sampling steps (higher = better quality, slower) |
| `request_id` | string | *(auto-generated)* | Idempotency key for retry deduplication |
| `alt_prompt` | string | `""` | Alternative/negative prompt |
| `image_start` | string | `null` | URL or path to start image (for image-to-video) |
| `image_end` | string | `null` | URL or path to end image |
| `image_refs` | array | `null` | Reference images (URLs or paths) |
| `video_source` | string | `null` | URL or path to source video |
| `audio_guide` | string | `null` | URL or path to audio guide |
| `audio_guide2` | string | `null` | URL or path to second audio guide |
| `image_prompt_type` | string | `"Image Prompt"` | Image input mode |
| `video_prompt_type` | string | `"Video Prompt"` | Video input mode |
| `audio_prompt_type` | string | `"Audio Prompt"` | Audio input mode |

#### Idempotency & Caching

- **With `request_id`**: If you provide a `request_id`, the server caches the result for 30 minutes. Retrying with the same `request_id` returns the cached result without re-generating.
- **Without `request_id`**: Each request generates fresh content (no caching).
- **Concurrent requests**: If a request with the same `request_id` is already running, subsequent requests will wait for it to complete rather than starting a new generation.

#### File Inputs

File parameters (`image_start`, `video_source`, `audio_guide`, etc.) accept:
- **URLs** — The server downloads the file automatically  
- **Local file paths** — If the file exists on the server's filesystem

---

### `GET /outputs/{filename}` — Download Generated Files

Serves generated files directly via HTTP. The URL is returned by the `/n8n/sync` endpoint.

```bash
curl -O http://localhost:7860/outputs/wan_1748550000_1234.mp4
```

---

### Gradio Web UI — `GET /`

The standard WanGP web interface is available at the root URL, mounted on top of the FastAPI server.

```
http://localhost:7860/
```

---

## 🔗 n8n Workflow Integration

### Basic n8n HTTP Request Node Configuration

1. **Add an HTTP Request node** in your n8n workflow
2. Configure it as follows:

| Setting | Value |
|---------|-------|
| Method | `POST` |
| URL | `http://your-server:7860/n8n/sync` |
| Body Content Type | `JSON` |
| Body | See example below |

**Body JSON:**
```json
{
  "prompt": "{{ $json.prompt }}",
  "model_type": "Wan2.1-T2V-1.3B",
  "resolution": "832x480",
  "video_length": 81,
  "num_inference_steps": 20,
  "request_id": "{{ $json.id }}"
}
```

### n8n Expression Handling

The API automatically handles common n8n expression quirks:
- **Leading `=` signs** in keys/values are stripped (n8n sometimes prepends these)
- **`parameters` array format** is automatically flattened to a simple key-value object
- **String numbers** for `video_length` and `num_inference_steps` are auto-converted to integers

### Timeout Configuration

Video generation can take several minutes depending on model, resolution, and hardware. Configure your n8n HTTP Request node with a generous timeout:

| Setting | Recommended Value |
|---------|------------------|
| Timeout | `600000` (10 minutes) |
| Retry on Fail | `true` |
| Max Retries | `2` |

> **Tip:** Use the `request_id` parameter when retrying to avoid duplicate generations.

---

## 🖥️ VPS Deployment

This fork includes scripts for remote VPS access:

| File | Purpose |
|------|---------|
| `start_wan2gp.bat` | Start WanGP locally |
| `start_wan2gp_vps.bat` | Start with FRP tunnel to VPS |
| `start_wan2gp_cloudflared.bat` | Start with Cloudflare tunnel |
| `frpc.toml` | FRP client configuration |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | `7860` | Server listen port |
| `N8N_OUTPUT_URL_BASE` | `https://wan.gochapachi.com` | Base URL for output file URLs |

---

## ⚙️ Setup

```bash
# Clone this fork
git clone https://github.com/gochapachi/Wan2gp.git
cd Wan2gp/Wan2GP

# Follow standard WanGP installation
conda create -n wan2gp python=3.11.14
conda activate wan2gp
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt

# Additional dependencies for API server
pip install fastapi uvicorn

# Run
python wgp.py --listen
```

---

## 📂 Repository Structure

```
Wan2gp/
├── Wan2GP/                  # Upstream WanGP (submodule tracking deepbeepmeep/Wan2GP)
│   ├── wgp.py               # Main app with n8n API integration
│   ├── models/               # Model definitions and handlers
│   ├── plugins/              # WanGP plugins
│   └── ...
├── start_wan2gp.bat          # Local launch script
├── start_wan2gp_vps.bat      # VPS tunnel launch script
├── start_wan2gp_cloudflared.bat  # Cloudflare tunnel launch
├── frpc.toml                 # FRP tunnel config
├── vps/                      # VPS deployment configs
└── README.md                 # This file
```

---

## 🔄 Upstream Sync

This fork tracks the upstream [deepbeepmeep/Wan2GP](https://github.com/deepbeepmeep/Wan2GP) repository. To update:

```bash
cd Wan2GP
git pull origin main
cd ..
git add -A
git commit -m "Sync upstream Wan2GP"
git push
```

---

## 📜 License

This project inherits the license from the upstream [Wan2GP](https://github.com/deepbeepmeep/Wan2GP) project. API integration code is provided as-is for personal and research use.
