// Service Worker for Greek News Analyzer PWA
const CACHE_NAME = 'greek-news-analyzer-v2';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-72x72.png',
  '/static/icons/icon-96x96.png',
  '/static/icons/icon-128x128.png',
  '/static/icons/icon-144x144.png',
  '/static/icons/icon-152x152.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-384x384.png',
  '/static/icons/icon-512x512.png'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Handle share target
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SHARE_TARGET') {
    const { title, text, url } = event.data;
    
    // Store shared data for the main app to use
    self.registration.showNotification('Greek News Analyzer', {
      body: `Analyzing: ${title || text || url}`,
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-72x72.png',
      tag: 'news-analysis',
      data: { title, text, url }
    });
  }
});

// Handle share target from form submission
self.addEventListener('fetch', (event) => {
  if (event.request.method === 'GET' && event.request.url.includes('?')) {
    const url = new URL(event.request.url);
    const title = url.searchParams.get('title');
    const text = url.searchParams.get('text');
    const sharedUrl = url.searchParams.get('url');
    
    if (title || text || sharedUrl) {
      // Store the shared data and redirect to main app
      event.respondWith(
        caches.open('shared-data').then(cache => {
          return cache.put('shared-data', new Response(JSON.stringify({
            title, text, url: sharedUrl
          })));
        }).then(() => {
          return Response.redirect('/', 302);
        })
      );
    }
  }
});

// Handle protocol handlers (web+greeknews://)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'PROTOCOL_HANDLER') {
    const { url } = event.data;
    
    // Open the app with the URL parameter
    self.clients.openWindow(`/?url=${encodeURIComponent(url)}`);
  }
});

// Background sync for offline analysis
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Handle any pending analysis requests
  console.log('Background sync triggered');
}
