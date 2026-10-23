const API_BASE = window.API_BASE || "http://127.0.0.1:5000/api";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

const api = {
  listItems: (search = "") =>
    apiRequest(`/items${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getItem: (id) => apiRequest(`/items/${encodeURIComponent(id)}`),
  reportItem: (item) =>
    apiRequest("/items", { method: "POST", body: JSON.stringify(item) }),
  submitClaim: (id, claim) =>
    apiRequest(`/items/${encodeURIComponent(id)}/claims`, {
      method: "POST",
      body: JSON.stringify(claim),
    }),
};
