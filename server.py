#!/usr/bin/env python3
"""
LLM Gateway Dashboard v5.2
手机端模型+写作面板 · 多提供商 · 连接测试 · 余额查询 · 模型列表 · AI对话
"""
import sys, os, json, re, datetime, uuid, subprocess, urllib.request
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(Path(__file__).parent / "data")))

app = FastAPI(title="LLM Gateway Dashboard", version="5.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PROVIDERS_FILE = DATA_DIR / "providers.json"
TOKEN_FILE = DATA_DIR / "token_usage.json"

# ═══════════════════════════════════════
# Data helpers
# ═══════════════════════════════════════

def _load_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else (default or {})
    except:
        return default or {}

def _save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ═══════════════════════════════════════
# Provider Management
# ═══════════════════════════════════════

def get_providers():
    return _load_json(PROVIDERS_FILE, {"providers": []})

def save_providers(data):
    _save_json(PROVIDERS_FILE, data)

# ═══════════════════════════════════════
# Token Tracking
# ═══════════════════════════════════════

def get_token_usage():
    return _load_json(TOKEN_FILE, {"total_tokens": 0, "total_requests": 0, "total_tests": 0, "by_provider": {}})

def add_token_usage(tokens, provider_name="", req_type="chat"):
    data = get_token_usage()
    data["total_tokens"] = data.get("total_tokens", 0) + tokens
    data["total_requests"] = data.get("total_requests", 0) + 1
    if req_type == "test":
        data["total_tests"] = data.get("total_tests", 0) + 1
    if provider_name:
        bp = data.setdefault("by_provider", {})
        bp[provider_name] = bp.get(provider_name, 0) + tokens
    _save_json(TOKEN_FILE, data)
    return data

def estimate_tokens(text):
    return max(1, len(text) // 2)

# ═══════════════════════════════════════
# AI Call
# ═══════════════════════════════════════

def call_llm(provider, messages, max_tokens=256):
    """Generic OpenAI-compatible API call."""
    url = (provider.get("base_url", "").rstrip("/") + "/chat/completions")
    body = json.dumps({
        "model": provider.get("model", "gpt-3.5-turbo"),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider.get('api_key', '')}"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        raise HTTPException(e.code, f"API {e.code}: {err_body}")
    except Exception as e:
        raise HTTPException(500, str(e)[:200])

def test_connection(provider):
    """Test provider connection by listing models."""
    url = (provider.get("base_url", "").rstrip("/") + "/models")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {provider.get('api_key', '')}"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            models = []
            for m in data.get("data", []):
                mid = m.get("id", "")
                if mid and not mid.startswith("ft:") and "audio" not in mid.lower() and "tts" not in mid.lower() and "whisper" not in mid.lower() and "dall" not in mid.lower() and "moderation" not in mid.lower():
                    models.append({"id": mid, "owned_by": m.get("owned_by", "")})
            return {
                "connected": True,
                "models": models[:80],
                "model_count": len(models),
                "provider_info": data.get("object", "unknown")
            }
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:300]
        return {"connected": False, "error": f"HTTP {e.code}", "detail": err}
    except Exception as e:
        return {"connected": False, "error": str(e)[:200]}

def check_balance(provider):
    """Check account balance/credits by making a minimal API call."""
    # Try /dashboard/billing/usage or /usage endpoint
    base = provider.get("base_url", "").rstrip("/")
    
    # Method 1: OpenAI-style billing
    for endpoint in ["/dashboard/billing/subscription", "/v1/dashboard/billing/subscription"]:
        try:
            url = base + endpoint
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {provider.get('api_key', '')}"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return {
                    "source": "billing_api",
                    "has_payment_method": data.get("has_payment_method", False),
                    "hard_limit_usd": data.get("hard_limit_usd", 0),
                    "soft_limit_usd": data.get("soft_limit_usd", 0),
                    "system_hard_limit_usd": data.get("system_hard_limit_usd", 0),
                    "access_until": data.get("access_until", None),
                    "raw": data
                }
        except:
            continue
    
    # Method 2: Try /v1/usage for usage-based providers
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        url = base + f"/v1/usage?date={today}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {provider.get('api_key', '')}"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                "source": "usage_api",
                "total_usage": data.get("total_usage", 0) / 100,
                "daily_costs": data.get("daily_costs", []),
                "raw": data
            }
    except:
        pass
    
    # Method 3: Minimal chat call to verify credits are available
    try:
        resp = call_llm(provider, [{"role": "user", "content": "hi"}], max_tokens=5)
        return {"source": "test_call", "credits_available": True, "test_response": resp[:100]}
    except HTTPException as e:
        if "insufficient" in str(e.detail).lower() or "quota" in str(e.detail).lower() or "billing" in str(e.detail).lower():
            return {"source": "test_call", "credits_available": False, "error": str(e.detail)[:200]}
        return {"source": "test_call", "credits_available": None, "error": str(e.detail)[:200]}
    except:
        return {"source": "none", "credits_available": None, "note": "Provider doesn't support balance queries"}

# ═══════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════

class ProviderInput(BaseModel):
    name: str
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"

class ChatInput(BaseModel):
    messages: list = []
    provider_id: str = ""

# ═══════════════════════════════════════
# API: Health & Stats
# ═══════════════════════════════════════

