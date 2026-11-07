import { useState } from "react";
import { checkUrl } from "../api/client";
import InspectForm from "../components/InspectForm";
import ResultCard from "../components/ResultCard";
import FeatureChart from "../components/FeatureChart";
import HistoryChart from "../components/HistoryChart";

export default function HomePage({ history, addToHistory }) {
  // status is one of: "idle", "loading", "success", "error"
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleCheck(url) {
    setStatus("loading");
    setErrorMessage("");
    try {
      const data = await checkUrl(url);
      const entry = { ...data, id: Date.now() };
      setResult(entry);
      addToHistory(entry);
      setStatus("success");
    } catch (err) {
      setErrorMessage(err.status === 503
        ? "PhishLens is busy or unavailable. Try again shortly."
        : err.message);
      setStatus("error");
    }
  }

  function showFromHistory(entry) {
    setResult(entry);
    setStatus("success");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <main className="page">
      <section className="hero">
        <h1>PhishLens</h1>
        <p>
          Inspect suspicious URLs locally using AI-inspired format signals. PhishLens never opens the link,
          fetches its content, or sends it to a third-party service.
        </p>
      </section>

      {status === "success" ? (
        <ResultCard result={result} onNewQuery={() => setStatus("idle")} />
      ) : (
        <>
          <div className="intro">
            <div>
              <p className="eyebrow">Link safety, without the click</p>
              <h2>Know where a link leads before you trust it.</h2>
              <p className="muted">
                Paste a link from an email or message. PhishLens reads only the text of the address,
                so you never have to visit the site to check it.
              </p>
            </div>
            <div className="grid-art" aria-hidden="true" />
          </div>
          <InspectForm onSubmit={handleCheck} loading={status === "loading"}
            serverError={status === "error" ? errorMessage : ""} />
        </>
      )}

      {status === "success" && (
        <div className="charts">
          <FeatureChart features={result.features} />
          <HistoryChart history={history} selectedId={result.id} onSelect={showFromHistory} />
        </div>
      )}
    </main>
  );
}