# WanGP API Documentation

This document outlines the API endpoints available for WanGP, including custom integrations for n8n.

## 1. Synchronous Generation (n8n Optimized)

**Endpoint:** `POST /n8n/sync`

This endpoint is specifically designed for synchronous video generation, returning a direct URL to the result once completed.

### Request Body (JSON)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `prompt` | String | **Required** | The text description of the video to generate. |
| `model_type` | String | `"Wan2.1-T2V-1.3B"` | The model ID to use for generation. |
| `resolution` | String | `"832x480"` | Output resolution (e.g., `832x480`, `480x832`). |
| `video_length` | Integer | `81` | Number of frames to generate. |
| `num_inference_steps` | Integer | `20` | Number of sampling steps. |

### Example Request (Curl)

```bash
curl -X POST "http://wan.gochapachi.com:9000/n8n/sync" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A futuristic city at sunset, cinematic lighting",
       "model_type": "Wan2.1-T2V-1.3B",
       "resolution": "832x480",
       "video_length": 81,
       "num_inference_steps": 20
     }'
```

### Response

Returns a JSON object with the public URL of the generated video.

```json
{
  "url": "http://wan.gochapachi.com:9000/outputs/wan_1740000000.mp4"
}
```

---

## 2. Static File Access

**Endpoint:** `GET /outputs/{filename}`

Directly access and download generated videos and images from the server.

### Example
`GET http://wan.gochapachi.com:9000/outputs/wan_1739962383.mp4`

---

## 3. Standard Gradio API

WanGP also supports the standard Gradio API structure.

- **Interactive Documentation:** `http://wan.gochapachi.com:9000/docs` (Swagger UI)
- **Gradio Config:** `http://wan.gochapachi.com:9000/config`

---

## Performance Notes
- **Model Loading:** Generation will be slow if the models are not yet loaded into VRAM.
- **Port:** Default port is `9000`.
- **Concurrency:** Ensure your VPS has enough VRAM if triggerring multiple requests simultaneously.

---

## 4. Get Available Models

**Endpoint:** `GET /n8n/models`

Returns a list of all available model IDs supported by the server. Use the `id` field from the response as the `model_type` in your `/n8n/sync` requests.

### Example Request

```bash
curl "http://wan.gochapachi.com:9000/n8n/models"
```

### Response

```json
{
  "models": [
    {
      "id": "Wan2.1-T2V-1.3B",
      "name": "Wan2.1-T2V-1.3B",
      "family": "wan",
      "resolution": "832x480"
    },
    {
      "id": "ltx2_distilled_gguf_q4_k_m", 
      "name": "LTX2 19B Distilled Q4_K_M",
      "family": "ltx2",
      "resolution": "768x432"
    }
  ]
}
```
