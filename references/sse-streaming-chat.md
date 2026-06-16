# SSE Streaming Chat — FastAPI + JS Frontend Pattern

> Server-Sent Events for real-time AI chat with token counting.
> Used in InkOS Studio v6.6 for live-streaming writing responses.

## Backend: FastAPI SSE Endpoint

```python
@app.post("/api/chat/stream")
async def chat_stream(req: ChatInput):
    # Resolve provider/model from config
    models_data = _load_json("models.json", {"models": []})
    provider = find_provider(models_data, req.provider_id)
    
    async def event_stream():
        if not provider:
            yield f"data: {json.dumps({'type':'error','content':'No model configured'})}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # Call API with stream=True
        req_body = json.dumps({
            "model": provider.get("model_id"),
            "messages": req.messages,
            "stream": True
        }).encode()
        
        try:
            req_http = urllib.request.Request(url, data=req_body, headers={...})
            full_content = ""
            token_count = 0
            
            with urllib.request.urlopen(req_http, timeout=120) as resp:
                while True:
                    line = resp.readline()
                    if not line: break
                    line = line.decode().strip()
                    if not line or line.startswith(':'): continue
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]': break
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content += content
                            token_count += 1
                            yield f"data: {json.dumps({'type':'token','content':content,'tokens':token_count})}\n\n"
                            await asyncio.sleep(0)  # yield control
                        
                        finish = chunk.get('choices', [{}])[0].get('finish_reason')
                        if finish:
                            total = estimate_tokens(full_content)
                            yield f"data: {json.dumps({'type':'done','content':full_content,'tokens':total})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            yield f"data: {json.dumps({'type':'error','content':str(err)})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','content':str(e)[:200]})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### Key Requirements
- `async def` handler (FastAPI) — need `import asyncio`
- `yield` in async generator — need `async def event_stream()`
- `await asyncio.sleep(0)` — yields control to event loop between tokens
- `StreamingResponse` — wraps async generator
- `media_type="text/event-stream"` — sets correct Content-Type
- Each event: `data: <json>\n\n` (double newline terminates event)
- Stream end: `data: [DONE]\n\n`

### Provider Resolver Strategy
1. Try exact `provider_id` match from request
2. Fallback to first model with non-empty `model_id`
3. If none: return error event

## Frontend: JS SSE Consumer

```javascript
async function sendChat() {
  // ... setup messages, user bubble etc.
  
  // 1. Create placeholder bubble
  am.innerHTML = '<div class="m-bub streaming" id="streamBub">▍</div>' +
    '<div class="m-time">12:30 <span class="tk-counter" id="tkCounter">⚡0</span></div>';
  
  // 2. SSE fetch
  let resp = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({messages, provider_id})
  });
  
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  
  // 3. Read stream
  let reader = resp.body.getReader();
  let decoder = new TextDecoder();
  let fullContent = '';
  let buffer = '';
  
  while (true) {
    let {done, value} = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, {stream: true});
    let lines = buffer.split('\n');
    buffer = lines.pop() || '';
    
    for (let line of lines) {
      line = line.trim();
      if (!line || line === 'data: [DONE]') continue;
      if (line.startsWith('data: ')) {
        let evt = JSON.parse(line.slice(6));
        if (evt.type === 'token') {
          fullContent += evt.content;
          bub.innerHTML = escapeHtml(fullContent) + '▍';
          tkCounter.textContent = '⚡' + evt.tokens;
        } else if (evt.type === 'done') {
          bub.innerHTML = escapeHtml(evt.content);
          bub.classList.remove('streaming');
          tkCounter.textContent = '⚡' + evt.tokens;
        }
      }
    }
  }
}
```

### Key Requirements
- `resp.body.getReader()` — ReadableStream API (modern browsers only)
- `TextDecoder('utf-8', {stream: true})` — handles multi-byte char splits
- Buffer management: accumulate partial lines, split on `\n`
- No `response.json()` — that waits for entire body
- CSS `border-left: 2px solid var(--primary)` on `.streaming` class
- `blinky` animation on the cursor: `@keyframes blinky { 0%,100%{opacity:1} 50%{opacity:0} }`

## Event Types

| type | payload | When |
|------|---------|------|
| `token` | `{content, tokens}` | Every streamed token (token_count increments) |
| `done` | `{content, tokens, provider}` | finish_reason received |
| `error` | `{content}` | Any error (model config, API error) |
| `[DONE]` | (raw string) | Stream terminated (final marker) |

## Live Token Counter UI

```html
<span class="tk-counter">⚡0</span>
```
```css
.tk-counter {
  font-size: .35rem;
  color: var(--accent);
  font-family: var(--font-mono);
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--secondary);
}
```

- Updates on each `type: "token"` event
- Final count from `type: "done"` event
- Display in message timestamp area: `12:30 ⚡892`

## Error Handling Pattern

- Backend never throws HTTP errors — always returns SSE error event
- Frontend catches `HTTP !ok` (network errors), shows ❌ message
- No model configured → error event with helpful text
- API call fails → error event with truncated error text
