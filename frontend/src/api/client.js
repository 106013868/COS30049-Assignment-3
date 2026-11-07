// Every call to the back end goes through this file, so errors are handled in one place.
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(BASE_URL + path, options);
  } catch {
    // fetch only throws when the server could not be reached at all
    throw new Error("Cannot reach the PhishLens server. Is it running?");
  }

  // Every reply from our API is JSON, but guard against anything else
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.error?.message ?? "Something went wrong. Please try again.";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}

export function checkUrl(url) {
  return request("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

export function getModelInfo() {
  return request("/api/model-info");
}

export function getHealth() {
  return request("/api/health");
}