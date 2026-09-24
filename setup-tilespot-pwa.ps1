$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       TILESPOT PWA SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path ".\static\css" | Out-Null
New-Item -ItemType Directory -Force -Path ".\static\js" | Out-Null
New-Item -ItemType Directory -Force -Path ".\static\images" | Out-Null

@"
{
    "name": "Tilespot - Nigerian Tile Marketplace",
    "short_name": "Tilespot",
    "description": "Find, compare and buy tiles from sellers across Nigeria.",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#071019",
    "theme_color": "#071019",
    "lang": "en-NG",
    "categories": ["shopping", "business", "marketplace"],
    "icons": [
        {
            "src": "/static/images/tilespot-icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}
"@ | Set-Content ".\static\manifest.json" -Encoding UTF8

@"
const CACHE_NAME = "tilespot-pwa-v1";

const APP_SHELL = [
    "/",
    "/tiles/",
    "/static/manifest.json"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(APP_SHELL))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {
    if (event.request.method !== "GET") return;

    const url = new URL(event.request.url);

    if (url.origin !== self.location.origin) return;

    const protectedPaths = [
        "/login/",
        "/logout/",
        "/register/",
        "/dashboard/",
        "/profile/",
        "/messages/",
        "/notifications/",
        "/sell/",
        "/admin/"
    ];

    if (protectedPaths.some(path => url.pathname.startsWith(path))) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (
                    response &&
                    response.status === 200 &&
                    response.type === "basic"
                ) {
                    const copy = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => cache.put(event.request, copy));
                }

                return response;
            })
            .catch(() =>
                caches.match(event.request)
                    .then(cached => cached || caches.match("/"))
            )
    );
});
"@ | Set-Content ".\static\service-worker.js" -Encoding UTF8

@"
(function () {
    "use strict";

    let deferredPrompt = null;

    if ("serviceWorker" in navigator) {
        window.addEventListener("load", function () {
            navigator.serviceWorker
                .register("/static/service-worker.js")
                .then(function (registration) {
                    console.log(
                        "Tilespot service worker registered:",
                        registration.scope
                    );
                })
                .catch(function (error) {
                    console.error(
                        "Tilespot service worker registration failed:",
                        error
                    );
                });
        });
    }

    window.addEventListener("beforeinstallprompt", function (event) {
        event.preventDefault();
        deferredPrompt = event;

        document.dispatchEvent(
            new CustomEvent("tilespot:installavailable")
        );
    });

    window.TilespotPWA = {
        canInstall: function () {
            return deferredPrompt !== null;
        },

        install: async function () {
            if (!deferredPrompt) return false;

            deferredPrompt.prompt();

            const result = await deferredPrompt.userChoice;

            deferredPrompt = null;

            document.dispatchEvent(
                new CustomEvent("tilespot:installed", {
                    detail: result
                })
            );

            return result;
        }
    };

    window.addEventListener("appinstalled", function () {
        deferredPrompt = null;
        console.log("Tilespot was installed.");
    });
})();
"@ | Set-Content ".\static\js\pwa.js" -Encoding UTF8

@"
html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}

body {
    overscroll-behavior-y: contain;
    -webkit-tap-highlight-color: transparent;
}

button,
a,
input,
select,
textarea {
    touch-action: manipulation;
}

button,
.btn,
a.btn {
    min-height: 44px;
}

@media (max-width: 768px) {
    body {
        padding-bottom: 76px;
    }

    input,
    select,
    textarea {
        font-size: 16px !important;
    }

    button,
    .btn {
        min-height: 46px;
    }

    img {
        max-width: 100%;
        height: auto;
    }
}

@media (display-mode: standalone) {
    body {
        overscroll-behavior-y: none;
    }
}

.tilespot-install-button {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: 0;
    border-radius: 12px;
    padding: 12px 18px;
    background: #00c2ff;
    color: #071019;
    font-weight: 800;
    cursor: pointer;
}

.tilespot-install-button.tilespot-install-visible {
    display: inline-flex;
}

@media (max-width: 768px) {
    .tilespot-mobile-nav {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        min-height: 64px;
        padding: 8px 10px calc(8px + env(safe-area-inset-bottom));
        background: rgba(7, 16, 25, 0.97);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        display: flex;
        align-items: center;
        justify-content: space-around;
    }

    .tilespot-mobile-nav a {
        min-width: 58px;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 3px;
        color: rgba(255, 255, 255, 0.65);
        text-decoration: none;
        font-size: 11px;
        font-weight: 700;
        border-radius: 12px;
    }

    .tilespot-mobile-nav a:hover,
    .tilespot-mobile-nav a.active {
        color: #00f5d4;
    }

    .tilespot-mobile-nav .nav-icon {
        font-size: 21px;
        line-height: 1;
    }
}
"@ | Set-Content ".\static\css\pwa.css" -Encoding UTF8

@"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
    <rect width="512" height="512" rx="110" fill="#071019"/>
    <rect x="80" y="80" width="352" height="352" rx="70" fill="#00c2ff"/>
    <path d="M128 128h256v256H128z" fill="#071019"/>
    <path d="M160 160h88v88h-88zM264 160h88v88h-88zM160 264h88v88h-88zM264 264h88v88h-88z" fill="#00f5d4"/>
    <path d="M204 204h104v104H204z" fill="#071019"/>
</svg>
"@ | Set-Content ".\static\images\tilespot-icon.svg" -Encoding UTF8

Write-Host ""
Write-Host "PWA files created successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Created:" -ForegroundColor Yellow
Write-Host "  static\manifest.json"
Write-Host "  static\service-worker.js"
Write-Host "  static\js\pwa.js"
Write-Host "  static\css\pwa.css"
Write-Host "  static\images\tilespot-icon.svg"
Write-Host ""
Write-Host "Next: we will connect these files to your existing base.html." -ForegroundColor Cyan
