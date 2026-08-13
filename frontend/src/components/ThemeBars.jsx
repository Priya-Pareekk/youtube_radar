export default function ThemeBars({ themes = [] }) {
  if (!themes.length) return null;
  const max = Math.max(...themes.map((t) => t.count));

  return (
    <div className="panel">
      <h3>Recurring language</h3>
      {themes.map((t) => (
        <div className="theme-row" key={t.word}>
          <span className="theme-word">{t.word}</span>
          <span className="theme-bar-track">
            <span
              className="theme-bar-fill"
              style={{ width: `${(t.count / max) * 100}%` }}
            />
          </span>
          <span className="theme-count">{t.count}</span>
        </div>
      ))}
    </div>
  );
}
