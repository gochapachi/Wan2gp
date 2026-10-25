# WanGP / Wan2GP API Documentation

Cloud Online URL: `https://wan.anagataitsolutions.in`

---

## 1. Quick Summary of Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `https://wan.anagataitsolutions.in/n8n/sync`<br>`https://wan.anagataitsolutions.in/api/n8n/generate` | `POST` | Synchronously generate video, image, or audio and return public URL |
| `https://wan.anagataitsolutions.in/n8n/health`<br>`https://wan.anagataitsolutions.in/api/n8n/health` | `GET` | Health check and version status |
| `https://wan.anagataitsolutions.in/n8n/models`<br>`https://wan.anagataitsolutions.in/api/n8n/models` | `GET` | Retrieve list of all available models and their IDs |
| `https://wan.anagataitsolutions.in/outputs/{filename}` | `GET` | Access generated MP4, PNG, FLAC, or WAV media |

---

## 2. Generating with MiniMax H3 FastH3 Omni 8-Step (Using Custom Assets as References)

### Model Overview
* **Model ID:** `minimax_h3_fasth3_omni` (or NVFP4: `minimax_h3_fasth3_omni_nvfp4`)
* **Architecture:** MiniMax H3 Ref2VA Pruned 20B (FastVideo 8-Step Distillation)
* **Sampling Solver:** `euler` (fixed 8 steps)
* **Flow Shift:** `12.0`
* **Frames / Duration:** `124` frames at `24` FPS (~5.16 seconds per window)
* **Supported Resolutions:** `832x480` (Landscape 16:9), `480x832` (Portrait 9:16), `1280x720` (HD Landscape), `720x1280` (HD Portrait)
* **Native Output:** Synchronized video + 32 kHz stereo audio generated jointly from your prompt and reference assets.

---

### How Custom Asset References Work

FastH3 Omni utilizes the **Ref2VA** (Reference-to-Video-and-Audio) conditioning branch:
1. **Reference Images (`image_refs`)**:
   Pass a list of direct image URLs (PNG, JPEG, WebP) or paths:
   ```json
   "image_refs": [
     "https://your-domain.com/character_face.png",
     "https://your-domain.com/outfit_or_prop.png"
   ]
   ```
2. **Video Prompt Type (`video_prompt_type`)**:
   Set to `"I"` (Image reference mode).
3. **Prompt Notation**:
   FastH3 Omni references the items in `image_refs` in order:
   * First image in `image_refs` = `<Picture 1>`
   * Second image in `image_refs` = `<Picture 2>`
   * Third image in `image_refs` = `<Picture 3>`
4. **Structured Ref2VA Prompt Format (Recommended for Best Quality)**:
   ```text
   subject_definitions: <Subject 1> is the character from <Picture 1>.
   summary: [reference generation] The referenced character walks through a sunlit pine forest.
   retention_analysis: <Subject 1> (appears in [Shot 1]): fully_preserved - retain facial features, hairstyle, and outfit.
   detailed_description: [Shot 1] <Subject 1> walks slowly towards the camera, looks around in awe, and smiles. Golden sunlight filters through tree branches. Smooth tracking shot at eye level.
   overall_soundscape: Birds chirping, footsteps crunching dry leaves and pine needles, gentle wind breeze.
   non_diegetic_music: N/A
   ```

---

### Request Payload Specification

| Field | Type | Required | Recommended Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| `model_type` | string | **Yes** | `"minimax_h3_fasth3_omni"` | Model identifier |
| `prompt` | string | **Yes** | *See prompt format above* | Narrative description referencing `<Picture 1>` etc. |
| `image_refs` | array[string] | **Yes** | `["https://.../asset1.png"]` | Public URLs or paths to reference images |
| `video_prompt_type` | string | Optional | `"I"` | Set to `"I"` for Reference Image mode |
| `resolution` | string | Optional | `"832x480"` | `"832x480"`, `"480x832"`, `"1280x720"`, `"720x1280"` |
| `video_length` | integer | Optional | `124` | 124 frames = ~5.16s at 24 FPS |
| `num_inference_steps`| integer | Optional | `8` | 8 steps for FastH3 Omni |
| `request_id` | string | Optional | UUID string | Optional idempotency/cache key |

---

### cURL Example

```bash
curl -X POST "https://wan.anagataitsolutions.in/n8n/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "minimax_h3_fasth3_omni",
    "prompt": "subject_definitions: <Subject 1> is the character from <Picture 1>.\nsummary: The referenced character walks in a vibrant neon cyberpunk city street at night.\nretention_analysis: <Subject 1>: fully_preserved.\ndetailed_description: [Shot 1] <Subject 1> walks forward through rain-slicked asphalt reflecting vivid purple and cyan holograms, turns their head towards the camera with a calm, confident gaze. Steady tracking camera moving backward.\noverall_soundscape: Distant traffic hum, light rain falling on puddles, footsteps.",
    "resolution": "832x480",
    "video_length": 124,
    "num_inference_steps": 8,
    "video_prompt_type": "I",
    "image_refs": [
      "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600"
    ]
  }'
```

### Response
```json
{
  "url": "https://wan.anagataitsolutions.in/outputs/wan_1792925161_9952.mp4"
}
```

---

### Python Example

```python
import requests

ENDPOINT = "https://wan.anagataitsolutions.in/n8n/sync"

payload = {
    "model_type": "minimax_h3_fasth3_omni",
    "prompt": (
        "subject_definitions: <Subject 1> is the character from <Picture 1>.\n"
        "summary: The character stands in an elegant modern art gallery.\n"
        "retention_analysis: <Subject 1>: fully_preserved - preserve identity and face.\n"
        "detailed_description: [Shot 1] <Subject 1> stands admiring a sculpture, turns to look at the viewer with a thoughtful smile. Camera pans slowly around them in soft museum lighting.\n"
        "overall_soundscape: Quiet indoor ambience, soft echo of footsteps on polished stone.\n"
        "non_diegetic_music: N/A"
    ),
    "resolution": "832x480",
    "video_length": 124,
    "num_inference_steps": 8,
    "video_prompt_type": "I",
    "image_refs": [
        "https://your-public-cdn.com/assets/character_portrait.png"
    ]
}

response = requests.post(ENDPOINT, json=payload, timeout=300)
response.raise_for_status()

result = response.json()
print("Generated Video URL:", result["url"])
```

---

### n8n Node Configuration
1. **Node**: **HTTP Request**
2. **Method**: `POST`
3. **URL**: `https://wan.anagataitsolutions.in/n8n/sync` (or `/api/n8n/generate`)
4. **Send Body**: `JSON`
5. **Specify Body**: `Using JSON`
6. **JSON**:
```json
{
  "model_type": "minimax_h3_fasth3_omni",
  "prompt": "subject_definitions: <Subject 1> is the character from <Picture 1>.\nsummary: The referenced character explores an ancient temple.\nretention_analysis: <Subject 1>: fully_preserved.\ndetailed_description: [Shot 1] <Subject 1> walks among sun-drenched stone pillars, running hand along ancient carvings with an amazed expression.\noverall_soundscape: Desert wind whistling through stone corridors, rustling clothes.",
  "resolution": "832x480",
  "video_length": 124,
  "num_inference_steps": 8,
  "video_prompt_type": "I",
  "image_refs": [
    "{{ $json.character_image_url }}"
  ]
}
```
7. Output expression in subsequent nodes: `{{ $json.url }}`
