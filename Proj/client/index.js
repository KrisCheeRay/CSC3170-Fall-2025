document.addEventListener('click', (e) => {
  const t = e.target.getAttribute?.('data-tab');
  if (t) switchTab(t);
});

function switchTab(to) {
  document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
  document.querySelector('#tab-' + to).classList.add('active');
  document.querySelector('#msg').textContent = '';
}

function showMsg(text, ok = true) {
  const msg = document.querySelector('#msg');
  msg.textContent = text;
  msg.className = ok ? 'msg' : 'msg error';
}

document.querySelector('#visitor-login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const identifier = document.querySelector('#v-identifier').value.trim();
  const password = document.querySelector('#v-password').value;
  try {
    const r = await api('/auth/visitor/login', { method: 'POST', auth: false, body: { identifier, password } });
    storage.token = r.access_token;
    localStorage.setItem('role', 'visitor');
    showMsg('Login successful, redirecting...');
    setTimeout(() => location.href = './visitor.html', 800);
  } catch (err) {
    showMsg('Visitor login failed: ' + err.message, false);
  }
});

document.querySelector('#visitor-register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.querySelector('#r-name').value.trim();
  const phone = document.querySelector('#r-phone').value.trim();
  const email = document.querySelector('#r-email').value.trim();
  const org = document.querySelector('#r-org').value.trim() || null;
  const password = document.querySelector('#r-password').value;

  if (!/^\d{11}$/.test(phone)) {
    showMsg('Phone number must be 11 digits', false);
    return;
  }

  try {
    const r = await api('/auth/visitor/register', {
      method: 'POST',
      auth: false,
      body: { name, phone, email, org, password }
    });
    storage.token = r.access_token;
    localStorage.setItem('role', 'visitor');
    showMsg('Registration successful, redirecting...');
    setTimeout(() => location.href = './visitor.html', 800);
  } catch (err) {
    showMsg('Registration failed: ' + err.message, false);
  }
});

document.querySelector('#visitor-reset-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.querySelector('#reset-email').value.trim();
  const phone = document.querySelector('#reset-phone').value.trim();
  const new_password = document.querySelector('#reset-newpass').value;
  try {
    await api('/auth/visitor/password/reset', {
      method: 'POST',
      auth: false,
      body: { email, phone, new_password }
    });
    showMsg('Password has been reset, please use the new password to log in.');
    setTimeout(() => switchTab('visitor-login'), 1000);
  } catch (err) {
    showMsg('Password reset failed: ' + err.message, false);
  }
});

document.querySelector('#admin-login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.querySelector('#a-username').value.trim();
  const password = document.querySelector('#a-password').value;
  try {
    const r = await api('/auth/admin/login', { method: 'POST', auth: false, body: { username, password } });
    storage.token = r.access_token;
    localStorage.setItem('role', 'admin');
    showMsg('Admin login successful, redirecting...');
    setTimeout(() => location.href = './admin.html', 800);
  } catch (err) {
    showMsg('Admin login failed: ' + err.message, false);
  }
});
