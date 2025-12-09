function waitForApi(maxWaitMs = 4000) {
  return new Promise((resolve) => {
    if (typeof window.api === 'function') return resolve();
    const started = Date.now();
    const timer = setInterval(() => {
      if (typeof window.api === 'function' || Date.now() - started > maxWaitMs) {
        clearInterval(timer);
        resolve();
      }
    }, 50);
  });
}

function logout(){ storage.clear(); location.href='./index.html'; }
function switchTab(to){
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), el => el.classList.remove('active'));
  const el = document.querySelector('#tab-'+to);
  if (el) el.classList.add('active');
  if (to === 'list') ensureListData();
}
addEventListener('click',(e)=>{ const t=e.target.getAttribute?.('data-tab'); if(t) switchTab(t); });
window.logout = logout;
window.switchTab = switchTab;

let _locations = [];
let __locLoaded = false;
async function loadLocations(){
  const sel = document.querySelector('#locid');
  if (!sel) return;

  sel.innerHTML = '<option value="">All</option>'; 

  try{
    const data = await api('/locations/flat'); 
    _locations = Array.isArray(data) ? data : [];
    if (_locations.length === 0) { console.warn('[admin] /locations/flat Return Empty Array'); __locLoaded = true; return; }

    const opts = _locations.map(l => `<option value="${l.id}">${l.campus} - ${l.name}</option>`).join('');
    sel.insertAdjacentHTML('beforeend', opts);
    __locLoaded = true;
  }catch(err){
    console.error('[admin] Failed to load locations:', err);
  }
}
window.loadLocations = loadLocations;

let __listLoaded = false;
async function loadAll(){
  const date = document.querySelector('#date')?.value || '';
  const locid = document.querySelector('#locid')?.value || '';
  const qs = new URLSearchParams();
  if(date) qs.set('date', date);
  if(locid) qs.set('location_id', locid);

  const data = await api('/reservations/admin/reservations?'+qs.toString());
  const ul = document.querySelector('#all-list');
  const rows = (data && Array.isArray(data.results)) ? data.results : [];
  if (rows.length === 0) {
    ul.innerHTML = '<li class="muted">No Data</li>';
    return;
  }
  ul.innerHTML = rows.map(r=>`<li>
    <div>#${r.id} | ${r.start_time} ~ ${r.end_time} | ${r.campus} - ${r.location} | ${r.visitor_name} (${r.visitor_org||'-'}) | Status:${r.status}</div>
    ${r.status==='pending'
      ? `<button data-approve="${r.id}">Approve</button> <button data-deny="${r.id}" class="secondary">Deny</button>` : ''}
  </li>`).join('');
}
window.loadAll = loadAll;

addEventListener('click', async (e)=>{
  if(e.target.dataset.approve || e.target.dataset.deny){
    const id = e.target.dataset.approve || e.target.dataset.deny;
    const decision = e.target.dataset.approve ? 'approved' : 'denied';
    try{
      await api(`/reservations/${id}/decision?decision=${decision}`,{method:'PUT'});
      loadAll();
    }catch(err){ alert('Approval failed: '+(err?.message||err)); }
  }
});

function numberFormat(n){ const v = Number(n); return Number.isFinite(v) ? String(Math.round(v)) : '-'; }

