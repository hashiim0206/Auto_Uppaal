// src/ChatWindow.jsx
import React from "react";

export default function ChatWindow({
  description,
  setDescription,
  queries,
  setQueries,
  onSend,
  xmlOutput,
  verificationOutput,
  loading
}) {
  const handleDownload = () => {
    if (!xmlOutput) return;
    const blob = new Blob([xmlOutput], { type: "text/xml" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "model.xml";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: "20px", width: "100%" }}>
      
      {/* ===== INPUT SECTION ===== */}
      <div
        style={{
          background: "#fafafa",
          padding: "20px",
          borderRadius: "10px",
          boxShadow: "0 0 4px rgba(0,0,0,0.08)",
          marginBottom: "25px"
        }}
      >
        <h2 style={{ marginBottom: "10px", fontWeight: 600 }}>
          Describe Your UPPAAL Model
        </h2>

        <textarea
          placeholder="Enter natural-language UPPAAL model description..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{
            width: "100%",
            height: "140px",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            fontSize: "15px",
            resize: "vertical",
          }}
        />

        <h3 style={{ marginTop: "20px", marginBottom: "8px", fontWeight: 600 }}>
          Queries
        </h3>

        <textarea
          placeholder="Enter UPPAAL verification queries..."
          value={queries}
          onChange={(e) => setQueries(e.target.value)}
          style={{
            width: "100%",
            height: "120px",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            fontSize: "15px",
            resize: "vertical",
          }}
        />

        <div style={{ textAlign: "center", marginTop: "20px" }}>
          <button
            onClick={onSend}
            disabled={loading}
            style={{
              padding: "12px 35px",
              borderRadius: "8px",
              background: loading ? "#7aa7ff" : "#346dff",
              color: "white",
              border: "none",
              fontSize: "17px",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Processing..." : "Generate & Verify"}
          </button>
        </div>
      </div>

      {/* ===== XML OUTPUT ===== */}
      {xmlOutput && (
        <div
          style={{
            background: "white",
            padding: "20px",
            borderRadius: "10px",
            boxShadow: "0 0 4px rgba(0,0,0,0.1)",
            marginBottom: "25px"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <h2 style={{ marginBottom: "10px", fontWeight: 600 }}>
              Generated UPPAAL XML
            </h2>
            <button
              onClick={handleDownload}
              style={{
                padding: "6px 14px",
                background: "#1c9c40",
                color: "white",
                borderRadius: "8px",
                border: "none",
                cursor: "pointer",
              }}
            >
              Download XML
            </button>
          </div>

          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "15px",
              background: "#fcfcfc",
              maxHeight: "350px",
              overflow: "auto",
              fontFamily: "monospace",
              whiteSpace: "pre-wrap"
            }}
          >
            {xmlOutput}
          </div>
        </div>
      )}

      {/* ===== VERIFICATION RESULTS ===== */}
      {verificationOutput && (
        <div
          style={{
            background: "#ffffff",
            padding: "20px",
            borderRadius: "10px",
            boxShadow: "0 0 4px rgba(0,0,0,0.1)"
          }}
        >
          <h2 style={{ marginBottom: "10px", fontWeight: 600 }}>
            Verification Results
          </h2>

          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "15px",
              background: "#fdfdfd",
              maxHeight: "400px",
              overflowY: "auto",
              fontFamily: "monospace",
              whiteSpace: "pre-wrap"
            }}
          >
            {verificationOutput}
          </div>
        </div>
      )}
    </div>
  );
}
