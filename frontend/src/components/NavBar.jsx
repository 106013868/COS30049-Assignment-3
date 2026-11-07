import { Link, NavLink } from "react-router";

export default function NavBar() {
  return (
    <header>
      <nav className="nav" aria-label="Main">
        <Link to="/" className="nav-logo">PhishLens</Link>
        <div className="nav-links">
          <NavLink to="/" end>Inspect</NavLink>
          <NavLink to="/about">How it works</NavLink>
        </div>
      </nav>
    </header>
  );
}