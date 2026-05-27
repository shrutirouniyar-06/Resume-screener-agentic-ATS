import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import { getRoles, screenResume } from "../../lib/api";
import { useEffect } from "react";
import { Upload, CheckCircle, XCircle, Loader, FileText } from "lucide-react";
import "./UploadPage.css";

function FileItem({ name, status, error, size }) {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  return (
    <div className="file-item">
      <FileText size={14} />
      <div className="file-info">
        <span className="file-name">{name}</span>
        <span className="file-size">{size ? formatFileSize(size) : ""}</span>
      </div>
      <span className="file-status">
        {status === "pending" && (
          <span className="status-pending">Waiting…</span>
        )}
        {status === "processing" && <Loader size={13} className="spin" />}
        {status === "done" && <CheckCircle size={14} color="#1D9E75" />}
        {status === "error" && (
          <span className="status-error" title={error}>
            <XCircle size={14} color="#E24B4A" />
          </span>
        )}
      </span>
    </div>
  );
}

export default function UploadPage() {
  const navigate = useNavigate();
  const [roles, setRoles] = useState([]);
  const [roleId, setRoleId] = useState("");
  const [files, setFiles] = useState([]); // [{file, status, error, size}]
  const [running, setRunning] = useState(false);
  const [sizeWarning, setSizeWarning] = useState("");

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  useEffect(() => {
    getRoles().then((r) => {
      setRoles(r);
      if (r.length) setRoleId(r[0].id);
    });
  }, []);

  const onDrop = useCallback((accepted, rejected) => {
    setSizeWarning("");

    if (rejected.length > 0) {
      setSizeWarning(`${rejected.length} file(s) rejected: file size exceeded 10MB`);
    }

    const newFiles = accepted
      .filter((f) => f.size <= MAX_FILE_SIZE)
      .map((f) => ({ file: f, status: "pending", error: null, size: f.size }));

    if (newFiles.length > 0) {
      setFiles((prev) => [...prev, ...newFiles]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
    },
    maxSize: MAX_FILE_SIZE,
  });

  const handleScreen = async () => {
    if (!roleId || files.length === 0) return;
    setRunning(true);
    for (let i = 0; i < files.length; i++) {
      setFiles((prev) =>
        prev.map((f, idx) => (idx === i ? { ...f, status: "processing" } : f)),
      );
      try {
        await screenResume(files[i].file, roleId);
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: "done" } : f)),
        );
      } catch (e) {
        const msg = e.response?.data?.error || e.message || "Screening failed";
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: "error", error: msg } : f,
          ),
        );
      }
    }
    setRunning(false);
  };

  const handleViewResults = () => {
    navigate("/candidates");
  };

  const allDone =
    files.length > 0 &&
    files.every((f) => f.status === "done" || f.status === "error");
  const doneCount = files.filter((f) => f.status === "done").length;
  const errorCount = files.filter((f) => f.status === "error").length;

  return (
    <div className="page">
      <div className="topbar">
        <div className="page-title">Upload resumes</div>
      </div>
      <div className="content" style={{ maxWidth: 640 }}>
        <div className="upload-card">
          <div className="field-row">
            <label className="field-label">Screen against role</label>
            <select
              value={roleId}
              onChange={(e) => setRoleId(e.target.value)}
              className="field-select"
            >
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title}
                </option>
              ))}
              {roles.length === 0 && (
                <option disabled>No roles yet — create one first</option>
              )}
            </select>
          </div>

          <div
            {...getRootProps()}
            className={`dropzone${isDragActive ? " active" : ""}`}
          >
            <input {...getInputProps()} />
            <Upload size={28} color="#aaa" />
            <div className="drop-title">
              {isDragActive ? "Drop files here…" : "Drag & drop resumes"}
            </div>
            <div className="drop-sub">
              PDF, DOCX, or TXT · multiple files supported
            </div>
            <button type="button" className="btn" style={{ marginTop: 10 }}>
              Browse files
            </button>
          </div>

          {sizeWarning && (
            <div className="size-warning">
              <XCircle size={14} color="#E24B4A" />
              <span>{sizeWarning}</span>
            </div>
          )}

          {files.length > 0 && (
            <div className="file-list">
              {files.map((f, i) => (
                <FileItem
                  key={i}
                  name={f.file.name}
                  status={f.status}
                  error={f.error}
                  size={f.size}
                />
              ))}
            </div>
          )}

          {running && (
            <div className="screening-progress">
              <div className="progress-text">
                Screening in progress: {doneCount} of {files.length} completed
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${(doneCount / files.length) * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          {allDone && files.length > 0 && (
            <div className={`completion-message ${errorCount > 0 ? "with-errors" : "success"}`}>
              <div className="completion-header">
                {errorCount === 0 ? (
                  <>
                    <CheckCircle size={16} color="#1D9E75" />
                    <span>All resumes screened successfully!</span>
                  </>
                ) : (
                  <>
                    <XCircle size={16} color="#E24B4A" />
                    <span>Screening completed with {errorCount} error{errorCount !== 1 ? "s" : ""}</span>
                  </>
                )}
              </div>
              <div className="completion-details">
                {doneCount} successful • {errorCount} failed
              </div>
              <div className="completion-action">
                <span className="navigate-text">View your results in the Candidates tab →</span>
                <button className="btn btn-link" onClick={handleViewResults} style={{ marginTop: 8 }}>
                  Go to Candidates
                </button>
              </div>
            </div>
          )}

          <div className="upload-actions">
            {allDone ? (
              <button className="btn btn-primary" onClick={handleViewResults}>
                <CheckCircle size={14} /> View results ({doneCount} screened)
              </button>
            ) : (
              <button
                className="btn btn-primary"
                disabled={!roleId || files.length === 0 || running}
                onClick={handleScreen}
              >
                {running ? (
                  <>
                    <Loader size={14} className="spin" /> Screening…
                  </>
                ) : (
                  <>
                    <Upload size={14} /> Screen{" "}
                    {files.length > 0
                      ? `${files.length} resume${files.length > 1 ? "s" : ""}`
                      : "resumes"}
                  </>
                )}
              </button>
            )}
            {files.length > 0 && !running && (
              <button className="btn" onClick={() => setFiles([])}>
                Clear all
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
