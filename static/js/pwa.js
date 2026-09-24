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

/* ============================================================
   TILESPOT_STAGE4_MOBILE_POLISH_JS
   Mobile interaction and app-feel enhancement layer.
   Existing PWA and Stage 3 logic remains untouched.
   ============================================================ */

(function () {
    "use strict";

    function initialiseStage4MobilePolish() {

        /*
         * Add a lightweight pressed state for touch devices.
         * This complements CSS :active without changing navigation.
         */
        const interactiveElements = document.querySelectorAll(
            ".tilespot-mobile-nav-item, " +
            ".tilespot-install-button, " +
            "button, " +
            "[role='button']"
        );

        interactiveElements.forEach(function (element) {

            element.addEventListener(
                "touchstart",
                function () {
                    element.classList.add("tilespot-touching");
                },
                { passive: true }
            );

            element.addEventListener(
                "touchend",
                function () {
                    element.classList.remove("tilespot-touching");
                },
                { passive: true }
            );

            element.addEventListener(
                "touchcancel",
                function () {
                    element.classList.remove("tilespot-touching");
                },
                { passive: true }
            );
        });


        /*
         * Give the mobile navigation a small visual response
         * when the user changes pages.
         */
        const mobileNav = document.getElementById(
            "tilespot-mobile-nav"
        );

        if (mobileNav) {

            const navItems = mobileNav.querySelectorAll(
                ".tilespot-mobile-nav-item"
            );

            navItems.forEach(function (item) {

                item.addEventListener("click", function () {

                    item.classList.add(
                        "tilespot-mobile-nav-clicked"
                    );

                    window.setTimeout(function () {
                        item.classList.remove(
                            "tilespot-mobile-nav-clicked"
                        );
                    }, 220);

                });

            });
        }


        /*
         * Automatically hide the install button after installation.
         * This complements the existing PWA handler without
         * replacing it.
         */
        window.addEventListener(
            "appinstalled",
            function () {

                document
                    .querySelectorAll("[data-tilespot-install]")
                    .forEach(function (button) {

                        button.classList.remove(
                            "tilespot-install-visible"
                        );

                        button.setAttribute(
                            "hidden",
                            "hidden"
                        );

                    });

            }
        );


        /*
         * Prevent accidental double-taps on the install button.
         */
        document
            .querySelectorAll("[data-tilespot-install]")
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        if (button.dataset.tilespotInstalling === "1") {
                            return;
                        }

                        button.dataset.tilespotInstalling = "1";

                        window.setTimeout(function () {
                            delete button.dataset.tilespotInstalling;
                        }, 1800);

                    }
                );

            });


        /*
         * Keep the mobile navigation above the browser gesture area.
         * CSS handles the actual safe-area spacing.
         */
        function updateMobileViewportState() {

            if (!mobileNav) {
                return;
            }

            const isMobile =
                window.matchMedia("(max-width: 768px)").matches;

            mobileNav.classList.toggle(
                "tilespot-mobile-device",
                isMobile
            );
        }

        updateMobileViewportState();

        window.addEventListener(
            "resize",
            updateMobileViewportState,
            { passive: true }
        );

    }


    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initialiseStage4MobilePolish,
            { once: true }
        );

    } else {

        initialiseStage4MobilePolish();

    }

})();

/* ============================================================
   END TILESPOT_STAGE4_MOBILE_POLISH_JS
   ============================================================ */
