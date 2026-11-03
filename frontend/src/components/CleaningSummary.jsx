export default function CleaningSummary({ cleaning }) {
  if (!cleaning) return null;

  const { original_rows, final_rows, rows_removed, rows_modified, actions } = cleaning;

  return (
    <div className="report" style={{ marginTop: "1.5rem" }}>
      <div className="report-header">
        <div>
          <h2>Cleaning Summary</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            {actions.length} cleaning action(s) applied
          </p>
        </div>
      </div>

      <div className="meta-grid">
        <div className="meta-item">
          <div className="label">Original rows</div>
          <div className="value">{original_rows}</div>
        </div>
        <div className="meta-item">
          <div className="label">Final rows</div>
          <div className="value">{final_rows}</div>
        </div>
        <div className="meta-item">
          <div className="label">Rows removed</div>
          <div className="value" style={{ color: rows_removed ? "var(--warning)" : "inherit" }}>
            {rows_removed}
          </div>
        </div>
        <div className="meta-item">
          <div className="label">Rows modified</div>
          <div className="value" style={{ color: rows_modified ? "var(--warning)" : "inherit" }}>
            {rows_modified}
          </div>
        </div>
      </div>

      {actions.length > 0 && (
        <div className="issue-list">
          <h3>Actions ({actions.length})</h3>
          {actions.map((a, i) => (
            <div key={i} className="issue-item" style={{ background: "#eff6ff", borderColor: "#3b82f6" }}>
              <span className="code">{a.action}</span>
              {a.column && <span className="code">[{a.column}]</span>}
              {a.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}