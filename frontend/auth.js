// frontend/auth.js
// Simple auth helper: login to get JWT, save in localStorage, and helper for fetch headers.

const AUTH_TOKEN_KEY = "resume_app_token";

export async function login(username, password) {
  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Login failed");
  localStorage.setItem(AUTH_TOKEN_KEY, data.token);
  return data;
}

export function logout() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function authHeaders() {
  const token = getToken();
  if (!token) return {};
  return { Authorization: "Bearer " + token };
}

// helper to call the generate endpoint with auth
export async function generateResume(payload) {
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    authHeaders()
  );
  const res = await fetch("/generate", {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Generate failed");
  return data;
}
