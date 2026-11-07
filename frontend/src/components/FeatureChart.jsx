import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getModelInfo } from "../api/client";
import { FEATURE_GROUPS } from "../utils/features";

// Chart 1: "Why did this URL get this score?"
// Compares this URL's features with the average safe and phishing URL from the training data.
export default function FeatureChart({ features }) {
  const [reference, setReference] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [group, setGroup] = useState("counts");

  useEffect(() => {
    getModelInfo()
      .then((info) => setReference(info.reference))
      .catch((err) => setLoadError(err.message));
  }, []);                                  // [] = run once, when the chart first appears

  const rows = FEATURE_GROUPS[group].map(([key, label]) => ({
    name: label,
    thisUrl: features[key],
    safeAvg: reference?.legitimate[key],
    phishAvg: reference?.phishing[key],
  }));

  return (
    <section className="card chart-card" aria-labelledby="feature-chart-heading">
      <h2 id="feature-chart-heading">How this URL compares with typical URLs</h2>
      <p className="muted">
        The bars show what the model measured in this URL next to the average safe and phishing URL it learned from.
      </p>

      <div className="toggle-group" role="group" aria-label="Feature group">
        <button type="button" className="toggle" aria-pressed={group === "counts"}
          onClick={() => setGroup("counts")}>Counts</button>
        <button type="button" className="toggle" aria-pressed={group === "lengths"}
          onClick={() => setGroup("lengths")}>Lengths</button>
      </div>

      {loadError && <p className="error-text">Averages unavailable: {loadError}</p>}

      <div className="chart-box">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16, bottom: 16 }}>
            <CartesianGrid stroke="#1f3340" horizontal={false} />
            <XAxis type="number" stroke="var(--text-muted)"
              label={{ value: group === "lengths" ? "Characters" : "Count", position: "insideBottom", offset: -10, fill: "var(--text-muted)" }} />
            <YAxis type="category" dataKey="name" width={110} stroke="var(--text-muted)" />
            <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }}
              labelStyle={{ color: "var(--text)" }} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
            <Legend verticalAlign="top" />
            <Bar dataKey="thisUrl" name="This URL" fill="var(--purple)" />
            <Bar dataKey="safeAvg" name="Average safe URL" fill="var(--cyan)" />
            <Bar dataKey="phishAvg" name="Average phishing URL" fill="var(--danger)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}