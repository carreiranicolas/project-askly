(() => {
  const prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const page = document.getElementById("askly-page");
  if (!page) return;

  if (prefersReducedMotion) {
    page.classList.add("askly-page--ready");
    return;
  }

  // Fade in on load
  requestAnimationFrame(() => {
    page.classList.add("askly-page--ready");
  });

  function isModifiedClick(e) {
    return e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0;
  }

  function sameOrigin(url) {
    try {
      return new URL(url, window.location.href).origin === window.location.origin;
    } catch {
      return false;
    }
  }

  function shouldHandleLink(a, e) {
    if (!a) return false;
    if (a.hasAttribute("download")) return false;
    if (a.getAttribute("target") && a.getAttribute("target") !== "_self") return false;
    if (a.getAttribute("rel") && a.getAttribute("rel").includes("external")) return false;
    if (a.dataset.noTransition !== undefined) return false;
    if (isModifiedClick(e)) return false;

    const href = a.getAttribute("href");
    if (!href || href.startsWith("#")) return false;
    if (href.startsWith("mailto:") || href.startsWith("tel:")) return false;
    if (!sameOrigin(href)) return false;

    return true;
  }

  document.addEventListener("click", (e) => {
    const a = e.target && e.target.closest ? e.target.closest("a") : null;
    if (!shouldHandleLink(a, e)) return;

    e.preventDefault();
    const href = a.href;

    // Fade out then navigate
    page.classList.add("askly-page--leaving");
    window.setTimeout(() => {
      window.location.assign(href);
    }, 160);
  });

  // On back/forward cache restore, ensure ready state
  window.addEventListener("pageshow", (event) => {
    page.classList.remove("askly-page--leaving");
    page.classList.add("askly-page--ready");
  });
})();

