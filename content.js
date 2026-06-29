// ============================================
// ERP Recon - شنودگر درخواست‌های شبکه
// تمام XHR و Fetch رو intercept می‌کنه
// ============================================
(function () {
  'use strict';

  const MAX_STORE = 80;

  // ---- ذخیره درخواست ----
  function store(method, url, reqBody, resBody, status, resHeaders) {
    // فقط درخواست‌های API
    if (!url || !url.includes('/api/')) return;

    let parsedReq = null;
    let parsedRes = null;
    try { parsedReq = JSON.parse(reqBody); } catch (_) {}
    try { parsedRes = JSON.parse(resBody); } catch (_) {}

    const entry = {
      id: Date.now() + '_' + Math.random().toString(36).slice(2, 8),
      time: new Date().toLocaleTimeString('fa-IR'),
      method,
      url,
      shortUrl: url.split('/').slice(-2).join('/'),
      reqBody: reqBody || null,
      parsedReq,
      resBody: resBody || null,
      parsedRes,
      status,
      resHeaders,
      cookies: document.cookie
    };

    chrome.storage.local.get('recon', (r) => {
      let list = r.recon || [];
      list.unshift(entry);
      if (list.length > MAX_STORE) list = list.slice(0, MAX_STORE);
      chrome.storage.local.set({ recon: list });
    });
  }

  // ---- Intercept XMLHttpRequest ----
  const xhrOpen = XMLHttpRequest.prototype.open;
  const xhrSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function (m, u, ...a) {
    this._r = { m, u };
    return xhrOpen.apply(this, [m, u, ...a]);
  };

  XMLHttpRequest.prototype.send = function (b) {
    if (this._r) {
      this._r.b = b;
      this.addEventListener('load', function () {
        store(this._r.m, this._r.u, this._r.b, this.responseText, this.status, this.getAllResponseHeaders());
      });
    }
    return xhrSend.apply(this, [b]);
  };

  // ---- Intercept Fetch ----
  const nativeFetch = window.fetch;
  window.fetch = function (input, init) {
    init = init || {};
    const url = typeof input === 'string' ? input : (input.url || '');
    const method = (init.method || 'GET').toUpperCase();
    const body = init.body || null;

    return nativeFetch.apply(this, [input, init]).then(async (resp) => {
      try {
        const clone = resp.clone();
        const text = await clone.text();
        const hdrs = {};
        resp.headers.forEach((v, k) => { hdrs[k] = v; });
        store(method, url, body, text, resp.status, hdrs);
      } catch (_) {}
      return resp;
    }).catch(e => Promise.reject(e));
  };

  // ---- نشانگر کوچک روی صفحه ----
  const badge = document.createElement('div');
  badge.id = 'erp-recon-badge';
  badge.textContent = '🔍 Recon';
  badge.style.cssText = `
    position:fixed; bottom:12px; left:12px; z-index:999999;
    background:#1a1a2e; color:#00ff88; font:12px monospace;
    padding:5px 10px; border-radius:6px; opacity:0.7;
    pointer-events:none; transition:opacity 0.3s;
    direction:ltr; box-shadow:0 2px 8px rgba(0,0,0,0.4);
  `;
  document.addEventListener('DOMContentLoaded', () => document.body.appendChild(badge));

  // شمارنده درخواست‌ها
  let count = 0;
  const origStore = store;
  // نمیتونیم store رو override کنم چون تو closure هست
  // پس شمارنده رو داخل خود store بذاریم
  // راه حل ساده‌تر: هر ۲ ثانیه تعداد رو بروز کنیم
  setInterval(() => {
    chrome.storage.local.get('recon', (r) => {
      const c = (r.recon || []).length;
      if (badge.parentNode) {
        badge.textContent = `🔍 Recon: ${c} requests`;
      }
    });
  }, 2000);
})();
