import { useEffect, useState } from "react";

export default function CSVPreview({ file }) {
  const [rows, setRows] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!file) {
      setRows([]);
      setHeaders([]);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lines = text.split(/\r?\n/).filter((l) => l.trim() !== "");
        if (lines.length === 0) {
          setError("File is empty.");
          return;
        }
        const headerLine = lines[0].split(",");
        const dataLines = lines.slice(1, 6).map((line) => line.split(","));
        setHeaders(headerLine);
        setRows(dataLines);
        setError(null);
      } catch (err) {
        setError("Could not parse preview.");
      }
    };
    reader.readAsText(file);
  }, [file]);

  if (!file) return null;
  if (error) return <div className="preview">{error}</div>;

  return (
    <div className="preview">
      <h3>Preview (first 5 rows)</h3>
      <table>
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}