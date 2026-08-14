import { useEffect, useState } from "react";
import { createWatch, deleteWatch, fetchWatches } from "../api.js";

export default function WatchesPanel({ user, defaultEmail }) {
  const [watches, setWatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [topic, setTopic] = useState("");
  const [threshold, setThreshold] = useState(0.15);
  const [email, setEmail] = useState(defaultEmail || "");

  async function load() {
    if (!user) return;
    try {
      const data = await fetchWatches();
      setWatches(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  async function handleCreate(e) {
    e.preventDefault();
    if (!topic.trim() || !email.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await createWatch({
        topic: topic.trim(),
        platforms: ["youtube"],
        threshold: Number(threshold),
        email: email.trim(),
      });
      setTopic("");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteWatch(id);
      setWatches((w) => w.filter((x) => x.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!user) {
    return (
      <div className="state-block">
        <span className="glyph">sign in to set up watches</span>
        Watches email you when a topic's sentiment drops — needs an account
        so we know where to send the alert.
      </div>
    );
  }

  return (
    <section>
      <form className="scan-form" onSubmit={handleCreate}>
        <div className="field-row">
          <div className="field">
            <label htmlFor="watch-topic">Topic to watch</label>
            <input
              id="watch-topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Pixel 10"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="watch-email">Alert email</label>
            <input
              id="watch-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="field-foot">
          <div className="slider-field">
            <label htmlFor="watch-threshold">Alert if score drops by</label>
            <input
              id="watch-threshold"
              type="range"
              min="0.05"
              max="1"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
            />
            <span className="slider-value">{Number(threshold).toFixed(2)}</span>
          </div>
          <button className="scan-btn" type="submit" disabled={loading}>
            {loading ? "Adding…" : "Add watch"}
          </button>
        </div>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {watches.length === 0 ? (
        <div className="state-block">
          <span className="glyph">no watches yet</span>
          Add one above — it's checked daily and rechecked against its own
          last score.
        </div>
      ) : (
        <div className="panel">
          <h3>Active watches</h3>
          {watches.map((w) => (
            <div className="video-row" key={w.id}>
              <div>
                <div className="video-title">{w.topic}</div>
                <div className="history-sub">
                  alert on drop ≥ {Number(w.threshold).toFixed(2)} · sends to {w.email}
                  {w.last_score != null && ` · last read ${Number(w.last_score).toFixed(2)}`}
                </div>
              </div>
              <button className="export-btn" onClick={() => handleDelete(w.id)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
