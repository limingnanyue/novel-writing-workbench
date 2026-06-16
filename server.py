#!/usr/bin/env python3
"""InkOS Studio v6.0 — AI Writing Workbench + Model Balance"""
import sys, os, json, datetime, uuid, shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import urllib.request

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(Path(__file__).parent / "data")))

app = FastAPI(title="InkOS Studio", version="6.6.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR.mkdir(parents=True, exist_ok=True)

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
# Model Balance (configurable)
# ═══════════════════════════════════════

BALANCE_FILE = DATA_DIR / "models.json"

@app.get("/api/models")
def list_models():
    data = _load_json(BALANCE_FILE, {"models": []})
    for m in data.get("models", []):
        m["has_key"] = bool(m.pop("api_key", ""))
    return data

class ModelInput(BaseModel):
    name: str
    base_url: str = ""
    model_id: str = ""
    api_key: str = ""
    total_credits: float = 0
    used_credits: float = 0
    expires: str = ""

@app.post("/api/models")
def add_model(req: ModelInput):
    data = _load_json(BALANCE_FILE, {"models": []})
    entry = {
        "id": uuid.uuid4().hex[:8],
        "name": req.name,
        "base_url": req.base_url,
        "model_id": req.model_id,
        "api_key": req.api_key,
        "total_credits": req.total_credits,
        "used_credits": req.used_credits,
        "expires": req.expires,
        "created": datetime.datetime.now().isoformat()
    }
    for i, m in enumerate(data.get("models", [])):
        if m.get("name") == req.name:
            entry["id"] = m.get("id", entry["id"])
            data["models"][i] = entry
            _save_json(BALANCE_FILE, data)
            # Strip api_key from response
            resp = {k: v for k, v in entry.items() if k != "api_key"}
            resp["has_key"] = bool(entry.get("api_key"))
            return {"model": resp, "updated": True}
    data.setdefault("models", []).append(entry)
    _save_json(BALANCE_FILE, data)
    resp = {k: v for k, v in entry.items() if k != "api_key"}
    resp["has_key"] = bool(entry.get("api_key"))
    return {"model": resp, "created": True}

@app.delete("/api/models/{model_id}")
def delete_model(model_id: str):
    data = _load_json(BALANCE_FILE, {"models": []})
    data["models"] = [m for m in data.get("models", []) if m.get("id") != model_id]
    _save_json(BALANCE_FILE, data)
    return {"deleted": True}

# ═══════════════════════════════════════
# AI Chat (for writing prompts)
# ═══════════════════════════════════════

class ChatInput(BaseModel):
    messages: list = []
    provider_id: str = ""

def estimate_tokens(text):
    return max(1, len(text) // 2)

@app.post("/api/chat")
def write_chat(req: ChatInput):
    models_data = _load_json(BALANCE_FILE, {"models": []})
    provider = None
    if req.provider_id:
        for m in models_data.get("models", []):
            if m.get("id") == req.provider_id:
                provider = m
                break
    if not provider:
        provider = next(iter(m.get("models", [])), None) if models_data.get("models") else None
    if not provider:
        return {"role": "assistant", "content": "⚠️ 未配置模型。请先在设置中添加模型（名称、API地址、Key、模型ID）。", "tokens": 0, "error": "no_model"}
    
    url = (provider.get("base_url", "").rstrip("/") + "/chat/completions")
    body = json.dumps({
        "model": provider.get("model_id", "gpt-3.5-turbo"),
        "messages": req.messages or [{"role": "user", "content": "Hello"}],
        "max_tokens": 4096,
        "temperature": 0.7
    }).encode()
    req_http = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider.get('api_key', '')}"
    })
    try:
        with urllib.request.urlopen(req_http, timeout=120) as resp:
            data = json.loads(resp.read())
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            tokens = estimate_tokens(content)
            # Update usage
            m = provider
            m["used_credits"] = m.get("used_credits", 0) + tokens
            _save_json(BALANCE_FILE, models_data)
            return {"role": "assistant", "content": content, "tokens": tokens, "provider": provider.get("name")}
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:500]
        return {"role": "assistant", "content": f"[API {e.code}] {err}", "tokens": 0, "error": str(err)[:200]}
    except Exception as e:
        return {"role": "assistant", "content": f"[Error] {str(e)[:200]}", "tokens": 0, "error": str(e)[:200]}

