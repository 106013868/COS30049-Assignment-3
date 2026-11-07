import { useEffect, useState } from "react";
import { Route, Routes } from "react-router";
import { getHealth } from "./api/client";
import ErrorBoundary from "./components/ErrorBoundary";
import NavBar from "./components/NavBar";
import HomePage from "./pages/HomePage";
import AboutPage from "./pages/AboutPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  // History lives here, not in HomePage, so it survives visits to the About page
  const [history, setHistory] = useState([]);
  const [serverProblem, setServerProblem] = useState("");

  useEffect(() => {
    getHealth().catch((err) => setServerProblem(err.message));
  }, []);

  function addToHistory(entry) {
    setHistory((old) => [...old, entry]);
  }

  return (
    <ErrorBoundary>
      <NavBar />
      {serverProblem && (
        <p className="banner" role="status">PhishLens server problem: {serverProblem}</p>
      )}
      <Routes>
        <Route path="/" element={<HomePage history={history} addToHistory={addToHistory} />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </ErrorBoundary>
  );
}