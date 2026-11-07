import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const FILTERS = [
  ["all", "All"],
  ["phishing", "Phishing"],
  ["legitimate", "Legitimate"],
];

// Short label for the x-axis: the domain, cut to 14 characters
function shortName(url) {
  const domain = url.replace(/^[a-z]+:\/\//i, "").split("/")[0];
  return domain.length > 14 ? domain.slice(0, 13) + "…" : domain;
}

function HistoryTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const item = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <p className="checked-url">{item.url}</p>
      <p>Trust score: {item.trust_score}%</p>
      <p>Verdict: {item.verdict}</p>
    </div>
  );
}

// Chart 2: "How do the URLs I checked this session compare?"
export default function HistoryChart({ history, selectedId, onSelect }) {
  const [filter, setFilter] = useState("all");
  const shown = history.filter((item) => filter === "all" || item.verdict === filter);
  const data = shown.map((item) => ({ ...item, label: shortName(item.url) }));

  return (
    <section className="card chart-card" aria-labelledby="history-chart-heading">
      <h2 id="history-chart-heading">URLs checked this session</h2>
      <p className="muted">Trust score of every URL you checked. Select a bar or a URL below to see its full result.</p>

      <div className="toggle-group" role="group" aria-label="Filter by verdict">
        {FILTERS.map(([value, label]) => (
          <button key={value} type="button" className="toggle" aria-pressed={filter === value}
            onClick={() => setFilter(value)}>{label}</button>
        ))}
      </div>

      <p className="chart-legend">
        <span className="legend-swatch" style={{ background: "var(--danger)" }} /> Phishing
        <span className="legend-swatch" style={{ background: "var(--cyan)" }} /> Legitimate
        <span className="legend-line" /> 50% cut-off
      </p>

      {shown.length === 0 ? (
        <p className="muted">No URLs match this filter yet.</p>
      ) : (
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, left: 8, right: 8, bottom: 8 }}>
              <CartesianGrid stroke="#1f3340" vertical={false} />
              <XAxis dataKey="label" stroke="var(--text-muted)" interval={0} angle={-30} textAnchor="end" height={60} />
              <YAxis domain={[0, 100]} stroke="var(--text-muted)"
                width={56}
                label={{ value: "Trust score (%)", angle: -90, position: "insideLeft", offset: 4, dy: 50, fill: "var(--text-muted)" }} />
              <Tooltip content={<HistoryTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
              <ReferenceLine y={50} stroke="var(--purple-soft)" strokeDasharray="4 4"
                label={{ value: "Cut-off", fill: "var(--purple-soft)", position: "insideTopLeft" }} />
              <Bar dataKey="trust_score" name="Trust score" cursor="pointer"
                onClick={(_, index) => onSelect(data[index])}>
                {data.map((item) => (
                  <Cell key={item.id}
                    fill={item.verdict === "phishing" ? "var(--danger)" : "var(--cyan)"}
                    stroke={item.id === selectedId ? "var(--text)" : "none"} strokeWidth={2} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* The same list as buttons, so every URL can also be selected by keyboard */}
      <ul className="history-list">
        {shown.map((item) => (
          <li key={item.id}>
            <button type="button" className="history-item" onClick={() => onSelect(item)}
              aria-current={item.id === selectedId ? "true" : undefined}>
              <span className="history-url">{item.url}</span>
              <span className="history-score" style={{ color: item.verdict === "phishing" ? "var(--danger)" : "var(--cyan)" }}>
                {item.trust_score}% {item.verdict === "phishing" ? "phishing" : "safe"}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}