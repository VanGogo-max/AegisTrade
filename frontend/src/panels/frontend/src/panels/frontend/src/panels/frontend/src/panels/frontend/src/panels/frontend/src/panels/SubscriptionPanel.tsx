import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се върже с реалния subscription state
const useSubscription = () => {
  return {
    isLoading: false,
    isActive: false,
    tier: null
  }
}

export const SubscriptionPanel: React.FC = () => {
  const { isLoading, isActive, tier } = useSubscription()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Checking subscription…
      </div>
    )
  }

  // Empty / inactive subscription state
  if (!isActive) {
    return (
      <div style={{ padding: 16 }}>
        <h4>{emptyStatesV2.empty_subscription.title}</h4>
        <p>{emptyStatesV2.empty_subscription.description}</p>

        <button
          style={{
            marginTop: 12,
            padding: "8px 14px",
            borderRadius: 6,
            border: "none",
            cursor: "pointer"
          }}
          onClick={() => {
            // future: open billing / upgrade modal
            alert("Upgrade flow will be available soon.")
          }}
        >
          Upgrade Subscription
        </button>
      </div>
    )
  }

  // Active subscription
  return (
    <div style={{ padding: 16 }}>
      <h4>Subscription Active</h4>
      <p>Your current plan: <strong>{tier}</strong></p>

      <button
        style={{
          marginTop: 12,
          padding: "8px 14px",
          borderRadius: 6,
          border: "none",
          cursor: "pointer"
        }}
        onClick={() => {
          // future: manage subscription
          alert("Manage subscription coming soon.")
        }}
      >
        Manage Subscription
      </button>
    </div>
  )
}
