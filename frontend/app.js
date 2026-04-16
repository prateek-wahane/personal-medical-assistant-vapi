const apiBase = "http://localhost:8000";
let accessToken = localStorage.getItem("medical_assistant_token") || "";
let currentUser = JSON.parse(localStorage.getItem("medical_assistant_user") || "null");

function setAuth(token, user) {
  accessToken = token || "";
  currentUser = user || null;
  if (token) {
    localStorage.setItem("medical_assistant_token", token);
  } else {
    localStorage.removeItem("medical_assistant_token");
  }
  if (user) {
    localStorage.setItem("medical_assistant_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("medical_assistant_user");
  }
  document.getElementById("authStatus").textContent = user ? `Logged in as ${user.email} (${user.id})` : "Not authenticated yet.";
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return fetch(`${apiBase}${path}`, { ...options, headers });
}

setAuth(accessToken, currentUser);

document.getElementById("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    email: document.getElementById("registerEmail").value.trim(),
    password: document.getElementById("registerPassword").value,
  };
  const response = await apiFetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  document.getElementById("authResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    email: document.getElementById("loginEmail").value.trim(),
    password: document.getElementById("loginPassword").value,
  };
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (response.ok) {
    setAuth(data.access_token, data.user);
  }
  document.getElementById("authResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const response = await apiFetch("/api/reports/upload", {
    method: "POST",
    body: form,
  });
  const data = await response.json();
  document.getElementById("uploadResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("compareBtn").addEventListener("click", async () => {
  const reportA = document.getElementById("reportA").value.trim();
  const reportB = document.getElementById("reportB").value.trim();
  const response = await apiFetch("/api/reports/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_id_a: reportA, report_id_b: reportB }),
  });
  const data = await response.json();
  document.getElementById("compareResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("mountWidgetBtn").addEventListener("click", () => {
  const assistantId = document.getElementById("assistantId").value.trim();
  const publicKey = document.getElementById("publicKey").value.trim();
  const notice = document.getElementById("vapiWidgetNotice");
  const mount = document.getElementById("widgetMount");

  if (!assistantId || !publicKey) {
    notice.textContent = "Enter both the assistant id and the public key.";
    return;
  }

  mount.innerHTML = "";
  const existingScript = document.querySelector('script[data-vapi-widget="true"]');
  if (!existingScript) {
    const script = document.createElement("script");
    script.src = "https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js";
    script.async = true;
    script.type = "text/javascript";
    script.dataset.vapiWidget = "true";
    document.body.appendChild(script);
  }

  const widget = document.createElement("vapi-widget");
  widget.setAttribute("public-key", publicKey);
  widget.setAttribute("assistant-id", assistantId);
  widget.setAttribute("mode", "voice");
  widget.setAttribute("theme", "dark");
  widget.setAttribute("size", "compact");
  if (currentUser?.id) {
    widget.setAttribute(
      "assistant-overrides",
      JSON.stringify({ metadata: { userId: currentUser.id }, variableValues: { userId: currentUser.id } })
    );
  }
  mount.appendChild(widget);
  notice.textContent = currentUser?.id
    ? `Vapi widget mounted with user context ${currentUser.id}.`
    : "Vapi widget mounted. Login first if you want per-user report isolation in voice mode.";
});
