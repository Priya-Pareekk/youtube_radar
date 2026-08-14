function moodOf(score) {
  if (score > 0.15) return "positive";
  if (score < -0.15) return "negative";
  return "neutral";
}

const PLATFORM_LABEL = {
  youtube: "YT",
  reddit: "RD",
};

export default function VideoBreakdown({ items = [] }) {
  if (!items.length) return null;

  return (
    <div className="panel">
      <h3>Per-item breakdown</h3>
      {items.map((v) => (
        <div className="video-row" key={`${v.platform}-${v.id}`}>
          <div>
            <div className="video-title">
              <span className="platform-tag">{PLATFORM_LABEL[v.platform] || v.platform}</span>{" "}
              <a href={v.url} target="_blank" rel="noreferrer">
                {v.title}
              </a>
            </div>
          </div>
          <span className={`video-score ${moodOf(v.avg_score)}`}>
            {v.avg_score.toFixed(2)} · {v.comment_count} cmts
          </span>
        </div>
      ))}
    </div>
  );
}
