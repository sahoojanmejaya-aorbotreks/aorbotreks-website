

(function () {
  // helper: set cookie (days optional)
  function setCookie(name, value, days) {
    let expires = "";
    if (typeof days === "number") {
      const d = new Date();
      d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
      expires = "; expires=" + d.toUTCString();
    }
    document.cookie =
      name + "=" + encodeURIComponent(value) + expires + "; path=/; SameSite=Lax";
  }

  // helper: get cookie
  function getCookie(name) {
    const match = document.cookie
      .split("; ")
      .find((row) => row.startsWith(name + "="));
    return match ? decodeURIComponent(match.split("=")[1]) : null;
  }

  // helper: delete cookie
  function deleteCookie(name) {
    document.cookie = name + "=; Max-Age=0; path=/; SameSite=Lax";
  }

  // unified save (cookie + localStorage)
  function saveConsent(value) {
    // 10 years cookie
    setCookie("cookiesAccepted", value, 3650);
    // also localStorage
    localStorage.setItem("cookiesAccepted", value);
  }

  // unified load (check both cookie & localStorage)
  function loadConsent() {
    let value = getCookie("cookiesAccepted");
    if (value === null) {
      value = localStorage.getItem("cookiesAccepted");
      if (value !== null) {
        // re-sync cookie if only localStorage exists
        setCookie("cookiesAccepted", value, 3650);
      }
    } else {
      // sync localStorage if only cookie exists
      localStorage.setItem("cookiesAccepted", value);
    }
    return value; // "true", "false", or null
  }

  // Example functions to enable/disable third-party scripts
  function enableThirdParty() {
    if (!window.__aorbo_analytics_loaded) {
      const gaId = "G-XXXXXXXXXX"; // replace with your real GA ID
      if (gaId && gaId.indexOf("G-") === 0) {
        const s = document.createElement("script");
        s.src = "https://www.googletagmanager.com/gtag/js?id=" + gaId;
        s.async = true;
        document.head.appendChild(s);

        window.dataLayer = window.dataLayer || [];
        function gtag() {
          window.dataLayer.push(arguments);
        }
        window.gtag = gtag;
        gtag("js", new Date());
        gtag("config", gaId);
      }
      window.__aorbo_analytics_loaded = true;
    }
  }

  function disableThirdParty() {
    deleteCookie("_ga");
    deleteCookie("_gid");
    deleteCookie("_gat");
    window.__aorbo_analytics_loaded = false;
  }

  // DOM ready
  document.addEventListener("DOMContentLoaded", function () {
    const banner = document.getElementById("cookie-banner");
    const acceptBtn = document.getElementById("accept-cookies");
    const declineBtn = document.getElementById("decline-cookies");

    if (!banner) return;

    const consent = loadConsent(); // check cookie + localStorage

    if (consent === null) {
      banner.classList.remove("d-none"); // show banner first-time
    } else {
      if (consent === "true") {
        enableThirdParty();
      } else {
        disableThirdParty();
      }
    }

    // Accept
    if (acceptBtn) {
      acceptBtn.addEventListener("click", function () {
        saveConsent("true");
        banner.classList.add("d-none");
        enableThirdParty();
      });
    }

    // Decline
    if (declineBtn) {
      declineBtn.addEventListener("click", function () {
        saveConsent("false");
        banner.classList.add("d-none");
        disableThirdParty();
      });
    }

    // Optional: Esc key closes banner
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        banner.classList.add("d-none");
      }
    });
  });
})();