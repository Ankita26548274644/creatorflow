export default function ValidationReport({ result }) {
  if (!result) return null;

  const { validation, original_filename, size_mb } = result;
  const { passed, error_count, warning_count, prediction_enabled, errors, warnings } = validation;

  return (
    <div className="report">
      <div className="report-header">
        <div>
          <h2>Validation Report</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            {original_filename} ({size_mb} MB)
          </p>
        </div>
        <span className={`status-badge ${passed ? "status-pass" : "status-fail"}`}>
          {passed ? "PASSED" : "FAILED"}
        </span>
      </div>

      <div className="meta-grid">
        <div className="meta-item">
          <div className="label">Errors</div>
          <div className="value" style={{ color: error_count ? "var(--danger)" : "inherit" }}>
            {error_count}
          </div>
        </div>
        <div className="meta-item">
          <div className="label">Warnings</div>
          <div className="value" style={{ color: warning_count ? "var(--warning)" : "inherit" }}>
            {warning_count}
          </div>
        </div>
        <div className="meta-item">
          <div className="label">Prediction</div>
          <div className="value">
            {prediction_enabled ? "Enabled" : "Disabled"}
          </div>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="issue-list">
          <h3>Errors ({errors.length})</h3>
          {errors.map((issue, i) => (
            <div key={i} className="issue-item issue-error">
              <span className="code">{issue.code}</span>
              {issue.column && <span className="code">[{issue.column}]</span>}
              {issue.message}
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="issue-list">
          <h3>Warnings ({warnings.length})</h3>
          {warnings.map((issue, i) => (
            <div key={i} className="issue-item issue-warning">
              <span className="code">{issue.code}</span>
              {issue.column && <span className="code">[{issue.column}]</span>}
              {issue.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}