import React from "react"
import { useUIContexts } from "../ui/ui_contexts"

export const ReferralPanel: React.FC = () => {
  const { referralRank, layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["referral_dashboard"]
  if (collapsed) return null

  return (
    <div style={{ background: "#0D1117", padding: 8, borderRadius: 4, minHeight: 100 }}>
      <h4 style={{ color: "#00BFFF" }}>Referral Dashboard</h4>
      <div style={{ color: "#FFF", fontSize: 12 }}>
        Rank: {referralRank?.name || "None"}
      </div>
      <div style={{ color: "#FFF", fontSize: 12 }}>
        Rewards: {referralRank?.rewards || 0} USDT
      </div>
    </div>
  )
}
