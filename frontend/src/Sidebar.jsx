// src/Sidebar.jsx

import React from "react";

export default function Sidebar() {
  return (
    <div style={{
      width: "240px",
      borderRight: "1px solid #ddd",
      padding: "15px",
      background: "#f5f5f5"
    }}>
      <button
        style={{
          width: "100%",
          padding: "12px",
          borderRadius: "8px",
          border: "none",
          background: "#4a90e2",
          color: "white",
          marginBottom: "15px"
        }}
      >
        + New Chat
      </button>

      <input
        placeholder="Search..."
        style={{
          width: "100%",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #bbb"
        }}
      />

      <div style={{ marginTop: "20px", opacity: 0.6 }}>
        Chat history (coming soon)
      </div>
    </div>
  );
}
