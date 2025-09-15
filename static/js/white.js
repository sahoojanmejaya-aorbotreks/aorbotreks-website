document.addEventListener("DOMContentLoaded", function () {
    const overlay = document.getElementById("page-transition");

    // Show overlay when clicking links
    document.querySelectorAll("a[href]").forEach(link => {
      // Skip links like #, javascript:void(0), or external links
      if (
        link.getAttribute("href").startsWith("#") ||
        link.getAttribute("href").startsWith("javascript:") ||
        link.target === "_blank"
      ) return;

      link.addEventListener("click", function (e) {
        overlay.classList.add("active");
      });
    });

    // Hide overlay once page fully loads
    window.addEventListener("pageshow", function () {
      overlay.classList.remove("active");
    });
  });