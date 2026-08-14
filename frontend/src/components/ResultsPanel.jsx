import Dial from "./Dial.jsx";
import ThemeBars from "./ThemeBars.jsx";
import VideoBreakdown from "./VideoBreakdown.jsx";
import { exportCsv } from "../export.js";

export default function ResultsPanel({ result }) {
  if (!result) return null;
  const { positive, negative, neutral } = result.sentiment_split;

  return (
    <section>
      <div className="result-header">
        <h2>“{result.topic}”</h2>
        <span className="result-meta">
          {result.total_comments} comments · {result.item_count} items ·{" "}
          {result.platforms.join(" + ")}
        </span>
      </div>

      <div className="result-grid">
        <div className="gauge-card">
          <Dial score={result.avg_score} />
          <div className="split-legend">
            <span><i className="dot positive" />{positive}</span>
            <span><i className="dot neutral" />{neutral}</span>
            <span><i className="dot negative" />{negative}</span>
          </div>
          <button className="export-btn" onClick={() => exportCsv(result)}>
            Export CSV
          </button>
        </div>

        <div>
          <ThemeBars themes={result.themes} />
          <VideoBreakdown items={result.items} />
        </div>
      </div>
    </section>
  );
}
