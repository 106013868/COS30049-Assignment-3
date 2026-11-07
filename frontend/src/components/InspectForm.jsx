import { useState } from "react";
import { MAX_URL_LENGTH, validateUrl } from "../utils/validateUrl";

// The "Inspect a URL" card. Checks the input before anything is sent.
export default function InspectForm({ onSubmit, loading, serverError }) {
  const [url, setUrl] = useState("");
  const [fieldError, setFieldError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();                 // stop the browser reloading the page
    const problem = validateUrl(url);
    setFieldError(problem);
    if (problem) return;                    // invalid: nothing is sent to the back end
    onSubmit(url.trim());
  }

  const message = fieldError || serverError;

  return (
    <section className="card inspect" aria-labelledby="inspect-heading">
      <h2 id="inspect-heading">Inspect a URL</h2>
      <p className="muted">
        Paste a complete link or domain name below. Analysis is based only on URL structure and finishes in moments.
      </p>

      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="url-input">URL to Inspect</label>
        <div className="input-row">
          <input
            id="url-input"
            type="text"
            inputMode="url"
            autoComplete="off"
            spellCheck="false"
            placeholder="e.g. https://example.com/account"
            maxLength={MAX_URL_LENGTH + 100}
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-invalid={fieldError ? "true" : "false"}
            aria-describedby="url-message"
          />
          <button type="submit" className="button" disabled={loading}>
            {loading ? "Inspecting..." : "Submit"}
          </button>
        </div>
        <p id="url-message" className="field-message error-text" role="alert">
          {message}
        </p>
      </form>

      {/* Screen readers announce changes inside this region */}
      <p className="visually-hidden" aria-live="polite">
        {loading ? "Inspecting the URL, please wait." : ""}
      </p>
    </section>
  );
}