import "./Home.css"
import homePageRight from "../assets/home-page-right.png"

export default function Home({ navigate }) {
  return (
    <main className="home">

      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero-left">
          <h1 className="hero-heading">
            Your AI partner<br />
            in <span className="hero-accent">medical imaging</span>
          </h1>
          <p className="hero-sub">
            Simply upload, we analyze, and you get instant results
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={() => navigate("analysis")}>
              Try now
            </button>
            <button className="btn-outline" onClick={() => navigate("about")}>
              Learn more
            </button>
          </div>
        </div>

        <div className="hero-right">
          <img
            src={homePageRight}
            alt="MedScan Medical Illustration"
            className="hero-image"
          />
        </div>
      </section>

      {/* ── Feature cards ───────────────────────────────────── */}
      <section className="features">
        <div className="feature-card">
          <div className="feature-icon" style={{ background: "#eff6ff", color: "#2563eb" }}>🔬</div>
          <h3>AI-Powered Analysis</h3>
          <p>Deep learning models trained on thousands of chest X-rays for accurate disease detection.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon" style={{ background: "#f0fdf4", color: "#16a34a" }}>🗺️</div>
          <h3>GradCAM Explainability</h3>
          <p>Visual heatmaps highlight the exact regions influencing the model's prediction.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon" style={{ background: "#fef3c7", color: "#d97706" }}>📋</div>
          <h3>Clinical Reports</h3>
          <p>AI-generated screening summaries in clinical language to support radiologist review.</p>
        </div>
      </section>

    </main>
  )
}