@app.post("/api/chat/stream")
async def write_chat_stream(req: ChatInput):
    models_data = _load_json(BALANCE_FILE, {"models": []})
    provider = None
    if req.provider_id:
        for m in models_data.get("models", []):
            if m.get("id") == req.provider_id:
                provider = m
                break
    if not provider:
        for m in models_data.get("models", []):
            if m.get("model_id"):
                provider = m
                break
    
    async def event_stream():
        if not provider:
            yield f"data: {json.dumps({'type':'error','content':'⚠️ 未配置模型。请先在设置中添加模型。'})}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        url = (provider.get("base_url", "").rstrip("/") + "/chat/completions")
        req_body = json.dumps({
            "model": provider.get("model_id", "gpt-3.5-turbo"),
            "messages": req.messages or [{"role": "user", "content": "Hello"}],
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": True
        }).encode()
        
        try:
            req_http = urllib.request.Request(url, data=req_body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {provider.get('api_key', '')}"
            })
            full_content = ""
            token_count = 0
            with urllib.request.urlopen(req_http, timeout=120) as resp:
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    line = line.decode('utf-8', errors='replace').strip()
                    if not line or line.startswith(':'):
                        continue
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_content += content
                                token_count += 1
                                yield f"data: {json.dumps({'type':'token','content':content,'tokens':token_count})}\n\n"
                                await asyncio.sleep(0)
                            # Check if finish_reason is set
                            finish = chunk.get('choices', [{}])[0].get('finish_reason')
                            if finish:
                                # Estimate total tokens
                                total = estimate_tokens(full_content)
                                # Update usage
                                m = provider
                                m["used_credits"] = m.get("used_credits", 0) + total
                                _save_json(BALANCE_FILE, models_data)
                                yield f"data: {json.dumps({'type':'done','content':full_content,'tokens':total,'provider':provider.get('name')})}\n\n"
                        except json.JSONDecodeError:
                            continue
            
            if not full_content:
                yield f"data: {json.dumps({'type':'error','content':'AI 返回内容为空'})}\n\n"
            yield "data: [DONE]\n\n"
            
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            yield f"data: {json.dumps({'type':'error','content':f'[API {e.code}] {err}'})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','content':f'[Error] {str(e)[:200]}'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# ═══════════════════════════════════════
# Writing / Book Management

# ═══════════════════════════════════════

WRITING_DIR = DATA_DIR / "writing"
WRITING_DIR.mkdir(parents=True, exist_ok=True)

def _get_book_dir(book_id):
    return WRITING_DIR / book_id

def _load_book_json(book_id, filename, default=None):
    return _load_json(_get_book_dir(book_id) / filename, default)

def _save_book_json(book_id, filename, data):
    d = _get_book_dir(book_id)
    d.mkdir(parents=True, exist_ok=True)
    _save_json(d / filename, data)

@app.get("/api/writing/books")
def list_books():
    books = []
    if WRITING_DIR.exists():
        for d in sorted(WRITING_DIR.iterdir(), key=lambda x: x.name, reverse=True):
            if d.is_dir():
                b = _load_json(d / "book.json", {})
                b["stats"] = _load_json(d / "stats.json", {})
                books.append(b)
    return {"books": books}

class BookInput(BaseModel):
    title: str
    genre: str = ""

@app.post("/api/writing/books")
def create_book(req: BookInput):
    bid = uuid.uuid4().hex[:10]
    now = datetime.datetime.now().isoformat()
    book = {"id": bid, "title": req.title, "genre": req.genre, "created_at": now, "updated_at": now}
    _save_book_json(bid, "book.json", book)
    _save_book_json(bid, "stats.json", {"total_words": 0, "chapter_count": 0, "character_count": 0})
    _save_book_json(bid, "outline.json", {"volumes": []})
    _save_book_json(bid, "characters.json", [])
    (_get_book_dir(bid) / "chapters").mkdir(parents=True, exist_ok=True)
    return {"book": book, "created": True}

@app.get("/api/writing/books/{book_id}")
def get_book(book_id: str):
    b = _load_book_json(book_id, "book.json")
    if not b:
        raise HTTPException(404, "Book not found")
    b["stats"] = _load_book_json(book_id, "stats.json", {})
    b["chapters"] = _list_chapters(book_id)
    b["characters"] = _load_book_json(book_id, "characters.json", [])
    b["outline"] = _load_book_json(book_id, "outline.json", {"volumes": []})
    return b

