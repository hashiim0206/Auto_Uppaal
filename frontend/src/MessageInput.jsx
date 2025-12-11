import React from "react";

export default function MessageInput({ onFileSelect }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
      <label
        style={{
          padding: "10px",
          borderRadius: "8px",
          cursor: "pointer",
          border: "1px solid #aaa"
        }}
        title="Upload a file"
      >
        📎
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => onFileSelect(e.target.files[0])}
        />
      </label>
    </div>
  );
}
