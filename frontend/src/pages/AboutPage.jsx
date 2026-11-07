import { ChecklistIcon, LinkIcon, OfflineIcon } from "../components/Icons";

const CARDS = [
  [ChecklistIcon, "Checks URL length, domain and path length, IP addresses, subdomains, digits, symbols and suspicious words."],
  [LinkIcon, "Flags wording and URL patterns frequently associated with phishing attempts."],
  [OfflineIcon, "Does not visit the URL or retrieve page content during analysis."],
];

export default function AboutPage() {
  return (
    <main className="page about">
      <h1>How Does PhishLens Work?</h1>
      <p>
        This tool inspects patterns in the URL itself. It is an additional safety check, not a guarantee
        that a website is safe.
      </p>
      <ul className="about-cards">
        {CARDS.map(([Icon, text]) => (
          <li key={text} className="about-card">
            <p>{text}</p>
            <Icon size={120} />
          </li>
        ))}
      </ul>
    </main>
  );
}