@app.delete("/api/writing/books/{book_id}")
def delete_book(book_id: str):
    d = _get_book_dir(book_id)
    if d.exists():
        shutil.rmtree(d)
    return {"deleted": True}

def _list_chapters(book_id):
    cd = _get_book_dir(book_id) / "chapters"
    if not cd.exists():
        return []
    chaps = []
    for f in sorted(cd.iterdir(), key=lambda x: x.name):
        if f.suffix == '.json':
            chaps.append(_load_json(f, {}))
    return chaps

@app.get("/api/writing/books/{book_id}/chapters")
def list_chapters(book_id: str):
    return {"chapters": _list_chapters(book_id)}

class ChapterInput(BaseModel):
    title: str = ""
    content: str = ""
    status: str = "draft"

@app.post("/api/writing/books/{book_id}/chapters")
def save_chapter(book_id: str, req: ChapterInput):
    cd = _get_book_dir(book_id) / "chapters"
    cd.mkdir(parents=True, exist_ok=True)
    cid = uuid.uuid4().hex[:8]
    chs = _list_chapters(book_id)
    ch_num = len(chs) + 1
    wc = len(req.content.replace(' ', '').replace('\n', '')) if req.content else 0
    now = datetime.datetime.now().isoformat()
    chap = {
        "id": cid, "title": req.title or f"第{ch_num}章",
        "content": req.content, "word_count": wc,
        "chapter_number": ch_num, "status": req.status,
        "created_at": now, "updated_at": now
    }
    _save_json(cd / f"{cid}.json", chap)
    chs = _list_chapters(book_id)
    stats = _load_book_json(book_id, "stats.json", {})
    stats["total_words"] = sum(c.get("word_count", 0) for c in chs)
    stats["chapter_count"] = len(chs)
    _save_book_json(book_id, "stats.json", stats)
    b = _load_book_json(book_id, "book.json", {})
    b["updated_at"] = now
    _save_book_json(book_id, "book.json", b)
    return {"chapter": chap}

@app.get("/api/writing/books/{book_id}/chapters/{chapter_id}")
def get_chapter(book_id: str, chapter_id: str):
    path = _get_book_dir(book_id) / "chapters" / f"{chapter_id}.json"
    if not path.exists():
        raise HTTPException(404, "Chapter not found")
    return _load_json(path, {})

@app.delete("/api/writing/books/{book_id}/chapters/{chapter_id}")
def delete_chapter(book_id: str, chapter_id: str):
    path = _get_book_dir(book_id) / "chapters" / f"{chapter_id}.json"
    if path.exists():
        path.unlink()
    chs = _list_chapters(book_id)
    stats = _load_book_json(book_id, "stats.json", {})
    stats["total_words"] = sum(c.get("word_count", 0) for c in chs)
    stats["chapter_count"] = len(chs)
    _save_book_json(book_id, "stats.json", stats)
    return {"deleted": True}

class CharactersInput(BaseModel):
    characters: list = []

@app.post("/api/writing/books/{book_id}/characters")
def save_characters(book_id: str, req: CharactersInput):
    _save_book_json(book_id, "characters.json", req.characters)
    stats = _load_book_json(book_id, "stats.json", {})
    stats["character_count"] = len(req.characters)
    _save_book_json(book_id, "stats.json", stats)
    return {"saved": True, "count": len(req.characters)}

class OutlineInput(BaseModel):
    volumes: list = []

@app.post("/api/writing/books/{book_id}/outline")
def save_outline(book_id: str, req: OutlineInput):
    _save_book_json(book_id, "outline.json", {"volumes": req.volumes})
    return {"saved": True, "volumes": len(req.volumes)}

# ═══════════════════════════════════════
# Frontend
# ═══════════════════════════════════════

@app.get("/")
def index():
    p = STATIC_DIR / "index.html"
    return HTMLResponse(p.read_text(encoding="utf-8") if p.exists() else "<h1>Not Found</h1>")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    print(f"\n  ✦ InkOS Studio v6.0")
    print(f"  ✦ http://{HOST}:{PORT}")
    print(f"  ✦ Data: {DATA_DIR}\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
