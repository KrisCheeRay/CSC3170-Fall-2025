function logout() {
  storage.clear();
  location.href = './index.html';
}
document.querySelector('#logout-btn').addEventListener('click', logout);


function switchTab(to) {
  document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
  const el = document.querySelector('#tab-' + to);
  if (el) el.classList.add('active');
  if (to === 'list') loadReservations();
  if (to === 'noti') { loadUnreadCount(); loadNotifications(true); }
  if (to === 'profile') loadProfile();
}
addEventListener('click', (e) => {
  const tab = e.target.getAttribute?.('data-tab');
  if (tab) switchTab(tab);
});


function toLocalISOString(dateStrOrDate) {
  const d = (dateStrOrDate instanceof Date) ? dateStrOrDate : new Date(dateStrOrDate);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString();
}
function toInputValue(isoStr) {
  const d = new Date(isoStr);
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}
function sameDay(a, b) {
  return a.getFullYear() === b.getFullYear() &&
         a.getMonth() === b.getMonth() &&
         a.getDate() === b.getDate();
}
function inOfficeHour(d) {
  const h = d.getHours();
  return h >= 9 && h <= 17;
}
function validateWindow(start, end) {
  if (!sameDay(start, end)) return 'Start and end must be on the same day';
  if (start >= end) return 'End time must be after start time';
  if (!(inOfficeHour(start) && inOfficeHour(end))) return 'Time must be between 09:00 and 17:00';
  return '';
}

let _locations = [];
async function loadLocations() {
  try {
    const locs = await api('/locations/flat');
    _locations = Array.isArray(locs) ? locs : [];
    const html = _locations.map(l => `<option value="${l.id}">${l.campus} - ${l.name}</option>`).join('');
    const sel1 = document.querySelector('#location');
    const sel2 = document.querySelector('#edit-location');
    if (sel1) sel1.innerHTML = html;
    if (sel2) sel2.innerHTML = html;
  } catch {
    alert('Failed to load locations. Please check your network or backend.');
  }
}
function getLocationsByCampus(campus) {
  return _locations.filter(l => !campus || l.campus === campus);
}
function renderEditLocations(campus, selectedId) {
  const list = getLocationsByCampus(campus);
  const sel = document.querySelector('#edit-location');
  sel.innerHTML = list.map(l => `<option value="${l.id}">${l.campus} - ${l.name}</option>`).join('');
  if (selectedId != null) {
    const has = list.some(l => String(l.id) === String(selectedId));
    sel.value = has ? String(selectedId) : (list[0] ? String(list[0].id) : '');
  }
}

document.querySelector('#create-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const campus = document.querySelector('#campus').value;
  const location_id = Number(document.querySelector('#location').value);
  const start = new Date(document.querySelector('#start').value);
  const end = new Date(document.querySelector('#end').value);
  const purpose = document.querySelector('#purpose').value || null;
  const is_driving = document.querySelector('#drive').checked;
  const plate_number = is_driving ? document.querySelector('#plate').value.trim() : null;

  const err = validateWindow(start, end);
  if (err) return alert('❌ ' + err);
  if (!location_id && location_id !== 0) return alert('Please select a location!');
  if (is_driving && !/^[A-Z0-9]{6}$/.test(plate_number || '')) return alert('Plate number must be 6 uppercase letters or digits');

  const body = {
    campus,
    start_time: toLocalISOString(start),
    end_time: toLocalISOString(end),
    location_id,
    purpose,
    is_driving,
    plate_number
  };

  try {
    const r = await api('/reservations/', { method: 'POST', body });
    alert(`Reservation created successfully! Status: ${r.status || 'pending'}`);
    e.target.reset();
    switchTab('list');
  } catch (err2) {
    alert('Fail to create reservation: ' + err2.message);
    console.error('Creation error details:', err2);
  }
});


