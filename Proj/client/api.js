const BASE_URL = 'http://localhost:8000';

const storage = {
  get token() { return localStorage.getItem('access_token'); },
  set token(v) { localStorage.setItem('access_token', v); },
  clear() { localStorage.removeItem('access_token'); localStorage.removeItem('role'); }
};

async function api(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 
    'Content-Type': 'application/json',
    'accept': 'application/json'
  };
  if (auth && storage.token) headers['Authorization'] = `Bearer ${storage.token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method, headers, body: body ? JSON.stringify(body) : undefined
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || res.statusText || `HTTP ${res.status}`);
  }

  const text = await res.text().catch(() => '');
  if (!text) return {}; 

  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}