async function loadReport(){
  const d = document.querySelector('#rdate')?.value;
  const qs = d ? `?date=${d}` : '';

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('mb-name','-'); set('mb-total','-'); set('mb-approved','-');
  set('mv-name','-'); set('mv-approved','-'); set('mv-total','-');
  set('ds-total','-'); set('ds-pending','-'); set('ds-approved','-'); set('ds-denied','-');
  set('ds-uvdays','-');

  try{
    const r = await api('/reservations/admin/report/daily' + qs);
    const raw = document.querySelector('#report-raw');
    if (raw) {
      raw.textContent = JSON.stringify(r, null, 2);
    }

    const mb = r?.most_booked_location || {};
    const mv = r?.most_visited_location || {};
    const ds = r?.daily_stats || {};

    set('mb-name', mb.location_name ?? 'No data');
    set('mb-total', numberFormat(mb.reservation_count));  
    set('mb-approved', numberFormat(mb.approved_count));  

    
    set('mv-name', mv.location_name ?? 'No data');
    set('mv-approved', numberFormat(mv.approved_count));  
    set('mv-total', numberFormat(mv.reservation_count));  

   
    set('ds-total', numberFormat(ds.total_reservations));
    set('ds-pending', numberFormat(ds.pending_count));
    set('ds-approved', numberFormat(ds.approved_count));
    set('ds-denied', numberFormat(ds.denied_count));

    
    set('ds-uvdays', numberFormat(ds.total_unique_visitor_days_up_to_date));

    document.querySelector('#report-view')?.classList.remove('hidden');
  }catch(err){
    const raw = document.querySelector('#report-raw');
    if (raw) { raw.textContent = 'Fail to load:' + (err?.message || err); raw.classList.remove('hidden'); }
    alert('Daily Report Failed to load:' + (err?.message || err));
  }
}

let __profileCache = null;

function fillProfileView(p) {
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v ?? '-'; };
  set('av-email', p?.email);
  set('av-phone', p?.phone);
  set('av-org', p?.org);
  set('av-work', p?.work_address);
  set('av-dn', p?.display_name);
}

function fillProfileForm(p) {
  const val = (id, v) => { const el = document.getElementById(id); if (el) el.value = v ?? ''; };
  val('ae', p?.email);
  val('ap', p?.phone);
  val('ao', p?.org);
  val('aw', p?.work_address);
  val('ad', p?.display_name);
}

function showProfileView() {
  document.getElementById('a-profile-view')?.classList.remove('hidden');
  document.getElementById('a-profile')?.classList.add('hidden');
}

function showProfileEdit() {
  document.getElementById('a-profile-view')?.classList.add('hidden');
  document.getElementById('a-profile')?.classList.remove('hidden');
}

async function loadProfile() {
  try {
    const data = await api('/auth/admin/profile'); 
    __profileCache = data || {};
    fillProfileView(__profileCache);
    fillProfileForm(__profileCache);
    showProfileView();
  } catch (err) {
    alert('Failed to load profile:' + (err?.message || err));
  }
}
addEventListener('click', (e) => {
  const t = e.target.getAttribute?.('data-tab');
  if (t === 'profile') {
    setTimeout(() => loadProfile(), 0);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-edit')?.addEventListener('click', () => {
    fillProfileForm(__profileCache || {});
    showProfileEdit();
  });

  document.getElementById('btn-cancel')?.addEventListener('click', () => {
    fillProfileView(__profileCache || {});
    showProfileView();
  });
});

document.querySelector('#a-profile')?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const body = {
    email: document.querySelector('#ae').value || null,
    phone: document.querySelector('#ap').value || null,
    org: document.querySelector('#ao').value || null,
    work_address: document.querySelector('#aw').value || null,
    display_name: document.querySelector('#ad').value || null
  };
  try{ await api('/auth/admin/profile',{method:'PUT',body}); alert('Profile updated successfully.'); }
  catch(err){ alert('Failed to save profile:'+(err?.message||err)); }
});

async function ensureListData(){
  if (!__locLoaded) { try{ await loadLocations(); }catch(e){ console.warn('ensureListData.loadLocations', e); } }
  if (!__listLoaded) { try{ await loadAll(); __listLoaded = true; }catch(e){ console.warn('ensureListData.loadAll', e); } }
}
window.ensureListData = ensureListData;

document.addEventListener('DOMContentLoaded', async () => {
  try { await waitForApi(); } catch(e){ console.warn('waitForApi timeout, continue initialization'); }
  try { await ensureListData(); } catch(e){ console.warn('init ensureListData error:', e); }
});



