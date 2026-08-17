const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function postPersonalize(payload) {
  return postJson("/personalize", payload, true);
}

export async function postDebug(payload) {
  return postJson("/debug/personalization", payload, true);
}

export async function login(payload) {
  return postJson("/auth/login", payload);
}

export async function register(payload) {
  return postJson("/auth/register", payload);
}

export async function getUsers() {
  const response = await fetch(`${API_BASE_URL}/auth/users`, { headers: authHeaders() });
  const data = await response.json();
  if (!response.ok) throw new Error(extractMessage(data));
  return data;
}

export async function createCheckout(payload) {
  return postJson("/billing/checkout", payload, true);
}

export async function getLogs(lines = 120) {
  const response = await fetch(`${API_BASE_URL}/admin/logs?lines=${lines}`, { headers: authHeaders() });
  const data = await response.json();
  if (!response.ok) throw new Error(extractMessage(data));
  return data;
}

async function postJson(path, payload, authenticated = false) {
  const headers = {
    "Content-Type": "application/json",
    ...(authenticated ? authHeaders() : {}),
  };
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(extractMessage(data));
  }
  return data;
}

function authHeaders() {
  const token = localStorage.getItem("mynaksh:token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function extractMessage(data) {
  const message = data?.error?.message || data?.detail?.error?.message || data?.detail || "Request failed";
  return typeof message === "string" ? message : JSON.stringify(message);
}
