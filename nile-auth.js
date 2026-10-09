// 📌 PATH: nile-auth.js
// 📌 PURPOSE: One shared, localStorage-backed phone+token store so logging
//             in on any ONDA Nile admin page is good on every other page
//             too — instead of each page trusting only whatever token got
//             frozen into its own URL whenever it first loaded. Also keeps
//             Xano's own copy of magic_auth_token_expiry rolling forward
//             while someone's actually using the site (not just has a tab
//             open), via a throttled call to /nile/auth/touch — David +
//             Ray Deck's "active session never times out, an idle one
//             does" model. Built 2026-10-09; touch endpoint confirmed live
//             the same day, 24h rolling window.
//
// Usage, on every page that currently reads ?phone=&token= itself:
//   <script src="../nile-auth.js"></script>
//   const resolved = OndaNileAuth.resolveAuth(urlPhone, urlToken);
//   // use resolved.phone / resolved.token in place of the raw URL values
//   OndaNileAuth.startActivityTouch(resolved.phone, resolved.token);
//   // after a fresh OTP verification succeeds elsewhere on the page:
//   OndaNileAuth.saveAuth(newPhone, newToken);

(function (global) {
  const STORAGE_KEY = 'onda_nile_auth';
  const TOUCH_URL = 'https://xrxm-29on-xlyt.n7e.xano.io/api:nile/auth/touch';
  const TOUCH_MIN_INTERVAL_MS = 5 * 60 * 1000; // at most once per 5 min of activity

  function readStore() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.phone || !parsed.token) return null;
      return parsed;
    } catch (_) { return null; }
  }

  function writeStore(phone, token) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ phone, token, savedAt: Date.now() }));
    } catch (_) {}
  }

  function clearStore() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
  }

  // Call once, as early as possible on every page. Reconciles the URL
  // (which may be carrying a stale token from whenever this specific link
  // was first generated) against the shared store (which reflects whatever
  // the most recent login anywhere actually was).
  //
  // Precedence:
  //  - URL has a phone that's different from the stored one → someone's
  //    deliberately signing in as a different number; trust the URL and
  //    overwrite the store.
  //  - A stored entry exists (and the URL's phone, if any, agrees with it)
  //    → trust the store; it's the most recently-known-good login, which
  //    the URL's own frozen copy can't claim to be.
  //  - Otherwise, fall back to whatever the URL provided (first-ever visit
  //    via a fresh magic link) and seed the store from it.
  function resolveAuth(urlPhone, urlToken) {
    const stored = readStore();
    if (urlPhone && stored && stored.phone && stored.phone !== urlPhone) {
      if (urlToken) writeStore(urlPhone, urlToken);
      return { phone: urlPhone, token: urlToken || null };
    }
    if (stored && stored.phone && stored.token) {
      return { phone: stored.phone, token: stored.token };
    }
    if (urlPhone && urlToken) {
      writeStore(urlPhone, urlToken);
      return { phone: urlPhone, token: urlToken };
    }
    return { phone: urlPhone || null, token: urlToken || null };
  }

  // Call after a fresh OTP verification succeeds, so the brand-new token
  // becomes the shared one every other page picks up from here on.
  function saveAuth(phone, token) {
    writeStore(phone, token);
  }

  function logOut() {
    clearStore();
  }

  // Keeps Xano's own copy of magic_auth_token_expiry rolling forward while
  // someone's actually using the page. Any real interaction (click, scroll,
  // keypress) counts; throttled so it's at most one network call every 5
  // minutes, not one per scroll event.
  function startActivityTouch(phone, token) {
    if (!phone || !token) return;
    let lastTouch = 0;
    let inFlight = false;
    function touch() {
      const now = Date.now();
      if (inFlight || now - lastTouch < TOUCH_MIN_INTERVAL_MS) return;
      inFlight = true;
      lastTouch = now;
      fetch(TOUCH_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, magic_auth_token: token }),
      }).catch(() => {}).finally(() => { inFlight = false; });
    }
    ['click', 'scroll', 'keydown'].forEach((evt) =>
      document.addEventListener(evt, touch, { passive: true }));
    // One touch shortly after load too — covers someone reading a page for
    // a while without clicking anything, which is still "using it."
    setTimeout(touch, 2000);
  }

  global.OndaNileAuth = { resolveAuth, saveAuth, logOut, startActivityTouch };
})(window);
