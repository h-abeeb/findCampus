const API_BASE = window.API_BASE || "http://127.0.0.1:5000/api";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      // Only set JSON header for string bodies; FormData sets its own boundary
      ...(typeof options.body === "string" ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
}

const api = {
  listItems: (search = "") =>
    apiRequest(`/items${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getItem: (id) => apiRequest(`/items/${encodeURIComponent(id)}`),
  reportItem: (item) =>
    apiRequest("/items", { method: "POST", body: JSON.stringify(item) }),
  uploadImage: (file) => {
    const form = new FormData();
    form.append("image", file);
    return apiRequest("/upload", { method: "POST", body: form });
  },
  submitClaim: (id, claim) =>
    apiRequest(`/items/${encodeURIComponent(id)}/claims`, {
      method: "POST",
      body: JSON.stringify(claim),
    }),
};