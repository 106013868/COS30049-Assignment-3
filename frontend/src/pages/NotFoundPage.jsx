import { Link } from "react-router";

export default function NotFoundPage() {
  return (
    <main className="page">
      <div className="card message-page">
        <p className="eyebrow">Error 404</p>
        <h1>Page not found</h1>
        <p className="muted">There is nothing at this address. Check the link, or go back to inspect a URL.</p>
        <Link to="/">Back to Inspect</Link>
      </div>
    </main>
  );
}