import { useEffect, useState } from "react";
import { fetchHistory, fetchHistoryDetail } from "../api.js";

export default function HistoryDrawer({ open, onClose, user, localHistory, onSelectLocal, onSelectRemote }) {
  const [remoteHistory, setRemoteHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && user) {
      setLoading(true);
      fetchHistory()
        .then(setRemoteHistory)
        .catch(() => setRemoteHistory([]))
        .finally(() => setLoading(false));
    }
  }, [open, user]);

  async function handleRemoteClick(item) {
    const detail = await fetchHistoryDetail(item.id);
    onSelectRemote(detail);
  }

  const usingRemote = Boolean(user);
  const list = usingRemote ? remoteHistory : localHistory;

  return (
    <>
      {open && <div className="drawer-overlay" onClick={onClose} />}
      <aside className={`history-drawer ${open ? "open" : ""}`}>
        <h3>Scan log {usingRemote ? "(synced)" : "(this session only)"}</h3>

        {loading && <p className="history-empty">Loading…</p>}

        {!loading && list.length === 0 && (
          <p className="history-empty">
            {usingRemote
              ? "No saved scans yet — run one and it'll land here."
              : "Nothing scanned yet this session. Sign in to keep history across visits."}
          </p>
        )}

        {!loading &&
          list.map((h) =>
            usingRemote ? (
              <div className="history-item" key={h.id} onClick={() => handleRemoteClick(h)}>
                <div className="history-topic">
                  {h.mode === "compare" ? `${h.topic} vs ${h.topic_b}` : h.topic}
                </div>
                <div className="history-sub">
                  {new Date(h.created_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })} · avg{" "}
                  {Number(h.avg_score).toFixed(2)} · {(h.platforms || []).join(" + ")}
                </div>
              </div>
            ) : (
              <div className="history-item" key={h.id} onClick={() => onSelectLocal(h)}>
                <div className="history-topic">
                  {h.mode === "compare" ? `${h.topic} vs ${h.topicB}` : h.topic}
                </div>
                <div className="history-sub">
                  {h.time} · avg {h.avgScore.toFixed(2)}
                </div>
              </div>
            )
          )}
      </aside>
    </>
  );
}
