import React, { useState } from "react";
import ChatWindow from "./ChatWindow";

export default function MainPage() {
  const [description, setDescription] = useState("");
  const [queries, setQueries] = useState("");
  const [xmlText, setXmlText] = useState("");
  const [verifyOutput, setVerifyOutput] = useState("");
  const [downloadName, setDownloadName] = useState("model.xml");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    try {
      if (!description.trim()) {
        alert("Description cannot be empty.");
        return;
      }

      // Convert user text → list of queries
      let queryList = queries
        .split("\n")
        .map((q) => q.trim())
        .filter((q) => q.length > 0);

      if (!Array.isArray(queryList)) {
        alert("Queries must be a list.");
        return;
      }

      setLoading(true);

      const res = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: description,
          queries: queryList,
        }),
      });

      const data = await res.json();
      console.log("Backend response:", data);

      if (!res.ok) {
        alert(`Error: ${data.error || "Backend error"}`);
        return;
      }

      // Accept ANY backend naming conventions
      setXmlText(
        data.xml_text ||
        data.xml ||
        data.model_xml ||
        data.output_xml ||
        ""
      );

      setVerifyOutput(
        data.verify_output ||
        data.verification ||
        data.verify ||
        data.verifier_output ||
        ""
      );

      setDownloadName(
        data.xml_filename ||
        data.filename ||
        "uppaal_model.xml"
      );

    } catch (err) {
      console.error("Frontend error:", err);
      alert("Unexpected frontend error. Check console.");
    } finally {
      setLoading(false);
    }
  }

  // Download XML file
  function downloadXML() {
    const blob = new Blob([xmlText], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = downloadName;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ padding: "30px", width: "100%", maxWidth: "900px", margin: "auto" }}>
      
      {/* Description Field */}
      <h2>Describe Your UPPAAL Model</h2>
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Describe the model, templates, clocks, transitions, etc."
        style={{
          width: "100%",
          height: "180px",
          border: "1px solid #ccc",
          borderRadius: "6px",
          padding: "10px",
          fontSize: "14px",
          resize: "vertical"
        }}
      />

      {/* Queries Field */}
      <h3 style={{ marginTop: "25px" }}>Queries</h3>
      <textarea
        value={queries}
        onChange={(e) => setQueries(e.target.value)}
        placeholder="Example:\nA[] x >= 0\nE<> P.id1\nA<> not deadlock"
        style={{
          width: "100%",
          height: "150px",
          border: "1px solid #ccc",
          borderRadius: "6px",
          padding: "10px",
          fontSize: "14px",
          fontFamily: "monospace",
          resize: "vertical"
        }}
      />

      {/* Button */}
      <button
        onClick={handleSend}
        disabled={loading}
        style={{
          marginTop: "25px",
          padding: "12px 25px",
          background: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "8px",
          fontSize: "17px",
          cursor: "pointer",
          width: "220px",
          fontWeight: "bold"
        }}
      >
        {loading ? "Processing..." : "Generate & Verify"}
      </button>

      {/* XML Output */}
      {xmlText && (
        <div style={{ marginTop: "40px" }}>
          <h2>Your Model XML:</h2>
          <pre
            style={{
              background: "#f7f7f7",
              padding: "15px",
              borderRadius: "6px",
              maxHeight: "400px",
              overflow: "auto",
              border: "1px solid #ddd"
            }}
          >
            {xmlText}
          </pre>

          {/* Download Button */}
          <button
            onClick={downloadXML}
            style={{
              marginTop: "10px",
              padding: "10px 20px",
              background: "#059669",
              color: "white",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            Download XML
          </button>
        </div>
      )}

      {/* Verification Output */}
      {verifyOutput && (
        <div style={{ marginTop: "40px" }}>
          <h2>Verification Results:</h2>
          <pre
            style={{
              background: "#f0f0f0",
              padding: "15px",
              borderRadius: "6px",
              maxHeight: "400px",
              overflowY: "auto",
              border: "1px solid #ddd",
              whiteSpace: "pre-wrap"
            }}
          >
            {verifyOutput}
          </pre>
        </div>
      )}
    </div>
  );
}
