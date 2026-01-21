import React from "react"
import { useUIContexts } from "../ui/ui_contexts"

export const SubscriptionPanel: React.FC = () => {
  const { subscriptionTier, layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["subscription"]
  if (collapsed) return null

  return (
    <div style={{ background: "#0D1117", padding: 8, borderRadius: 4, minHeight: 100 }}>
      <h4 style={{ color: "#FFD700" }}>Subscription</h4>
      <div style={{ color: "#FFF", fontSize: 12 }}>Current Tier: {subscriptionTier}</div>
      <div style={{ color: "#FFF", fontSize: 12 }}>Monthly: 5 USDT</div>
    </div>
  )
}
