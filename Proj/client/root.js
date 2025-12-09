const API = "http://localhost:8000"; 

const getToken = () => localStorage.getItem("root_token") || "";
const setToken = (t) => (t ? localStorage.setItem("root_token", t) : localStorage.removeItem("root_token"));

const loginView = document.getElementById("login-view");
const portalView = document.getElementById("portal-view");
const msg = document.getElementById("msg");
const createSection = document.getElementById("create-section");
const locationManagement = document.getElementById("location-management");

if (getToken()) {
  loginView.classList.add("hidden");
  portalView.classList.remove("hidden");
}

document.getElementById("login-btn").addEventListener("click", async () => {
  const username = document.getElementById("root-username").value.trim();
  const password = document.getElementById("root-password").value.trim();
  msg.textContent = "Login in...";

  try {
    const res = await fetch(`${API}/auth/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) throw new Error("Login failed");
    const data = await res.json();

    if (data.role === "superadmin") {
      setToken(data.access_token);
      msg.textContent = "Login successful";
      loginView.classList.add("hidden");
      portalView.classList.remove("hidden");
    } else {
      msg.textContent = "Not a superadmin account";
    }
  } catch (err) {
    msg.textContent = "Login failed: " + err.message;
  }
});

document.getElementById("logout-btn").addEventListener("click", () => {
  setToken("");
  portalView.classList.add("hidden");
  loginView.classList.remove("hidden");
  msg.textContent = "Logged out";
});

document.getElementById("show-location-management").addEventListener("click", () => {
  locationManagement.style.display = "block";
  loadLocations();
});

async function loadLocations() {
  const tbody = document.getElementById("location-body");
  tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";

  try {
    const res = await fetch(`${API}/locations/admin/all`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    if (res.status === 401) {
      msg.textContent = "Login expired, please log in again";
      setToken("");
      portalView.classList.add("hidden");
      loginView.classList.remove("hidden");
      tbody.innerHTML = `<tr><td colspan="5">Unauthorized</td></tr>`;
      return;
    }

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const list = await res.json();
    const rows = Array.isArray(list) ? list : [];

    if (!rows.length) {
      tbody.innerHTML = `<tr><td colspan="5">No locations available</td></tr>`;
      return;
    }

    tbody.innerHTML = rows
      .map((loc) => {
      
        const val = (loc.is_active + "").toLowerCase();
        const isActive = val === "1" || val === "true";

        
        const delDisabled = isActive ? "disabled" : "";
        const delTitle = isActive ? "title='Change the status to disabled first, then delete'" : "title='Delete location'";

        return `
          <tr>
            <td>${loc.id}</td>
            <td>${loc.campus ?? ""}</td>
            <td>${loc.name ?? ""}</td>
            <td>${isActive ? "Enabled" : "Disabled"}</td>
            <td>
              <button class="set-active" data-id="${loc.id}" data-value="1" ${isActive ? "disabled" : ""}>Enable</button>
              <button class="set-active" data-id="${loc.id}" data-value="0" ${!isActive ? "disabled" : ""}>Disable</button>
              <button class="delete-location" data-id="${loc.id}" ${delDisabled} ${delTitle}>Delete</button>
            </td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    document.getElementById("location-body").innerHTML = `<tr><td colspan="5">Loading failed: ${err.message}</td></tr>`;
  }
}


document.getElementById("load-locations").addEventListener("click", loadLocations);


document.getElementById("show-create-location").addEventListener("click", () => {
  document.getElementById("create-location-form").style.display = "block";
});


document.getElementById("create-location-btn").addEventListener("click", async () => {
  const campus = document.getElementById("campus").value;
  const name = document.getElementById("new-location-name").value.trim();

  if (!name) {
    msg.textContent = "Name cannot be empty";
    return;
  }

  try {
    const res = await fetch(`${API}/locations/admin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ campus, name }),
    });

    if (res.ok) {
      msg.textContent = "Location created successfully!";
      document.getElementById("create-location-form").style.display = "none";
      loadLocations();
    } else {
      const t = await res.text();
      msg.textContent = "Creation failed: " + (t || res.status);
    }
  } catch (err) {
    msg.textContent = "Network error: " + err.message;
  }
});

document.getElementById("location-body").addEventListener("click", async (e) => {
  const delBtn = e.target.closest("button.delete-location");
  if (delBtn) {
    if (delBtn.disabled) {
      msg.textContent = "Please disable the location before deleting";
      return;
    }
    const id = delBtn.dataset.id;
    if (!id) return;
    const ok = window.confirm(`Are you sure you want to delete location #${id}? This action cannot be undone.`);
    if (!ok) return;

    try {
      delBtn.disabled = true;
      const res = await fetch(`${API}/locations/admin/${id}`, {
        method: "DELETE",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (res.status === 401) {
        msg.textContent = "Login expired, please log in again";
        setToken("");
        portalView.classList.add("hidden");
        loginView.classList.remove("hidden");
        return;
      }

      if (!res.ok) {
        const t = await res.text();
        msg.textContent = `Deletion failed: ${t || res.status}`;
        return;
      }

      msg.textContent = "Location deleted successfully";
      await loadLocations();
    } catch (err) {
      msg.textContent = "Network error: " + err.message;
    } finally {
      delBtn.disabled = false;
    }
    return; 
  }

  const btn = e.target.closest("button.set-active");
  if (!btn) return;

  const id = btn.dataset.id;
  const value = btn.dataset.value; 
  const boolStr = value === "1" ? "true" : "false";

  try {
    btn.disabled = true;
    const res = await fetch(`${API}/locations/admin/${id}/active?is_active=${boolStr}`, {
      method: "PATCH",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${getToken()}`,
      }
    });

    if (res.status === 401) {
      msg.textContent = "Login expired, please log in again";
      setToken("");
      portalView.classList.add("hidden");
      loginView.classList.remove("hidden");
      return;
    }

    if (!res.ok) {
      const t = await res.text();
      msg.textContent = `Update failed: ${t || res.status}`;
      return;
    }

    await loadLocations();
  } catch (err) {
    msg.textContent = "Network error: " + err.message;
  } finally {
    btn.disabled = false;
  }
});


document.getElementById("cancel-create-location").addEventListener("click", () => {
  document.getElementById("create-location-form").style.display = "none";
  document.getElementById("new-location-name").value = "";
});


document.getElementById("cancel-location-management").addEventListener("click", () => {
  locationManagement.style.display = "none";
});


document.addEventListener("DOMContentLoaded", () => {
  if (getToken()) loadLocations();
});


document.getElementById("create-admin-btn").addEventListener("click", () => {
  createSection.classList.remove("hidden");
});


document.getElementById("cancel-create").addEventListener("click", () => {
  createSection.classList.add("hidden");
  document.getElementById("new-username").value = "";
  document.getElementById("new-password").value = "";
  document.getElementById("create-msg").textContent = "";
});


document.getElementById("confirm-create").addEventListener("click", async () => {
  const newUsername = document.getElementById("new-username").value.trim();
  const newPassword = document.getElementById("new-password").value.trim();
  const msgBox = document.getElementById("create-msg");
  const tk = getToken();

  if (!tk) {
    msgBox.textContent = "Please log in again as superadmin";
    return;
  }
  if (!newUsername || !newPassword) {
    msgBox.textContent = "Username and password cannot be empty";
    return;
  }

  msgBox.textContent = "Creating admin...";

  try {
    const res = await fetch(`${API}/auth/superadmin/admins`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${tk}`,
      },
      body: JSON.stringify({ username: newUsername, password: newPassword }),
    });

    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      msgBox.textContent = `Created successfully: ${data.username || newUsername}`;
      document.getElementById("new-username").value = "";
      document.getElementById("new-password").value = "";
    } else {
      msgBox.textContent = `Failed: ${data.detail || res.status}`;
    }
  } catch (err) {
    msgBox.textContent = "Network error: " + err.message;
  }
});
