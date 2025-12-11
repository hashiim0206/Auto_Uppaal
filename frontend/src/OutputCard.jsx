// src/OutputCard.jsx

import React, { useState } from "react";

export default function OutputCard({ xml, log, onClear }) {
  const [showLog, setShowLog] = useState(false);

  const downloadFile = () => {
    const blob = new Blob([xml], { type: "text/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "model.xml";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        padding: "12px 16px",
        background: "#fff8e1",
        borderBottom: "1px solid #ddd",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h3 style={{ margin: 0 }}>Generated XML</h3>
        <div>
          <button
            onClick={downloadFile}
            style={{
              marginRight: "8px",
              padding: "6px 12px",
              borderRadius: "6px",
              border: "none",
              background: "#4caf50",
              color: "white",
              cursor: "pointer",
            }}
          >
            ⬇ Download XML
          </button>
          <button
            onClick={onClear}
            style={{
              padding: "6px 12px",
              borderRadius: "6px",
              border: "none",
              background: "#e53935",
              color: "white",
              cursor: "pointer",
            }}
          >
            Clear
          </button>
        </div>
      </div>

      {log && (
        <div style={{ marginTop: "8px" }}>
          <button
            onClick={() => setShowLog((s) => !s)}
            style={{
              padding: "4px 8px",
              fontSize: "12px",
              borderRadius: "4px",
              border: "1px solid #aaa",
              background: "white",
              cursor: "pointer",
            }}
          >
            {showLog ? "Hide verifyta log" : "Show verifyta log"}
          </button>

          {showLog && (
            <pre
              style={{
                marginTop: "6px",
                maxHeight: "160px",
                overflowY: "auto",
                background: "#fff",
                border: "1px solid #eee",
                padding: "8px",
                fontSize: "11px",
              }}
            >
              {log}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
