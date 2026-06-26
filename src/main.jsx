import React, { useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const progress = useMemo(() => {
    if (status === "idle") return 0;
    if (status === "uploading") return 35;
    if (status === "processing") return 78;
    if (status === "complete") return 100;
    return 0;
  }, [status]);

  const statusText = {
    idle: "Waiting for sheet music...",
    uploading: "Uploading image...",
    processing: "Analyzing notes and generating MIDI...",
    complete: "Processing complete.",
    error: "Something needs attention.",
  }[status];

  function pickFile(selectedFile) {
    if (!selectedFile) return;
    setFile(selectedFile);
    setResult(null);
    setError("");
    setStatus("idle");
  }

  async function processImage() {
    if (!file) {
      setError("Choose a sheet music image first.");
      return;
    }

    setError("");
    setResult(null);
    setStatus("uploading");

    const formData = new FormData();
    formData.append("sheet", file);

    try {
      setTimeout(() => setStatus((current) => (current === "uploading" ? "processing" : current)), 350);
      const response = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || "Processing failed.");
      }

      setResult(payload);
      setStatus("complete");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  function resultUrl(name) {
    if (!result) return "";
    return `${API_BASE}/api/results/${result.jobId}/${name}`;
  }

  function downloadUrl(name) {
    if (!result) return "";
    return `${API_BASE}/api/download/${result.jobId}/${name}`;
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-mark">♪</div>
        <div>
          <h1>Sheet Music Note Identifier & Player</h1>
          <p>Convert a sheet image into detected notes and a downloadable MIDI file.</p>
        </div>
      </header>

      <section className="workspace">
        <div className="panel upload-panel">
          <div className="section-title">
            <span>↥</span>
            <h2>Upload Sheet Music</h2>
          </div>

          <button
            className={`drop-zone ${isDragging ? "dragging" : ""}`}
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragging(false);
              pickFile(event.dataTransfer.files?.[0]);
            }}
          >
            <span className="plus">+</span>
            <strong>{file ? file.name : "Drag & drop or click to upload"}</strong>
            <small>PNG, JPG, or JPEG</small>
          </button>

          <input
            ref={inputRef}
            className="visually-hidden"
            type="file"
            accept="image/png,image/jpeg"
            onChange={(event) => pickFile(event.target.files?.[0])}
          />

          <button className="primary-action" type="button" onClick={processImage} disabled={!file || status === "uploading" || status === "processing"}>
            Process Image
          </button>

          {error && <div className="error-box">{error}</div>}

          <div className="status-block">
            <div className="section-title">
              <span>▤</span>
              <h2>Processing Status</h2>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <div className="status-row">
              <span>{statusText}</span>
              <strong>{progress}%</strong>
            </div>
          </div>
        </div>

        <div className="panel results-panel">
          <div className="section-title">
            <span>♬</span>
            <h2>Identified Notes</h2>
          </div>

          {result ? (
            <>
              <div className="preview-frame">
                <img src={resultUrl(result.files.detected)} alt="Detected notes preview" />
              </div>

              <div className="summary-grid">
                <div>
                  <span>Detected</span>
                  <strong>{result.summary.detectedNotes}</strong>
                </div>
                <div>
                  <span>MIDI notes</span>
                  <strong>{result.summary.midiNotes}</strong>
                </div>
                <div>
                  <span>Staff lines</span>
                  <strong>{result.summary.staffLines}</strong>
                </div>
              </div>

              <div className="notes-list">
                {result.notes.length ? (
                  result.notes.map((note, index) => (
                    <div className="note-row" key={`${note.x}-${note.y}-${index}`}>
                      <span>Note {index + 1}</span>
                      <strong>{note.pitch}</strong>
                      <span>{note.typeLabel}</span>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">No notes were detected in this image.</div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-preview">
              <span>♩</span>
              <p>Detected notes and preview images will appear here after processing.</p>
            </div>
          )}
        </div>

        <aside className="panel action-panel">
          <div className="section-title">
            <span>▶</span>
            <h2>Music Output</h2>
          </div>

          <div className="player-card">
            <div className="player-title">Converted Music Player (Coming Soon)</div>
            <div className="controls">
              <button type="button" disabled>▶</button>
              <button type="button" disabled>■</button>
              <button type="button" disabled>◀</button>
              <button type="button" disabled>▶▶</button>
            </div>
            <div className="fake-slider">
              <span />
            </div>
          </div>

          <div className="settings">
            <label>
              Instrument
              <select defaultValue="recorder">
                <option value="recorder">Recorder</option>
                <option value="piano">Piano</option>
                <option value="violin">Violin</option>
              </select>
            </label>
            <label>
              Tempo
              <select defaultValue="100">
                <option value="80">80 BPM</option>
                <option value="100">100 BPM</option>
                <option value="120">120 BPM</option>
              </select>
            </label>
          </div>

          <div className="download-actions">
            <a className={result ? "download-button" : "download-button disabled"} href={result ? downloadUrl(result.files.midi) : undefined}>
              ⇩ Download MIDI
            </a>
            {result && (
              <a className="download-button secondary" href={resultUrl(result.files.cleaned)} target="_blank" rel="noreferrer">
                View Cleaned Image
              </a>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
