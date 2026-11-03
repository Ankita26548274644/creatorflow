import { useState } from "react";
import FileUploader from "../components/FileUploader";
import ValidationReport from "../components/ValidationReport";
import CleaningSummary from "../components/CleaningSummary";
import FeaturePreview from "../components/FeaturePreview";
import CSVPreview from "../components/CSVPreview";
import { uploadAndValidate } from "../services/api";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleFileSelected(selectedFile) {
    setFile(selectedFile);
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const data = await uploadAndValidate(selectedFile);
      setResult(data);
    } catch (err) {
      const detail =
        err.response?.data?.detail || err.message || "Upload failed.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setFile(null);
    setResult(null);
    setError(null);
  }

  const validationPassed = result?.validation?.passed;
  const cleaning = result?.cleaning;
  const features = result?.features;

  return (
    <div>
      <h1>Upload Your Data</h1>
      <p style={{ marginTop: "0.5rem", marginBottom: "1.5rem", color: "var(--text-muted)" }}>
        Select a CSV file containing your historical social media data. We'll
        validate it, clean it, extract features, and let you know if it's ready
        for analysis.
      </p>

      {!file && (
        <FileUploader onFileSelected={handleFileSelected} disabled={loading} />
      )}

      {loading && (
        <div style={{ marginTop: "1rem", color: "var(--text-muted)" }}>
          Uploading, validating, cleaning, and engineering features...
        </div>
      )}

      {error && (
        <div className="issue-item issue-error" style={{ marginTop: "1rem" }}>
          <span className="code">ERROR</span>
          {error}
        </div>
      )}

      {file && <CSVPreview file={file} />}

      {result && <ValidationReport result={result} />}

      {validationPassed && cleaning && <CleaningSummary cleaning={cleaning} />}

      {validationPassed && features && <FeaturePreview features={features} />}

      {file && (
        <div style={{ marginTop: "1rem" }}>
          <button className="btn btn-primary" onClick={handleReset}>
            Upload Another File
          </button>
        </div>
      )}
    </div>
  );
}