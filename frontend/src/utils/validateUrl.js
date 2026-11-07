export const MAX_URL_LENGTH = 2048;

// Front-end checks are for usability: the back end checks the same things again.
// Returns an error message, or "" when the URL looks fine.
export function validateUrl(value) {
  const url = value.trim();
  if (url === "") return "Please paste a URL.";
  if (url.length > MAX_URL_LENGTH) return `That URL is too long (${MAX_URL_LENGTH} characters max).`;
  if (/\s/.test(url)) return "URLs can't contain spaces.";
  if (!url.includes(".")) return "That doesn't look like a URL. Try something like example.com.";
  return "";
}