export default function FeaturePreview({ features }) {
  if (!features) return null;

  const { rows, features_created, final_columns, actions, sample } = features;

  return (
    <div className="report" style={{ marginTop: "1.5rem" }}>
      <div className="report-header">
        <div>
          <h2>Feature Engineering</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            {features_created} new feature(s) derived from {rows} rows
          </p>
        </div>
        <span className="status-badge status-pass">
          {features_created} FEATURES
        </span>
      </div>

      <div className="meta-grid">
        <div className="meta-item">
          <div className="label">Rows</div>
          <div className="value">{rows}</div>
        </div>
        <div className="meta-item">
          <div className="label">Final columns</div>
          <div className="value">{final_columns.length}</div>
        </div>
        <div className="meta-item">
          <div className="label">Features created</div>
          <div className="value">{features_created}</div>
        </div>
      </div>

      {actions.length > 0 && (
        <div className="issue-list">
          <h3>Feature families</h3>
          {Object.entries(
            actions.reduce((acc, a) => {
              acc[a.family] = acc[a.family] || [];
              acc[a.family].push(a);
              return acc;
            }, {})
          ).map(([family, items]) => (
            <div key={family} className="issue-item" style={{ background: "#f0fdf4", borderColor: "var(--success)" }}>
              <span className="code">{family.toUpperCase()}</span>
              {items.length} feature(s): {items.map((i) => i.column).join(", ")}
            </div>
          ))}
        </div>
      )}

      {sample && sample.length > 0 && (
        <div className="preview" style={{ marginTop: "1.5rem" }}>
          <h3>Feature preview (first {sample.length} rows)</h3>
          <table>
            <thead>
              <tr>
                {Object.keys(sample[0]).map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sample.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((val, j) => (
                    <td key={j}>
                      {typeof val === "number" ? val.toFixed(4) : String(val ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}