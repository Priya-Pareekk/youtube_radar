import Dial from "./Dial.jsx";
import ThemeBars from "./ThemeBars.jsx";
import VideoBreakdown from "./VideoBreakdown.jsx";
import { exportCsv } from "../export.js";

function Side({ result }) {
  return (
    <div>
      <h3 className="side-title">{result.topic}</h3>
      <div className="gauge-card" style={{ marginBottom: 20 }}>
        <Dial score={result.avg_score} size="small" />
        <span className="result-meta">
          {result.total_comments} comments · {result.video_count} videos
        </span>
        <button className="export-btn" onClick={() => exportCsv(result)}>
          Export CSV
        </button>
      </div>
      <ThemeBars themes={result.themes.slice(0, 6)} />
      <VideoBreakdown videos={result.videos} />
    </div>
  );
}

export default function CompareView({ compareResult }) {
  if (!compareResult) return null;
  const { a, b, winner, gap } = compareResult;

  return (
    <section>
      <div className="winner-strip">
        <span className="eyebrow">Stronger sentiment</span>
        <span className="winner-name">{winner}</span>
        <div className="result-meta" style={{ marginTop: 6 }}>
          gap of {gap.toFixed(2)}
        </div>
      </div>
      <div className="compare-grid">
        <Side result={a} />
        <Side result={b} />
      </div>
    </section>
  );
}
