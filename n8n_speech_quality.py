"""Verify short n8n Chatterbox lines and remove material outside the requested sentence."""
import json
import pathlib
import re
import subprocess
import sys
from difflib import SequenceMatcher

import torch
import whisper


def words(value):
    return re.findall(r"[a-z0-9]+", value.lower().replace("'", ""))


def verify(source, script):
    torch.set_num_threads(2)
    model = whisper.load_model("base", device="cpu")
    result = model.transcribe(str(source), language="en", fp16=False, word_timestamps=True, verbose=False)
    observed = [word for segment in result["segments"] for word in segment.get("words", []) if words(word["word"])]
    expected = words(script)
    if not expected or not observed:
        raise ValueError("Speech verification found no requested words")
    target = "".join(expected)
    best = None
    for start in range(min(4, len(observed))):
        for end in range(start + max(1, len(expected) - 2), min(len(observed), start + len(expected) + 3) + 1):
            heard = "".join(words(" ".join(word["word"] for word in observed[start:end])))
            score = SequenceMatcher(None, target, heard).ratio()
            candidate = (score, -abs((end - start) - len(expected)), -start, start, end)
            if best is None or candidate > best:
                best = candidate
    if best is None or best[0] < 0.86:
        raise ValueError("Generated narration did not match the requested sentence: " + result["text"])
    start, end = best[-2:]
    selected = observed[start:end]
    begin = max(0.0, float(selected[0]["start"]) - 0.07)
    finish = float(selected[-1]["end"]) + 0.10
    destination = source.with_name(source.stem + "_verified.wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-ss", str(begin), "-t", str(finish - begin), "-ar", "24000", "-ac", "1", str(destination)], check=True)
    report = {"source": str(source), "output": str(destination), "expected": script, "recognized": result["text"].strip(), "selected": " ".join(word["word"].strip() for word in selected), "match_score": round(best[0], 5), "start": begin, "end": finish, "duration": finish - begin}
    destination.with_suffix(".quality.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify(pathlib.Path(sys.argv[1]), sys.argv[2]), ensure_ascii=True))
