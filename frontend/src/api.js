import { supabase } from "./supabaseClient.js";

// In dev, Vite proxies "/api" to localhost:8000 (see vite.config.js).
// In production, set VITE_API_BASE to your deployed backend's full URL,
// e.g. https://tuberadar-backend.onrender.com/api
const BASE = import.meta.env.VITE_API_BASE || "/api";

async function authHeaders() {
  if (!supabase) return {};
  const { data } = await supabase.auth.getSession();
  const token = data?.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(method, path, body) {
  const headers = { "Content-Type": "application/json", ...(await authHeaders()) };
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = "Something went wrong.";
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* ignore parse error */
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export function analyzeTopic(topic, limit, platforms) {
  return request("POST", "/analyze", { topic, limit, platforms });
}

export function compareTopics(topic_a, topic_b, limit, platforms) {
  return request("POST", "/compare", { topic_a, topic_b, limit, platforms });
}

export function fetchHistory() {
  return request("GET", "/history");
}

export function fetchHistoryDetail(id) {
  return request("GET", `/history/${id}`);
}

export function createWatch(payload) {
  return request("POST", "/watches", payload);
}

export function fetchWatches() {
  return request("GET", "/watches");
}

export function deleteWatch(id) {
  return request("DELETE", `/watches/${id}`);
}
