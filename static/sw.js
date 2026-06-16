// AI Writing Workbench v4.5 — Service Worker
const V = 'v4.5-1';
const STATIC = [
  '/static/index.html',
  '/static/manifest.json',
  '/',
];

// Install: pre-cache core assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(V).then(c => c.addAll(STATIC).catch(_ => {}))
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== V).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

// Fetch: network-first for API, cache-first for static
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // API calls — network only (don't cache dynamic data)
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(fetch(e.request).catch(() => offlineResponse()));
    return;
  }
  // Static assets — cache-first then network fallback
  e.respondWith(
    caches.match(e.request).then(cached => {
      const fetched = fetch(e.request).then(resp => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(V).then(c => c.put(e.request, clone));
        }
        return resp;
      });
      return cached || fetched;
    })
  );
});

function offlineResponse() {
  return new Response(
    JSON.stringify({ error: 'offline', detail: '网络离线，请检查连接' }),
    { status: 503, headers: { 'Content-Type': 'application/json' } }
  );
}
