const OPTIONS = [
  { id: "youtube", label: "YouTube" },
  { id: "reddit", label: "Reddit" },
];

export default function PlatformToggle({ platforms, onChange }) {
  function toggle(id) {
    if (platforms.includes(id)) {
      if (platforms.length === 1) return; // keep at least one selected
      onChange(platforms.filter((p) => p !== id));
    } else {
      onChange([...platforms, id]);
    }
  }

  return (
    <div className="slider-field" style={{ gap: 8 }}>
      <label>Sources</label>
      {OPTIONS.map((opt) => (
        <button
          key={opt.id}
          type="button"
          className={`mode-switch-pill ${platforms.includes(opt.id) ? "active" : ""}`}
          onClick={() => toggle(opt.id)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
