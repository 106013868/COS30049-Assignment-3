import TrustGauge from "./TrustGauge";
import SignalCard from "./SignalCard";
import { CheckIcon, PlusIcon, WarnIcon } from "./Icons";

export default function ResultCard({ result, onNewQuery }) {
  const phishing = result.verdict === "phishing";
  const confidence = Math.round(result.confidence * 100);
  const modelSignals = result.signals.filter((s) => s.used_by_model);
  const extraSignals = result.signals.filter((s) => !s.used_by_model);

  return (
    <section className="card" aria-labelledby="result-heading">
      <div className="result-top">
        <TrustGauge score={result.trust_score} phishing={phishing} />

        <div className="result-text">
          <p className="eyebrow">Local inspection complete</p>
          <h2 id="result-heading">URL Safety Assessment</h2>
          <p className={`badge ${phishing ? "phishing" : "safe"}`}>
            {phishing ? <WarnIcon size={16} /> : <CheckIcon size={16} />}
            {phishing ? "LIKELY PHISHING" : "LIKELY SAFE"}
          </p>
          <p className="confidence">Model confidence: {confidence}%</p>
          {/* The URL is shown as plain text. It is never a link, so it can't be opened by accident. */}
          <p className="checked-url muted">Checked: {result.url}</p>
          <p className="muted">
            {phishing
              ? "The URL format shows warning signs often seen in phishing links. Do not enter any details on this site."
              : "The URL format presents relatively few warning signs. Continue to verify the sender and destination before sharing information."}
          </p>
          <button type="button" className="button button-small" onClick={onNewQuery}>
            <PlusIcon size={16} /> New query
          </button>
        </div>
      </div>

      <hr className="divider" />

      <div className="signals">
        <h3>Signals used in this assessment</h3>
        <ul className="signal-grid">
          {modelSignals.map((s) => <SignalCard key={s.id} signal={s} />)}
        </ul>

        <h3 className="extra">Extra checks (not part of the score)</h3>
        <ul className="signal-grid">
          {extraSignals.map((s) => <SignalCard key={s.id} signal={s} />)}
        </ul>
      </div>

      <p className="disclaimer muted">
        PhishLens is an extra safety check based on the URL text alone, not a guarantee that a site is safe.
      </p>
    </section>
  );
}