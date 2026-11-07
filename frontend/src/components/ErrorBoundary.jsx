import { Component } from "react";

// Catches any crash inside the app and shows a friendly page instead of a blank screen.
// React only supports this as a class component.
export default class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    console.error("PhishLens crashed:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="page">
          <div className="card message-page" role="alert">
            <p className="eyebrow">Unexpected error</p>
            <h1>Something went wrong</h1>
            <p className="muted">PhishLens hit a problem it could not recover from. Reloading usually fixes it.</p>
            <button type="button" className="button" onClick={() => window.location.reload()}>
              Reload
            </button>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}