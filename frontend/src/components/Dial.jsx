export default function Dial({ score = 0, size = "normal" }) {
  const clamped = Math.max(-1, Math.min(1, score));
  const angleDeg = clamped * 90; // -90..90 across the semicircle
  const rad = ((angleDeg - 90) * Math.PI) / 180;

  const cx = 110;
  const cy = 110;
  const needleR = 78;
  const nx = cx + needleR * Math.cos(rad);
  const ny = cy + needleR * Math.sin(rad);

  const ticks = [-1, -0.5, 0, 0.5, 1];

  const mood =
    clamped > 0.15 ? "positive" : clamped < -0.15 ? "negative" : "neutral";
  const moodLabel =
    mood === "positive" ? "Positive" : mood === "negative" ? "Negative" : "Neutral";

  return (
    <div className="dial-wrap">
      <svg
        viewBox="0 0 220 130"
        className="dial-svg"
        role="img"
        aria-label={`Sentiment ${clamped.toFixed(2)}, ${moodLabel}`}
      >
        <path d="M 24 110 A 86 86 0 0 1 196 110" className="dial-arc" />
        {ticks.map((t) => {
          const a = ((t * 90 - 90) * Math.PI) / 180;
          const inner = t === 0 ? 66 : 70;
          const x1 = cx + inner * Math.cos(a);
          const y1 = cy + inner * Math.sin(a);
          const x2 = cx + 86 * Math.cos(a);
          const y2 = cy + 86 * Math.sin(a);
          return (
            <line
              key={t}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              className={t === 0 ? "dial-tick-mid" : "dial-tick"}
            />
          );
        })}
        <line
          x1={cx}
          y1={cy}
          x2={nx}
          y2={ny}
          className={`dial-needle ${mood}`}
        />
        <circle cx={cx} cy={cy} r="5" className="dial-pivot" />
      </svg>
      <div className="dial-readout">
        <span className="dial-score">{clamped.toFixed(2)}</span>
        <span className="dial-label">{moodLabel}{size === "small" ? "" : " sentiment"}</span>
      </div>
    </div>
  );
}
