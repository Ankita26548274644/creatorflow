import { useRef, useState } from "react";

export default function FileUploader({ onFileSelected, disabled }) {
  const [dragover, setDragover] = useState(false);
  const inputRef = useRef(null);

  function handleClick() {
    if (!disabled) inputRef.current?.click();
  }

  function handleChange(e) {
    const file = e.target.files?.[0];
    if (file) onFileSelected(file);
    e.target.value = "";
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragover(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelected(file);
  }

  function handleDragOver(e) {
    e.preventDefault();
    if (!disabled) setDragover(true);
  }

  function handleDragLeave() {
    setDragover(false);
  }

  return (
    <div
      className={`uploader ${dragover ? "dragover" : ""}`}
      onClick={handleClick}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      style={disabled ? { opacity: 0.6, cursor: "not-allowed" } : undefined}
    >
      <div className="icon">📁</div>
      <div className="label">
        {dragover
          ? "Drop your CSV here"
          : "Click to select or drag and drop your CSV"}
      </div>
      <div className="hint">
        Only .csv files · Max 5 MB · At least 10 rows required
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        onChange={handleChange}
        disabled={disabled}
      />
    </div>
  );
}