async function loadReservations() {
  try {
    const status = document.querySelector('#filter-status').value;
    const list = await api('/reservations/' + (status ? `?status=${status}` : ''));
    const ul = document.querySelector('#resv-list');
    if (!Array.isArray(list) || list.length === 0) {
      ul.innerHTML = '<li class="muted">Currently No Reservations</li>';
      return;
    }
    ul.innerHTML = list.map(r => {
      const editable = r.status === 'pending';
      const when = `${new Date(r.start_time).toLocaleString()} ~ ${new Date(r.end_time).toLocaleString()}`;
      const loc = r.location || (r.location_detail ? `${r.location_detail.campus}-${r.location_detail.name}` : '');
      return `<li data-id="${r.id}">
        <div><b>#${r.id}</b> ${when} <span class="muted">(${loc})</span></div>
        <div>Status：<b>${r.status}</b> ${r.purpose ? `｜Purpose：${r.purpose}` : ''} ${r.is_driving ? `｜Plate Number：${r.plate_number || ''}` : ''}</div>
        <div class="actions">
          ${editable ? `<button data-edit="${r.id}">Edit</button> <button data-del="${r.id}" class="secondary">Delete</button>` : ''}
        </div>
      </li>`;
    }).join('');
  } catch (err) {
    alert('Fail to load reservations: ' + err.message);
  }
}
document.querySelector('#refresh-btn').addEventListener('click', loadReservations);

addEventListener('click', async (e) => {
  const delId = e.target.dataset?.del;
  if (delId) {
    if (!confirm('Are you sure you want to delete this reservation?')) return;
    try {
      await api('/reservations/' + delId, { method: 'DELETE' });
      loadReservations();
    } catch (err) {
      alert('Fail to delete reservation: ' + err.message);
    }
    return;
  }

  const editId = e.target.dataset?.edit;
  if (editId) {
    try {
      const status = document.querySelector('#filter-status').value;
      const list = await api('/reservations/' + (status ? `?status=${status}` : ''));
      const r = list.find(x => String(x.id) === String(editId));
      if (!r) return alert('Reservation not found, please refresh and try again');
      if (r.status !== 'pending') return alert('Only pending reservations can be edited');

      document.querySelector('#edit-id').value = r.id;
      document.querySelector('#edit-start').value = toInputValue(r.start_time);
      document.querySelector('#edit-end').value = toInputValue(r.end_time);
      document.querySelector('#edit-purpose').value = r.purpose || '';
      document.querySelector('#edit-drive').checked = !!r.is_driving;
      document.querySelector('#edit-plate').value = r.plate_number || '';

      const locObj = _locations.find(x => x.id === r.location_id);
      const campus = r.campus || (locObj ? locObj.campus : 'LOWER');
      document.querySelector('#edit-campus').value = campus;
      renderEditLocations(campus, r.location_id);

      document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
      const editSec = document.querySelector('#edit-resv-form');
      editSec.classList.remove('hidden'); 
      editSec.classList.add('active');
      editSec.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      alert('进入编辑失败：' + err.message);
    }
  }
});

document.querySelector('#cancel-edit-resv').addEventListener('click', () => {
  document.querySelector('#edit-resv').reset();
  switchTab('list');
});

document.querySelector('#edit-resv').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.querySelector('#edit-id').value;
  const campus = document.querySelector('#edit-campus').value; 
  const location_id = Number(document.querySelector('#edit-location').value);
  const start = new Date(document.querySelector('#edit-start').value);
  const end = new Date(document.querySelector('#edit-end').value);
  const purpose = document.querySelector('#edit-purpose').value || null;
  const is_driving = document.querySelector('#edit-drive').checked;
  const plate_number = is_driving ? document.querySelector('#edit-plate').value.trim() : null;

  const err = validateWindow(start, end);
  if (err) return alert('❌ ' + err);
  if (!location_id && location_id !== 0) return alert('Please select a location!');
  if (is_driving && !/^[A-Z0-9]{6}$/.test(plate_number || '')) return alert('License plate must be 6 uppercase letters or numbers');

  try {
    await api(`/reservations/${id}`, {
      method: 'PUT',
      body: {
        campus,                       
        location_id,
        start_time: toLocalISOString(start),
        end_time: toLocalISOString(end),
        purpose,
        is_driving,
        plate_number
      }
    });
    alert('Reservation edited successfully');
    switchTab('list');
    loadReservations();
  } catch (err2) {
    alert('Fail to edit reservation: ' + err2.message);
  }
});

