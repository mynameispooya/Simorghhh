// ============================================
// ERP Recon - تحلیل و نمایش درخواست‌ها
// ============================================

let allRequests = [];

// ---- بروزرسانی ----
function refresh() {
  chrome.storage.local.get('recon', (r) => {
    allRequests = r.recon || [];
    document.getElementById('count').textContent = allRequests.length;
    analyze();
    renderList();
  });
}

function clearAll() {
  chrome.storage.local.set({ recon: [] }, refresh);
}

// ---- تحلیل خودکار ----
function analyze() {
  analyzeConfirmer();
  analyzeSuccessResponse();
  analyzeListRequest();
}

// ---- بخش ۱: confirmer ----
function analyzeConfirmer() {
  const el = document.getElementById('sec1');

  // جستجو در ChangeState requests
  const cs = allRequests.filter(r => r.url.includes('ChangeState'));

  for (const req of cs) {
    if (req.parsedReq && req.parsedReq.extraData && req.parsedReq.extraData.confirmer != null) {
      const val = req.parsedReq.extraData.confirmer;
      const sourceState = req.parsedReq.sourceStateCode;
      const targetState = req.parsedReq.targetStateCode;

      el.innerHTML = `
        <div class="found">✅ شناسایی شد</div>
        <div class="code-box"><span class="hl-key">confirmer</span>: <span class="hl-num">${val}</span>
<span class="hl-key">sourceStateCode</span>: <span class="hl-num">${sourceState}</span>
<span class="hl-key">targetStateCode</span>: <span class="hl-num">${targetState}</span></div>
        <div class="copy-row"><button class="btn btn-copy" onclick="copyText('${val}')">کپی مقدار</button></div>
        <div style="margin-top:10px;font-size:11px;color:#888;">
          منبع: ChangeState → extraData.confirmer
        </div>
      `;
      return;
    }
  }

  el.innerHTML = `<div class="not-found">❌ هنوز درخواست ChangeState ثبت نشده<br>یک بار تایید دستی انجام بده</div>`;
}

// ---- بخش ۲: پاسخ موفق ----
function analyzeSuccessResponse() {
  const el = document.getElementById('sec2');

  const cs = allRequests.filter(r => r.url.includes('ChangeState') && r.status === 200);

  if (cs.length > 0) {
    const req = cs[0];
    const body = req.resBody || '(خالی)';
    el.innerHTML = `
      <div class="found">✅ ${cs.length} پاسخ موفق ثبت شده</div>
      <div class="code-box">${escHtml(body)}</div>
      <div class="copy-row"><button class="btn btn-copy" onclick="copyText(\`${escForAttr(body)}\`)">کپی Response</button></div>
    `;
  } else {
    // نشون بدم چند تا 400 داریم
    const errCount = allRequests.filter(r => r.url.includes('ChangeState') && r.status === 400).length;
    let msg = '❌ هنوز پاسخ 200 دریافت نشده';
    if (errCount > 0) {
      msg += `<br>(${errCount} تا خطای 400 ثبت شده — با درخواست تاییدشده امتحان کن)`;
    }
    el.innerHTML = `<div class="not-found">${msg}</div>`;
  }
}

// ---- بخش ۳: درخواست لیست ----
function analyzeListRequest() {
  const el = document.getElementById('sec3');

  // استراتژی ۱: URL شامل کلمات لیست باشه
  const keywords = ['List', 'Search', 'GetAll', 'Query', 'GetData', 'LeaveRequest'];
  let candidate = null;

  for (const req of allRequests) {
    if (req.url.includes('ChangeState')) continue;
    if (req.method !== 'GET' && req.method !== 'POST') continue;

    // چک URL
    const urlMatch = keywords.some(k => req.url.toLowerCase().includes(k.toLowerCase()));

    // چک بدنه پاسخ - آرایه‌ای از آبجکت‌ها با فیلدهای کارمندی
    let bodyMatch = false;
    if (req.parsedRes) {
      const arr = extractArray(req.parsedRes);
      if (arr && arr.length > 0) {
        const first = arr[0];
        bodyMatch = (first.employeeCode || first.firstName || first.lastName || first.requestNumber) ? true : false;
      }
    }

    if (urlMatch || bodyMatch) {
      candidate = req;
      if (bodyMatch) break; // اولین موردی که بدنه‌اش匹配ه، بهترین گزینه‌ست
    }
  }

  if (candidate) {
    const curl = buildCurl(candidate);
    el.innerHTML = `
      <div class="found">✅ شناسایی شد — ${candidate.method} ${candidate.shortUrl}</div>
      <div class="code-box">${escHtml(curl)}</div>
      <div class="copy-row"><button class="btn btn-copy" onclick="copyText(\`${escForAttr(curl)}\`)">کپی cURL</button></div>
    `;
  } else {
    el.innerHTML = `<div class="not-found">❌ هنوز شناسایی نشده<br>صفحه رو Refresh کن تا لیست بارگذاری بشه</div>`;
  }
}

