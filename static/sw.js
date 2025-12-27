const CACHE_NAME = 'gym-manager-v4';
const urlsToCache = [
    '/',
    '/static/icon.png',
    '/static/offline-db.js',
    '/dashboard',
    '/add_member',
    '/static/style.css',
    '/static/css/mobile.min.css',
    '/static/css/loading.css',
    '/static/js/mobile.js',
    '/static/js/animations.js',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch Strategy: Network First, fallback to Cache
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Clone the response
                const responseClone = response.clone();

                // Cache the fetched response
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseClone);
                });

                return response;
            })
            .catch(() => {
                // If network fails, try cache
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            return response;
                        }

                        // If not in cache, return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match('/dashboard');
                        }
                    });
            })
    );
});
