export default function HistoryDrawer({ open, onClose, history, onSelect }) {
  return (
    <>
      {open && <div className="drawer-overlay" onClick={onClose} />}
      <aside className={`history-drawer ${open ? "open" : ""}`}>
        <h3>Scan log</h3>
        {history.length === 0 && (
          <p className="history-empty">
            Nothing scanned yet this session. Runs will collect here.
          </p>
        )}
        {history.map((h) => (
          <div className="history-item" key={h.id} onClick={() => onSelect(h)}>
            <div className="history-topic">
              {h.mode === "compare" ? `${h.topic} vs ${h.topicB}` : h.topic}
            </div>
            <div className="history-sub">
              {h.time} · avg {h.avgScore.toFixed(2)}
            </div>
          </div>
        ))}
      </aside>
    </>
  );
}
