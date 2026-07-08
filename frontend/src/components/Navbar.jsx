import "./Navbar.css"
import logo from "../assets/logo-icon.png";

export default function Navbar({ currentPage, navigate }) {
  return (
    <nav className="navbar">
      <div className="navbar-inner">

        {/* Logo */}
        <button className="navbar-logo" onClick={() => navigate("home")}>
          <img src={logo} alt="MedScan Logo" className="logo-icon" />
          <span className="logo-text">MedScan</span>
        </button>
        {/* Nav links */}
        <div className="navbar-links">
          {["home", "analysis", "about"].map((p) => (
            <button
              key={p}
              className={`nav-link ${currentPage === p ? "active" : ""}`}
              onClick={() => navigate(p)}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>

      </div>
    </nav>
  )
}
