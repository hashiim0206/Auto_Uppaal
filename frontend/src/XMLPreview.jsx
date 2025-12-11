import React from "react";

export default function XMLPreview({ xml, verifyOutput, downloadUrl }) {
  // If XML is not available yet, show nothing
  if (!xml) {
    return (
      <div style={{ padding: "1rem", color: "#666" }}>
        XML output will appear here after generation.
      </div>
    );
  }

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Your Model XML:</h3>

      <pre
        style={{
          background: "#f7f7f7",
          padding: "1rem",
          borderRadius: "6px",
          maxHeight: "300px",
          overflowY: "auto",
          whiteSpace: "pre-wrap",
        }}
      >
        {xml}
      </pre>

      {downloadUrl && (
        <a
          href={downloadUrl}
          download="model.xml"
          style={{
            display: "inline-block",
            marginTop: "10px",
            background: "#4a90e2",
            color: "#fff",
            padding: "0.5rem 1rem",
            borderRadius: "4px",
            textDecoration: "none",
          }}
        >
          Download model.xml
        </a>
      )}

      {verifyOutput && (
        <>
          <h3 style={{ marginTop: "2rem" }}>Verification Results:</h3>
          <pre
            style={{
              background: "#eef2f4",
              padding: "1rem",
              borderRadius: "6px",
              whiteSpace: "pre-wrap",
            }}
          >
            {verifyOutput}
          </pre>
        </>
      )}
    </div>
  );
}
