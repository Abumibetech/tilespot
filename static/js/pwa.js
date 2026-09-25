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

/* =========================================================
   TILESPOT_STAGE5D_MOBILE_TOUCH_JS
   ========================================================= */

(function () {
    "use strict";

    if (window.matchMedia("(max-width: 600px)").matches) {

        document.addEventListener("touchstart", function (event) {

            const card = event.target.closest(".tilecard");

            if (!card) {
                return;
            }

            card.classList.add("tilespot-touching");

        }, { passive: true });

        document.addEventListener("touchend", function (event) {

            const card = event.target.closest(".tilecard");

            if (!card) {
                return;
            }

            window.setTimeout(function () {
                card.classList.remove("tilespot-touching");
            }, 120);

        }, { passive: true });

        document.addEventListener("touchcancel", function (event) {

            const card = event.target.closest(".tilecard");

            if (!card) {
                return;
            }

            card.classList.remove("tilespot-touching");

        }, { passive: true });
    }

})();

/* END TILESPOT_STAGE5D_MOBILE_TOUCH_JS */


/* =========================================================
   TILESPOT_STAGE5F_MOBILE_NAV_POLISH_JS
   ========================================================= */

(function () {
    "use strict";

    function updateTilespotStandaloneClass() {
        const standalone =
            window.matchMedia &&
            window.matchMedia("(display-mode: standalone)").matches;

        if (standalone) {
            document.body.classList.add("tilespot-standalone");
        } else {
            document.body.classList.remove("tilespot-standalone");
        }
    }

    function markCurrentNavigationItem() {
        const nav = document.getElementById("tilespot-mobile-nav");

        if (!nav) {
            return;
        }

        const currentPath =
            window.location.pathname.replace(/\/+$/, "") || "/";

        nav.querySelectorAll("a[data-nav-name]").forEach(function (link) {

            const linkPath =
                new URL(link.href, window.location.origin)
                    .pathname
                    .replace(/\/+$/, "") || "/";

            const isHome =
                linkPath === "/" && currentPath === "/";

            const isMatch =
                linkPath !== "/" &&
                currentPath === linkPath;

            if (isHome || isMatch) {
                link.classList.add("is-current");
                link.setAttribute("aria-current", "page");
            } else {
                link.classList.remove("is-current");
                link.removeAttribute("aria-current");
            }

        });
    }

    function initTilespotMobileNavigation() {
        updateTilespotStandaloneClass();
        markCurrentNavigationItem();

        window.addEventListener("pageshow", markCurrentNavigationItem);

        window.addEventListener("resize", function () {
            updateTilespotStandaloneClass();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initTilespotMobileNavigation
        );
    } else {
        initTilespotMobileNavigation();
    }

})();

/* END TILESPOT_STAGE5F_MOBILE_NAV_POLISH_JS */


/* ============================================================
   TILESPOT_MOBILE_FINAL_UPGRADE_JS

   Final mobile/app interaction layer.
   Additive only.
   ============================================================ */

(function () {

    "use strict";


    function isMobileViewport() {

        return window.matchMedia(
            "(max-width: 900px)"
        ).matches;
    }


    function setupMobileInteractionLayer() {

        if (!document.body) {
            return;
        }


        document.body.classList.toggle(
            "tilespot-mobile",
            isMobileViewport()
        );


        /*
         * Mobile touch feedback
         */

        var selectors = [
            ".btn",
            ".btnbtn-dark",
            "button",
            ".contactpill",
            ".tilecard a",
            ".tilecard button",
            ".mobile-nav-item",
            "#tilespot-mobile-nav a"
        ];


        var elements = document.querySelectorAll(
            selectors.join(",")
        );


        elements.forEach(function (element) {

            if (
                element.dataset.tilespotFinalTouchBound === "1"
            ) {
                return;
            }


            element.dataset.tilespotFinalTouchBound = "1";


            element.addEventListener(
                "touchstart",
                function () {

                    element.classList.add(
                        "tilespot-final-pressed"
                    );

                },
                {
                    passive: true
                }
            );


            element.addEventListener(
                "touchend",
                function () {

                    window.setTimeout(
                        function () {

                            element.classList.remove(
                                "tilespot-final-pressed"
                            );

                        },
                        80
                    );

                },
                {
                    passive: true
                }
            );


            element.addEventListener(
                "touchcancel",
                function () {

                    element.classList.remove(
                        "tilespot-final-pressed"
                    );

                },
                {
                    passive: true
                }
            );

        });

    }


    /*
     * Recalculate mobile state when screen size changes.
     */

    window.addEventListener(
        "resize",
        setupMobileInteractionLayer,
        {
            passive: true
        }
    );


    window.addEventListener(
        "pageshow",
        setupMobileInteractionLayer
    );


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            setupMobileInteractionLayer
        );

    } else {

        setupMobileInteractionLayer();

    }


    /*
     * Browser back/forward navigation.
     */

    window.addEventListener(
        "popstate",
        function () {

            window.setTimeout(
                setupMobileInteractionLayer,
                50
            );

        }
    );


    /*
     * App ready marker.
     */

    function markAppReady() {

        if (!document.body) {
            return;
        }


        document.body.classList.add(
            "tilespot-app-ready"
        );

    }


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            markAppReady
        );

    } else {

        markAppReady();

    }

})();


/* END TILESPOT_MOBILE_FINAL_UPGRADE_JS */