@app.get("/api/health")
def health():
    provs = get_providers()
    tc = get_token_usage()
    total_models = sum(len(p.get("cached_models", [])) for p in provs.get("providers", []))
    return {
        "ready": True,
        "version": "5.1.0",
        "host": HOST,
        "port": PORT,
        "providers_count": len(provs.get("providers", [])),
        "models_count": total_models,
        "total_tokens": tc.get("total_tokens", 0),
        "total_requests": tc.get("total_requests", 0),
        "total_tests": tc.get("total_tests", 0),
    }

@app.get("/api/tokens")
def tokens():
    return get_token_usage()

@app.post("/api/tokens/reset")
def reset_tokens():
    _save_json(TOKEN_FILE, {"total_tokens": 0, "total_requests": 0, "total_tests": 0, "by_provider": {}})
    return {"reset": True}

# ═══════════════════════════════════════
# API: Providers CRUD
# ═══════════════════════════════════════

@app.get("/api/providers")
def list_providers():
    provs = get_providers()
    # Strip api_key from response
    result = []
    for p in provs.get("providers", []):
        p2 = {k: v for k, v in p.items() if k != "api_key"}
        p2["has_key"] = bool(p.get("api_key"))
        result.append(p2)
    return {"providers": result, "count": len(result)}

@app.post("/api/providers")
def add_provider(req: ProviderInput):
    provs = get_providers()
    pid = uuid.uuid4().hex[:12]
    entry = {
        "id": pid,
        "name": req.name,
        "base_url": req.base_url,
        "api_key": req.api_key,
        "model": req.model,
        "cached_models": [],
        "last_test": None,
        "created": datetime.datetime.now().isoformat()
    }
    # Check for existing + update
    for i, p in enumerate(provs.get("providers", [])):
        if p.get("name") == req.name or p.get("base_url") == req.base_url:
            entry["id"] = p.get("id", pid)
            provs["providers"][i] = entry
            save_providers(provs)
            return {"provider": {k: v for k, v in entry.items() if k != "api_key"}, "updated": True}
    
    provs.setdefault("providers", []).append(entry)
    save_providers(provs)
    return {"provider": {k: v for k, v in entry.items() if k != "api_key"}, "created": True}

@app.delete("/api/providers/{provider_id}")
def delete_provider(provider_id: str):
    provs = get_providers()
    provs["providers"] = [p for p in provs.get("providers", []) if p.get("id") != provider_id]
    save_providers(provs)
    return {"deleted": True}

# ═══════════════════════════════════════
# API: Model Operations
# ═══════════════════════════════════════

@app.post("/api/providers/{provider_id}/test")
def test_provider(provider_id: str):
    provs = get_providers()
    for p in provs.get("providers", []):
        if p.get("id") == provider_id:
            result = test_connection(p)
            # Cache models if connected
            if result.get("connected") and result.get("models"):
                p["cached_models"] = result["models"]
                p["model_count"] = result.get("model_count", 0)
                p["last_test"] = datetime.datetime.now().isoformat()
                save_providers(provs)
            add_token_usage(0, p.get("name", ""), "test")
            return result
    raise HTTPException(404, "Provider not found")

@app.get("/api/providers/{provider_id}/models")
def list_models(provider_id: str):
    provs = get_providers()
    for p in provs.get("providers", []):
        if p.get("id") == provider_id:
            cached = p.get("cached_models", [])
            return {
                "provider_id": provider_id,
                "provider_name": p.get("name"),
                "models": cached,
                "count": len(cached),
                "cached": True,
                "last_test": p.get("last_test"),
            }
    raise HTTPException(404, "Provider not found")

@app.post("/api/providers/{provider_id}/balance")
def provider_balance(provider_id: str):
    provs = get_providers()
    for p in provs.get("providers", []):
        if p.get("id") == provider_id:
            result = check_balance(p)
            add_token_usage(0, p.get("name", ""), "test")
            return result
    raise HTTPException(404, "Provider not found")

# ═══════════════════════════════════════
# API: Chat / Test
# ═══════════════════════════════════════

@app.post("/api/chat")
def chat(req: ChatInput):
    provs = get_providers()
    provider = None
    if req.provider_id:
        for p in provs.get("providers", []):
            if p.get("id") == req.provider_id:
                provider = p
                break
    if not provider:
        provider = provs.get("providers", [{}])[0] if provs.get("providers") else None
    
    if not provider:
        raise HTTPException(400, "No provider configured")
    
    messages = req.messages or [{"role": "user", "content": "Hello"}]
    try:
        content = call_llm(provider, messages)
        tokens = estimate_tokens(content)
        add_token_usage(tokens, provider.get("name", ""), "chat")
        return {"role": "assistant", "content": content, "tokens": tokens, "provider": provider.get("name")}
    except HTTPException as he:
        return {"role": "assistant", "content": f"[API Error: {he.detail}]", "tokens": 0, "error": str(he.detail)[:200]}
    except Exception as e:
        return {"role": "assistant", "content": f"[Error: {str(e)[:100]}]", "tokens": 0, "error": str(e)[:200]}

# ═══════════════════════════════════════
# Frontend
# ═══════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def index():
    p = STATIC_DIR / "index.html"
    return HTMLResponse(p.read_text(encoding="utf-8") if p.exists() else "<h1>Not Found</h1>")

if __name__ == "__main__":
    import uvicorn
    print(f"\n  LLM Gateway Dashboard v5.2")
    print(f"  http://{HOST}:{PORT}")
    print(f"  Data: {DATA_DIR}\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