async function loadProfile() {
  try {
    const p = await api('/auth/visitor/profile');
    document.querySelector('#v-name').textContent = p.name || '';
    document.querySelector('#v-email').textContent = p.email || '';
    document.querySelector('#v-phone').textContent = p.phone || '';
    document.querySelector('#v-org').textContent = p.org || '';

    document.querySelector('#p-name').value = p.name || '';
    document.querySelector('#p-email').value = p.email || '';
    document.querySelector('#p-phone').value = p.phone || '';
    document.querySelector('#p-org').value = p.org || '';
  } catch (err) {
    alert('Fail to load profile: ' + err.message);
  }
}
document.querySelector('#edit-btn').addEventListener('click', () => {
  document.querySelector('#profile-view').style.display = 'none';
  document.querySelector('#profile-form').style.display = 'block';
});
document.querySelector('#cancel-profile').addEventListener('click', () => {
  document.querySelector('#profile-form').style.display = 'none';
  document.querySelector('#profile-view').style.display = 'block';
});
document.querySelector('#profile-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    const body = {
      name: document.querySelector('#p-name').value,
      email: document.querySelector('#p-email').value,
      phone: document.querySelector('#p-phone').value,
      org: document.querySelector('#p-org').value
    };
    const newPass = document.querySelector('#p-pass').value;
    if (newPass) body.new_password = newPass;

    await api('/auth/visitor/profile', { method: 'PUT', body });
    alert('Profile updated successfully');
    document.querySelector('#p-pass').value = '';
    document.querySelector('#profile-form').style.display = 'none';
    document.querySelector('#profile-view').style.display = 'block';
    loadProfile();
  } catch (err) {
    alert('Fail to save profile: ' + err.message);
  }
});

let _noti = { page: 1, limit: 10, onlyUnread: false };

async function loadUnreadCount() {
  try {
    const r = await api('/notifications/notifications/unread_count');
    const n = Number(r?.count || r || 0);
    const badge = document.querySelector('#noti-badge');
    if (!badge) return;
    if (n > 0) {
      badge.textContent = n;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  } catch { // Ignore errors
  }
}

async function loadNotifications(reset = false) {
  try {
    if (reset) _noti.page = 1;
    const skip = (_noti.page - 1) * _noti.limit;
    const qs = `?only_unread=${_noti.onlyUnread ? 1 : 0}&skip=${skip}&limit=${_noti.limit}`;

    let list = await api('/notifications/notifications' + qs);

    if (_noti.onlyUnread && Array.isArray(list)) {
      list = list.filter(n => !n.is_read);
    }

    const ul = document.querySelector('#noti-list');
    if (!Array.isArray(list) || list.length === 0) {
      ul.innerHTML = '<li class="muted">Currently no notifications</li>';
    } else {
      ul.innerHTML = list.map(n => `
        <li data-nid="${n.id}">
          <div><b>${n.title || 'System Notification'}</b> <span class="muted">#${n.id}</span></div>
          <div>${n.content || ''}</div>
          <div class="muted">${new Date(n.created_at).toLocaleString()} ｜ Status: ${n.is_read ? 'Read' : 'Unread'}</div>
          ${n.is_read ? '' : `<div class="actions"><button data-read="${n.id}">Mark as Read</button></div>`}
        </li>
      `).join('');
    }
    document.querySelector('#page-info').textContent = `第 ${_noti.page} 页`;
    loadUnreadCount();
  } catch (err) {
    alert('Fail to load notifications: ' + err.message);
  }
}

addEventListener('click', async (e) => {
  const nid = e.target.dataset?.read;
  if (!nid) return;

  try {
    await api(`/notifications/notifications/${nid}/read`, {
      method: 'PATCH',
      body: {}                 
    });
    await loadNotifications();
  } catch (err) {
    try {
      await api(`/notifications/notifications/${nid}/read`, {
        method: 'PATCH',
        body: { is_read: true }
      });
      await loadNotifications();
    } catch (err2) {
      alert('Fail to mark as read: ' + JSON.stringify(err2));
    }
  }
});

document.querySelector('#mark-all-read').addEventListener('click', async () => {
  if (!confirm('Are you sure you want to mark all notifications as read?')) return;
  try {
    await api('/notifications/notifications/read_all', { method: 'POST' });
    loadNotifications(true);
  } catch (err) {
    alert('Fail to mark all as read: ' + err.message);
  }
});

document.querySelector('#noti-only-unread').addEventListener('change', (e) => {
  _noti.onlyUnread = !!e.target.checked;
  loadNotifications(true); 
});
document.querySelector('#prev-page').addEventListener('click', () => {
  if (_noti.page > 1) { _noti.page -= 1; loadNotifications(); }
});
document.querySelector('#next-page').addEventListener('click', () => {
  _noti.page += 1;
  loadNotifications();
});
document.querySelector('#reload-noti').addEventListener('click', () => loadNotifications(true));

document.querySelector('#edit-campus').addEventListener('change', (e) => {
  const campus = e.target.value;
  renderEditLocations(campus, null); 
});

(async function init() {
  await loadLocations();
  await loadProfile();
  switchTab('new');
})();

