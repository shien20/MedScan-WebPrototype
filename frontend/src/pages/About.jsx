import "./About.css"

export default function About({ navigate }) {
  return (
    <main className="about-page">
      <div className="about-inner">
        <h1 className="page-title">About MedScan</h1>
        <p className="about-lead">
          MedScan is an AI-powered chest X-ray screening system developed as part of a
          final year capstone project at Sunway University. It uses deep learning to
          classify chest X-rays into four categories and provides visual and textual
          explanations to support clinical decision-making.
        </p>

        <div className="about-cards">
          <div className="about-card">
            <h3>🎯 Purpose</h3>
            <p>
              To assist radiologists in resource-limited settings by automating the
              initial screening of chest X-rays for pneumonia, tuberculosis, COVID-19,
              and normal cases.
            </p>
          </div>
          <div className="about-card">
            <h3>🧠 Model</h3>
            <p>
              Built on ResNet50 with transfer learning, fine-tuned on a combined
              dataset of chest X-rays. GradCAM provides visual explainability for
              every prediction.
            </p>
          </div>
          <div className="about-card">
            <h3>⚠️ Disclaimer</h3>
            <p>
              MedScan is a research prototype for decision support only.
              It does not replace clinical judgement. All predictions must be
              reviewed by a qualified medical professional.
            </p>
          </div>
        </div>

        <button className="btn-primary" onClick={() => navigate("analysis")}
                style={{ marginTop: "2rem" }}>
          Try it now
        </button>
      </div>
    </main>
  )
}
