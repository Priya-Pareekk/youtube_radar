import { useState } from "react";
import { analyzeTopic, compareTopics } from "./api.js";
import ResultsPanel from "./components/ResultsPanel.jsx";
import CompareView from "./components/CompareView.jsx";
import HistoryDrawer from "./components/HistoryDrawer.jsx";

export default function App() {
  const [mode, setMode] = useState("solo"); // "solo" | "compare"
  const [topic, setTopic] = useState("iPhone 16");
  const [topicB, setTopicB] = useState("Galaxy S25");
  const [limit, setLimit] = useState(10);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);

  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState([]);

  function pushHistory(entry) {
    setHistory((h) => [{ id: crypto.randomUUID(), ...entry }, ...h].slice(0, 25));
  }

  async function runScan(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === "solo") {
        setCompareResult(null);
        const data = await analyzeTopic(topic, limit);
        setResult(data);
        pushHistory({
          mode: "solo",
          topic: data.topic,
          avgScore: data.avg_score,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          snapshot: { type: "solo", data },
        });
      } else {
        setResult(null);
        const data = await compareTopics(topic, topicB, limit);
        setCompareResult(data);
        pushHistory({
          mode: "compare",
          topic: data.a.topic,
          topicB: data.b.topic,
          avgScore: data.a.avg_score,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          snapshot: { type: "compare", data },
        });
      }
    } catch (err) {
      setError(err.message || "Scan failed.");
    } finally {
      setLoading(false);
    }
  }

  function selectHistory(entry) {
    if (entry.snapshot.type === "solo") {
      setMode("solo");
      setResult(entry.snapshot.data);
      setCompareResult(null);
    } else {
      setMode("compare");
      setCompareResult(entry.snapshot.data);
      setResult(null);
    }
    setHistoryOpen(false);
  }

  return (
    <div className="shell">
      <header className="masthead">
        <div className="masthead-title">
          <span className="masthead-mark">TR-01</span>
          <div>
            <h1>TubeRadar</h1>
            <div className="masthead-tagline">a pulse-reading on public comment</div>
          </div>
        </div>
        <button className="history-toggle" onClick={() => setHistoryOpen(true)}>
          Scan log ({history.length})
        </button>
      </header>

      <div className="mode-switch">
        <button
          className={mode === "solo" ? "active" : ""}
          onClick={() => setMode("solo")}
        >
          Solo scan
        </button>
        <button
          className={mode === "compare" ? "active" : ""}
          onClick={() => setMode("compare")}
        >
          Competitor battle
        </button>
      </div>

      <form className="scan-form" onSubmit={runScan}>
        {mode === "solo" ? (
          <div className="field-row single">
            <div className="field">
              <label htmlFor="topic">Topic to scan</label>
              <input
                id="topic"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. iPhone 16"
                required
              />
            </div>
          </div>
        ) : (
          <div className="field-row">
            <div className="field">
              <label htmlFor="topicA">Contender A</label>
              <input
                id="topicA"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="topicB">Contender B</label>
              <input
                id="topicB"
                type="text"
                value={topicB}
                onChange={(e) => setTopicB(e.target.value)}
                required
              />
            </div>
          </div>
        )}

        <div className="field-foot">
          <div className="slider-field">
            <label htmlFor="limit">Videos to scan</label>
            <input
              id="limit"
              type="range"
              min="1"
              max="50"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            />
            <span className="slider-value">{limit}</span>
          </div>
          <button className="scan-btn" type="submit" disabled={loading}>
            {loading ? "Scanning…" : "Run scan"}
          </button>
        </div>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {!loading && !error && !result && !compareResult && (
        <div className="state-block">
          <span className="glyph">nothing on the dial yet</span>
          Run a scan to see how a topic reads.
        </div>
      )}

      {loading && (
        <div className="state-block">
          <span className="glyph">tuning in…</span>
          Pulling comments and scoring sentiment.
        </div>
      )}

      {!loading && mode === "solo" && <ResultsPanel result={result} />}
      {!loading && mode === "compare" && <CompareView compareResult={compareResult} />}

      <HistoryDrawer
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        history={history}
        onSelect={selectHistory}
      />
    </div>
  );
}
