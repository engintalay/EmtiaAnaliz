const CACHE = 'emtia-v1';
const STATIC = ['/static/style.css'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

// Network-first: API istekleri her zaman canlı, statik dosyalar cache'den
self.addEventListener('fetch', e => {
  if (e.request.url.includes('/analyze') || e.request.url.includes('/models') || e.request.url.includes('/history')) {
    return; // API isteklerine dokunma
  }
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
