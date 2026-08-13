function moodOf(score) {
  if (score > 0.15) return "positive";
  if (score < -0.15) return "negative";
  return "neutral";
}

export default function VideoBreakdown({ videos = [] }) {
  if (!videos.length) return null;

  return (
    <div className="panel">
      <h3>Per-video breakdown</h3>
      {videos.map((v) => (
        <div className="video-row" key={v.video_id}>
          <div>
            <div className="video-title">
              <a
                href={`https://www.youtube.com/watch?v=${v.video_id}`}
                target="_blank"
                rel="noreferrer"
              >
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