// ---- لیست تمام درخواست‌ها ----
function renderList() {
  const el = document.getElementById('reqList');

  if (allRequests.length === 0) {
    el.innerHTML = '<div class="not-found">هنوز درخواستی ثبت نشده</div>';
    return;
  }

  el.innerHTML = allRequests.map((r, i) => {
    const mClass = r.method === 'POST' ? 'method-post' : 'method-get';
    const sClass = r.status === 200 ? 'status-200' : r.status === 400 ? 'status-400' : 'status-other';
    const isCS = r.url.includes('ChangeState');
    const label = isCS ? ' ⭐' : '';

    return `
      <div class="req-item" onclick="toggleDetail(${i})">
        <span class="method ${mClass}">${r.method}</span>
        <span class="req-url" title="${escAttr(r.url)}">${r.shortUrl}${label}</span>
        <span class="req-status ${sClass}">${r.status}</span>
        <span class="req-time">${r.time}</span>
      </div>
      <div class="req-detail" id="detail-${i}">
        <h4>URL</h4>
        <div class="code-box" style="max-height:60px;">${escHtml(r.url)}</div>
        ${r.reqBody ? `<h4>Request Body</h4><div class="code-box" style="max-height:120px;">${escHtml(r.reqBody)}</div>` : ''}
        ${r.resBody ? `<h4>Response Body (${r.status})</h4><div class="code-box" style="max-height:120px;">${escHtml(r.resBody)}</div>` : ''}
        <div class="copy-row">
          ${r.reqBody ? `<button class="btn btn-copy" onclick="event.stopPropagation();copyText(\`${escForAttr(r.reqBody)}\`)">کپی Request</button>` : ''}
          ${r.resBody ? `<button class="btn btn-copy" onclick="event.stopPropagation();copyText(\`${escForAttr(r.resBody)}\`)">کپی Response</button>` : ''}
          <button class="btn btn-copy" onclick="event.stopPropagation();copyText(\`${escForAttr(buildCurl(r))}\`)">کپی cURL</button>
        </div>
      </div>
    `;
  }).join('');
}

function toggleDetail(i) {
  const el = document.getElementById('detail-' + i);
  if (el) el.classList.toggle('active');
}

// ---- ساخت cURL ----
function buildCurl(req) {
  let c = `curl '${req.url}'`;
  c += ` \\\n  -X ${req.method}`;

  // Headers
  c += ` \\\n  -H 'Accept: */*'`;
  c += ` \\\n  -H 'x-requested-with: XMLHttpRequest'`;

  if (req.reqBody) {
    c += ` \\\n  -H 'Content-Type: application/json'`;
    c += ` \\\n  --data-raw '${req.reqBody.replace(/'/g, "\\'")}'`;
  }

  // Cookie
  if (req.cookies) {
    c += ` \\\n  -b '${req.cookies}'`;
  }

  return c;
}

// ---- ابزارها ----
function extractArray(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object') {
    // رحکاران معمولاً data.result یا data.Data یا data.items برمیگردونه
    return data.result || data.Data || data.data || data.items ||
           data.Rows || data.rows || data.records || null;
  }
  return null;
}

function escHtml(s) {
  if (!s) return '';
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escAttr(s) {
  if (!s) return '';
  return s.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target;
    const orig = btn.textContent;
    btn.textContent = '✅ کپی شد!';
    btn.style.background = '#00ff88';
    btn.style.color = '#000';
    setTimeout(() => {
      btn.textContent = orig;
      btn.style.background = '';
      btn.style.color = '';
    }, 1500);
  });
}

// ---- شروع ----
refresh();
