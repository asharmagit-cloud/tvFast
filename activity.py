import os
import time
import json
import importlib
from itertools import islice

import pandas as pd
import requests

# Try to import the official Google GenAI client dynamically. If available, we'll use it instead of direct HTTP calls.
USE_GENAI_CLIENT = False
genai = None
try:
    genai = importlib.import_module("google.genai")
    USE_GENAI_CLIENT = True
except Exception:
    genai = None
    USE_GENAI_CLIENT = False

# Optional: load .env when python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Configuration
INPUT_FILE = "activity.xlsx"
OUTPUT_FILE = "categorized_activities3.xlsx"
ACTIVITY_COLUMN = "Activity"

CATEGORIES = [
    "Food", "Activities", "LocalMarkets", "Spiritual", "Historical",
    "Nature", "Cultural", "Adventure", "Others"
]

# Gemini API settings
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Batch / retry settings
BATCH_SIZE = int(os.getenv("ACTIVITY_BATCH_SIZE", "50"))
MAX_RETRIES = int(os.getenv("ACTIVITY_MAX_RETRIES", "6"))
INITIAL_BACKOFF = float(os.getenv("ACTIVITY_BACKOFF", "1.0"))  # seconds
REQUEST_TIMEOUT = float(os.getenv("ACTIVITY_REQUEST_TIMEOUT", "60"))

if not API_KEY:
    raise SystemExit(
        "GEMINI API key not found. Set GEMINI_API_KEY in the environment or create a .env file with GEMINI_API_KEY."
    )

HEADERS = {"Content-Type": "application/json"}


