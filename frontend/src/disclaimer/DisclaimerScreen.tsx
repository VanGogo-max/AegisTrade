// frontend/src/disclaimer/DisclaimerScreen.tsx

import React, { useState } from "react"

interface DisclaimerScreenProps {
  onAccept: () => void
}

const DisclaimerScreen: React.FC<DisclaimerScreenProps> = ({ onAccept }) => {
  const [accepted, setAccepted] = useState(false)

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#0b0f14",
        color: "#e5e7eb",
        padding: 24,
      }}
    >
      <div
        style={{
          maxWidth: 640,
          backgroundColor: "#111827",
          padding: 24,
          borderRadius: 8,
          boxShadow: "0 0 20px rgba(0,0,0,0.4)",
        }}
      >
        <h2 style={{ marginBottom: 16 }}>Important Information</h2>

        <p style={{ marginBottom: 12 }}>
          This application is a <strong>non-custodial trading interface</strong>.
        </p>

        <ul style={{ marginBottom: 16, lineHeight: 1.6 }}>
          <li>The application does not hold, store, or control user funds.</li>
          <li>All trading actions are executed through user-connected exchanges.</li>
          <li>The application does not provide financial or investment advice.</li>
          <li>Cryptocurrency trading involves significant risk, including loss of funds.</li>
          <li>Past performance or simulations do not guarantee future results.</li>
          <li>The user is solely responsible for all trading decisions and outcomes.</li>
        </ul>

        <label style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
          <input
            type="checkbox"
            checked={accepted}
            onChange={(e) => setAccepted(e.target.checked)}
            style={{ marginRight: 8 }}
          />
          I have read and agree to the information above
        </label>

        <button
          disabled={!accepted}
          onClick={onAccept}
          style={{
            width: "100%",
            padding: "10px 0",
            backgroundColor: accepted ? "#2563eb" : "#374151",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            cursor: accepted ? "pointer" : "not-allowed",
            fontSize: 16,
          }}
        >
          Continue
        </button>
      </div>
    </div>
  )
}

export default DisclaimerScreen
