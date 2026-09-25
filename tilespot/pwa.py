from django.http import JsonResponse, HttpResponse


def manifest(request):
    return JsonResponse({
        "name": "Tilespot — Nigeria's Modern Tile Marketplace",
        "short_name": "Tilespot",
        "description": "Discover, compare and buy tiles from sellers across Nigeria.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#0b1714",
        "theme_color": "#0b1714",
        "icons": [
            {
                "src": "/static/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/static/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    })


def service_worker(request):
    javascript = r'''
const CACHE_NAME = "tilespot-static-v2";

self.addEventListener("install", event => {
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    if (url.origin !== self.location.origin) {
        return;
    }

    if (!url.pathname.startsWith("/static/")) {
        return;
    }

    event.respondWith(
        caches.match(request).then(cached => {
            if (cached) {
                return cached;
            }

            return fetch(request).then(response => {
                if (!response || response.status !== 200) {
                    return response;
                }

                const copy = response.clone();

                caches.open(CACHE_NAME).then(cache => {
                    cache.put(request, copy);
                });

                return response;
            });
        })
    );
});
'''

    return HttpResponse(
        javascript,
        content_type="application/javascript"
    )