def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def extract_json_from_text(text):
    """
    Find the first JSON object or array in `text` and return it as a substring.
    Uses a small stack-based parser to find the matching closing brace/bracket so we don't rely on brittle regex.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    start = None
    for idx, ch in enumerate(text):
        if ch in ('{', '['):
            start = idx
            break
    if start is None:
        raise ValueError("No JSON object or array start found in text")

    pairs = {'{': '}', '[': ']'}
    stack = []
    for i in range(start, len(text)):
        c = text[i]
        if c in pairs:
            stack.append(pairs[c])
        elif c in (']', '}'):
            if not stack:
                # stray closing - continue searching
                continue
            expected = stack.pop()
            if c != expected:
                # mismatched closing, this indicates malformed JSON; continue trying
                continue
            if not stack:
                # found matching end
                return text[start:i + 1]

    raise ValueError("No complete JSON object/array found in text")


def call_api_with_retry(payload):
    """
    Wrapper that prefers the official google-genai client when available.
    If not available, uses the previous HTTP POST approach.
    Payload shape for HTTP path: the same JSON we used earlier.
    For the genai client, we will pass the prompt text extracted from payload.
    """
    # If genai client is available, try using it first
    if USE_GENAI_CLIENT:
        try:
            # create client; client loads credentials from environment (GOOGLE_API_KEY / ADC)
            client = genai.Client()
            # extract the prompt text from our payload structure
            # payload is expected to be: {"contents":[{"parts":[{"text": prompt_text}]}]}
            try:
                prompt_text = payload["contents"][0]["parts"][0]["text"]
            except Exception:
                # fallback: if payload is already a string
                prompt_text = payload if isinstance(payload, str) else ""

            # call the model via the client
            # wrap in retry loop similar to HTTP path to handle rate limits
            backoff = INITIAL_BACKOFF
            last_exc = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[{"type": "input_text", "text": prompt_text}],
                    )
                    # the client returns a response object; convert to a JSON-like dict similar to the HTTP path
                    # response.candidates is a list-like; each candidate has .content.parts[].text
                    # We'll build a compatible structure so the rest of the code can reuse it.
                    candidates = []
                    for cand in getattr(response, "candidates", []) or []:
                        # each candidate may have 'content' with 'parts'
                        content = {"parts": []}
                        for part in getattr(cand, "content", {}).get("parts", []) if hasattr(cand, "content") else []:
                            content["parts"].append({"text": getattr(part, "text", "")})
                        candidates.append({"content": content})

                    # If client response doesn't match, try to extract text directly from response
                    if not candidates:
                        # attempt to access response.text if available
                        txt = getattr(response, "text", None) or getattr(response, "output", None)
                        if isinstance(txt, str):
                            return {"candidates": [{"content": {"parts": [{"text": txt}]}}]}

                    return {"candidates": candidates}
                except Exception as e:
                    last_exc = e
                    # genai client will raise errors for rate limits; implement exponential backoff
                    time.sleep(backoff)
                    backoff *= 2
                    continue
            # if we exhausted retries using genai client, raise the last exception so caller can fallback
            raise last_exc
        except Exception:
            # fall back to HTTP below
            pass

    # Existing HTTP path (unchanged behavior)
    backoff = INITIAL_BACKOFF
    last_status = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(f"{API_URL}?key={API_KEY}", headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            # network-level error: retry
            last_status = None
            if attempt == MAX_RETRIES:
                raise
            time.sleep(backoff)
            backoff *= 2
            continue

        last_status = resp.status_code
        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            try:
                wait = float(retry_after) if retry_after and retry_after.isdigit() else backoff
            except Exception:
                wait = backoff
            time.sleep(wait)
            backoff *= 2
            continue

        # Retry on 5xx
        if 500 <= resp.status_code < 600:
            time.sleep(backoff)
            backoff *= 2
            continue

        # non-retryable
        resp.raise_for_status()

    raise RuntimeError(f"Exceeded retries calling Gemini API (last status {last_status})")


def build_prompt_for_batch(batch_activities):
    numbered = "\n".join(f"{i}. {act}" for i, act in enumerate(batch_activities))
    categories_line = ", ".join(CATEGORIES)
    prompt = (
        "You are given a numbered list of activities. For each activity return a JSON array of objects "
        "with fields: index (the input index), category (one of the allowed categories), and label (original activity). "
        "If activity doesn't clearly match any category, use 'Others'. Respond with ONLY valid JSON (no explanation).\n\n"
        f"Allowed categories: {categories_line}\n\n"
        "Input activities:\n" + numbered + "\n\n"
        "Example output format:\n"
        "[{\"index\":0,\"category\":\"Food\",\"label\":\"Street food stall\"}, {\"index\":1,\"category\":\"Historical\",\"label\":\"Old fort\"}]"
    )
    return prompt


def classify_batch(batch_activities):
    prompt = build_prompt_for_batch(batch_activities)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    result = call_api_with_retry(payload)

    # extract reply text robustly
    try:
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError("Unexpected Gemini response structure") from e

    json_text = extract_json_from_text(reply)
    return json.loads(json_text)


def classify_single(activity):
    prompt = (
        f"Categorize the following activity into one of: {', '.join(CATEGORIES)}.\n"
        f"Return a JSON object with fields: category and label (original). If none match, return category 'Others'.\n\nActivity: {activity}\n"
        "Respond with only JSON."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    result = call_api_with_retry(payload)
    try:
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "Others"

    try:
        json_text = extract_json_from_text(reply)
        obj = json.loads(json_text)
        cat = obj.get("category") if isinstance(obj, dict) else None
        if isinstance(cat, str):
            matched = next((c for c in CATEGORIES if c.lower() == cat.strip().lower()), None)
            return matched if matched else "Others"
    except Exception:
        # fallback: simple heuristic
        for c in CATEGORIES:
            if c.lower() in reply.lower():
                return c
    return "Others"


def main():
    df = pd.read_excel(INPUT_FILE)
    if ACTIVITY_COLUMN not in df.columns:
        raise SystemExit(f"Activity column '{ACTIVITY_COLUMN}' not found in {INPUT_FILE}")

    activities = df[ACTIVITY_COLUMN].fillna("").astype(str).tolist()
    categories_out = ["Others"] * len(activities)

    for batch_index, batch in enumerate(chunked_iterable(activities, BATCH_SIZE)):
        base_index = batch_index * BATCH_SIZE
        print(f"Classifying batch {batch_index + 1} (items {base_index}..{base_index + len(batch) - 1})")
        try:
            mapped = classify_batch(batch)
        except Exception as e:
            print(f"Batch {batch_index + 1} failed: {e}. Falling back to single-item classification.")
            # fallback per-item to be resilient to batch parsing issues
            for i, act in enumerate(batch):
                try:
                    categories_out[base_index + i] = classify_single(act)
                except Exception as e2:
                    print(f"  Single classify failed for index {base_index + i}: {e2}. Marking 'Others'.")
                    categories_out[base_index + i] = "Others"
            # small pause to avoid immediate re-rate limit
            time.sleep(1)
            continue

        # mapped expected to be a list of objects with 'index' and 'category'
        for item in mapped:
            try:
                rel_idx = int(item.get("index", 0))
                global_idx = base_index + rel_idx
                cat = item.get("category", "Others")
                if isinstance(cat, str):
                    matched = next((c for c in CATEGORIES if c.lower() == cat.strip().lower()), None)
                    categories_out[global_idx] = matched if matched else "Others"
                else:
                    categories_out[global_idx] = "Others"
            except Exception as e:
                print(f"  Skipping item from model due to parsing error: {e} -> {item}")

        # polite pause between batches
        time.sleep(0.5)

    df["Category"] = categories_out
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Categorized Excel file saved as '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
