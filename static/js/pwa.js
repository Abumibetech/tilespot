(function () {
    "use strict";

    let deferredPrompt = null;

    function showInstallButton() {
        document
            .querySelectorAll("[data-tilespot-install]")
            .forEach(function (button) {
                button.classList.add("tilespot-install-visible");
                button.removeAttribute("hidden");
            });
    }

    function hideInstallButton() {
        document
            .querySelectorAll("[data-tilespot-install]")
            .forEach(function (button) {
                button.classList.remove("tilespot-install-visible");
                button.setAttribute("hidden", "hidden");
            });
    }

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

        showInstallButton();
    });

    window.TilespotPWA = {
        canInstall: function () {
            return deferredPrompt !== null;
        },

        install: async function () {
            if (!deferredPrompt) {
                return false;
            }

            deferredPrompt.prompt();

            const result = await deferredPrompt.userChoice;

            deferredPrompt = null;

            if (result && result.outcome === "accepted") {
                hideInstallButton();
            }

            document.dispatchEvent(
                new CustomEvent("tilespot:installed", {
                    detail: result
                })
            );

            return result;
        }
    };

    document.addEventListener(
        "tilespot:installavailable",
        function () {
            showInstallButton();
        }
    );

    document.addEventListener(
        "click",
        function (event) {
            const button = event.target.closest(
                "[data-tilespot-install]"
            );

            if (!button) {
                return;
            }

            event.preventDefault();

            if (
                window.TilespotPWA &&
                window.TilespotPWA.canInstall()
            ) {
                window.TilespotPWA.install();
            }
        }
    );

    window.addEventListener("appinstalled", function () {
        deferredPrompt = null;
        hideInstallButton();

        console.log("Tilespot was installed.");
    });
})();
