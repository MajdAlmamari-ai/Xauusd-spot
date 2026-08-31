const CACHE_NAME = 'gold-pwa-v1';
const urlsToCache = [
  '/Xauusd-spot/',
  '/Xauusd-spot/index.html',
  '/Xauusd-spot/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
