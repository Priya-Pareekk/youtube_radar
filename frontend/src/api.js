// In dev, Vite proxies "/api" to localhost:8000 (see vite.config.js).
// In production, set VITE_API_BASE to your deployed backend's full URL,
// e.g. https://tuberadar-backend.onrender.com/api
const BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
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

  return res.json();
}

export function analyzeTopic(topic, limit) {
  return request("/analyze", { topic, limit });
}

export function compareTopics(topic_a, topic_b, limit) {
  return request("/compare", { topic_a, topic_b, limit });
}
