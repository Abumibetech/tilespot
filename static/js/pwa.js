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



/* TILESPOT_STAGE3_MOBILE_NAV_JS */

(function () {
    "use strict";

    /*
    ========================================================
    TILESPOT MOBILE NAVIGATION
    ========================================================
    */

    function initialiseTilespotMobileNavigation() {

        const navigation = document.getElementById(
            "tilespot-mobile-nav"
        );

        if (!navigation) {
            return;
        }

        const items = navigation.querySelectorAll(
            ".tilespot-mobile-nav-item"
        );

        if (!items.length) {
            return;
        }

        /*
        ----------------------------------------------------
        CURRENT PAGE DETECTION
        ----------------------------------------------------
        */

        const currentPath =
            window.location.pathname
                .replace(/\/+$/, "") || "/";

        items.forEach(function (item) {

            const href = item.getAttribute("href");

            if (!href) {
                return;
            }

            try {

                const linkUrl = new URL(
                    href,
                    window.location.origin
                );

                const linkPath =
                    linkUrl.pathname
                        .replace(/\/+$/, "") || "/";

                if (
                    linkPath === currentPath ||
                    (
                        linkPath !== "/" &&
                        currentPath.startsWith(
                            linkPath + "/"
                        )
                    )
                ) {
                    item.classList.add(
                        "tilespot-mobile-active"
                    );

                    item.setAttribute(
                        "aria-current",
                        "page"
                    );
                }

            } catch (error) {
                /*
                 Ignore malformed/relative URLs.
                Existing navigation remains functional.
                */
            }
        });

        /*
        ----------------------------------------------------
        TOUCH FEEDBACK
        ----------------------------------------------------
        */

        items.forEach(function (item) {

            item.addEventListener(
                "touchstart",
                function () {
                    item.classList.add(
                        "tilespot-mobile-touching"
                    );
                },
                { passive: true }
            );

            item.addEventListener(
                "touchend",
                function () {
                    window.setTimeout(
                        function () {
                            item.classList.remove(
                                "tilespot-mobile-touching"
                            );
                        },
                        100
                    );
                },
                { passive: true }
            );

        });

    }

    /*
    --------------------------------------------------------
    DOM READY
    --------------------------------------------------------
    */

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initialiseTilespotMobileNavigation
        );

    } else {

        initialiseTilespotMobileNavigation();

    }

})();

/* END TILESPOT_STAGE3_MOBILE_NAV_JS */
