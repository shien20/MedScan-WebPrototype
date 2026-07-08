import { useState, useRef } from "react"
import axios from "axios"
import "./Analysis.css"
import analysis from "../assets/analysis.png";


const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const CLASS_COLORS = {
  "Normal":       "#22c55e",
  "Pneumonia":    "#f97316",
  "COVID-19":     "#ef4444",
  "Tuberculosis": "#a855f7"
}

export default function Analysis({ navigate }) {
  const [file,    setFile]    = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)
  const [error,   setError]   = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [pdfPassword, setPdfPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // ── File handling ──────────────────────────────────────
  function handleFile(selected) {
    if (!selected) return
    if (!["image/jpeg", "image/png", "image/jpg"].includes(selected.type)) {
      setError("Only JPG and PNG files are accepted.")
      return
    }
    setFile(selected)
    setPreview(URL.createObjectURL(selected))
    setResult(null)
    setError(null)
  }

  function handleInputChange(e) {
    handleFile(e.target.files[0])
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  function handleDragOver(e) {
    e.preventDefault()
    setDragOver(true)
  }

  function handleDragLeave() {
    setDragOver(false)
  }

  // ── Submit to backend ──────────────────────────────────
  async function handleSubmit() {
    if (!file) return
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await axios.post(`${API_URL}/predict`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      setResult(response.data)
    } catch (err) {
      setError("Analysis failed. Please check the backend is running and try again.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // ── Reset ──────────────────────────────────────────────
  function handleReset() {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ""
  }

  const predClass   = result?.prediction?.predicted_class
  const confidence  = result?.prediction?.confidence
  const allProbs    = result?.prediction?.all_probabilities
  const predColor   = predClass ? CLASS_COLORS[predClass] : "#2563eb"


  function fileToBase64(file) {
        return new Promise((resolve, reject) => {

            const reader = new FileReader()

            reader.readAsDataURL(file)

            reader.onload = () => resolve(reader.result)

            reader.onerror = reject

          })
      }

  // ── RESULTS VIEW ───────────────────────────────────────
  if (result) {
    return (
      <main className="analysis-page">
        <div className="analysis-inner">

          <div className="result-header">
            <h1 className="page-title">Result</h1>
            <p className="page-subtitle">Prediction, Explainability, Report</p>
          </div>

          <div className="result-grid">

            {/* Left column */}
            <div className="result-left">

              {/* Prediction card */}
              <div className="card result-card" style={{ borderTop: `4px solid ${predColor}` }}>
                <h2 className="result-card-title" style={{ color: predColor }}>
                  Prediction
                </h2>
                <p className="result-disease">{predClass}</p>
                <p className="result-confidence">Confidence: {confidence?.toFixed(1)}%</p>

                {/* Probability bars */}
                <div className="prob-bars">
                  {allProbs && Object.entries(allProbs).map(([cls, prob]) => (
                    <div key={cls} className="prob-row">
                      <div className="prob-label-row">
                        <span className="prob-name">{cls}</span>
                        <span className="prob-val"
                              style={{ color: CLASS_COLORS[cls], fontWeight: 600 }}>
                          {prob.toFixed(1)}%
                        </span>
                      </div>
                      <div className="prob-track">
                        <div className="prob-fill"
                             style={{ width: `${prob}%`, background: CLASS_COLORS[cls] }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* GradCAM card */}
              <div className="card result-card">
                <h2 className="result-card-title" style={{ color: var_blue }}>
                  Grad-CAM
                </h2>
                <div className="gradcam-images">
                  <div className="gradcam-img-wrap">
                    <span className="gradcam-label">Original</span>
                    <img src={preview} alt="Original X-ray"
                         className="gradcam-img" />
                  </div>
                  <div className="gradcam-img-wrap">
                    <span className="gradcam-label">Heatmap</span>
                    <img src={`data:image/png;base64,${result.heatmap}`}
                         alt="GradCAM heatmap"
                         className="gradcam-img" />
                  </div>
                </div>
                <p className="gradcam-note">
                  Warm (red/orange) regions indicate areas most influential in the prediction.
                </p>
              </div>

            </div>

            {/* Right column — Report */}
            <div className="card result-card report-card">
              <h2 className="result-card-title" style={{ color: var_blue }}>
                Report
              </h2>
              <div className="report-meta">
                <span className="report-tag"
                      style={{ background: predColor + "20", color: predColor }}>
                  {predClass}
                </span>
                <span className="report-conf">{confidence?.toFixed(1)}% confidence</span>
              </div>

              {/* Findings */}
              <div className="report-section">
                <h3 className="report-section-title">Findings</h3>
                <p className="report-section-body">{result.report.findings}</p>
              </div>

              {/* Impression */}
              <div className="report-section">
                <h3 className="report-section-title">Impression</h3>
                <p className="report-section-body">{result.report.impression}</p>
              </div>

              {/* Recommendation */}
              <div className="report-section">
                <h3 className="report-section-title">Recommendation</h3>
                <p className="report-section-body">{result.report.recommendation}</p>
              </div>

              <div className="report-disclaimer">
                ⚠️ This report is AI-generated for screening support only and does not
                constitute a medical diagnosis. All findings must be reviewed by a
                qualified clinician.
              </div>
            </div>

          </div>

          {/* Analyse again or download */}
          <div className="result-actions">

            <button
                className="btn-download"
                onClick={() => setShowPasswordModal(true)}
            >
                Download Report
            </button>

            <button
                className="btn-secondary"
                onClick={handleReset}
            >
                Analyse Again
            </button>

        </div>

        </div>
        {/* Password Modal */}
            {showPasswordModal && (

                <div className="modal-overlay">

                    <div className="password-modal">

                        <h2>Protect PDF</h2>

                        <p>
                            Enter a password to encrypt the downloaded report.
                        </p>

                        <input
                            type="password"
                            placeholder="Password"
                            value={pdfPassword}
                            onChange={(e)=>setPdfPassword(e.target.value)}
                        />

                        <input
                            type="password"
                            placeholder="Confirm Password"
                            value={confirmPassword}
                            onChange={(e)=>setConfirmPassword(e.target.value)}
                        />

                        <div className="modal-buttons">

                            <button
                                className="btn-secondary"
                                onClick={()=>{
                                    setShowPasswordModal(false);
                                    setPdfPassword("");
                                    setConfirmPassword("");
                                }}
                            >
                                Cancel
                            </button>

                            <button
                                className="btn-download"
                                onClick={downloadPDF}
                            >
                                Download
                            </button>

                        </div>

                    </div>

                </div>

            )}
      </main>
    )
  }

  async function downloadPDF() {

    try {

        if (pdfPassword !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        if (pdfPassword.length < 4) {
            alert("Password should be at least 4 characters.");
            return;
        }

        const originalBase64 = await fileToBase64(file);

        const response = await axios.post(
            `${API_URL}/download-report`,
            {
                report: result.report,
                prediction: result.prediction,
                original_image: originalBase64,
                heatmap: result.heatmap,
                password: pdfPassword
            },
            {
                responseType: "blob"
            }
        );

        const url = window.URL.createObjectURL(new Blob([response.data]));

        const link = document.createElement("a");
        link.href = url;
        link.download = "MedScan_Report.pdf";

        document.body.appendChild(link);
        link.click();
        link.remove();

        // ✅ Clear password and close popup
        setPdfPassword("");
        setConfirmPassword("");
        setShowPasswordModal(false);

    } catch (err) {
        console.error(err);
        alert("Failed to download report.");
    }

  }


  // ── UPLOAD VIEW ────────────────────────────────────────
  return (
    <main className="analysis-page">
      <div className="analysis-inner">

        <div className="upload-header">
          <h1 className="page-title-icon">
            <img src={analysis} alt="Analysis Logo" className="logo-icon" />
            Analysis
          </h1>
        </div>

        <div className="upload-section">
          <h2 className="upload-title">Upload Chest X-ray</h2>

          {/* Drop zone */}
          <div
            className={`dropzone ${dragOver ? "dragover" : ""} ${preview ? "has-file" : ""}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => !preview && inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleInputChange}
              style={{ display: "none" }}
            />

            {preview ? (
              <div className="preview-wrap">
                <img src={preview} alt="Preview" className="preview-img" />
                <button className="remove-btn" onClick={(e) => { e.stopPropagation(); handleReset() }}>
                  ✕ Remove
                </button>
              </div>
            ) : (
              <div className="dropzone-placeholder">
                <div className="dropzone-icon">🫁</div>
                <p className="dropzone-main">Drag and drop your image here</p>
                <p className="dropzone-sub">Accepted format: jpg, png</p>
                <p className="dropzone-sub">Limit: 1</p>
                <button
                  className="choose-btn"
                  onClick={(e) => { e.stopPropagation(); inputRef.current?.click() }}
                >
                  Choose file
                </button>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="error-box">{error}</div>
          )}

          {/* Submit */}
          <div className="upload-actions">
            <button
              className="btn-primary analyse-btn"
              onClick={handleSubmit}
              disabled={!file || loading}
            >
              {loading ? (
                <span className="loading-row">
                  <span className="spinner" /> Analysing...
                </span>
              ) : "Analyse"}
            </button>
          </div>
        </div>

      </div>
    </main>
  )
}

// CSS variable helper — React inline styles can't use var() directly
const var_blue = "#2563eb"

