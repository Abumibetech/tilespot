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
