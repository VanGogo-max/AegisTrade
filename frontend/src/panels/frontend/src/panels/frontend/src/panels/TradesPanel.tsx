import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се замени с реален trades hook
const useTradesData = () => {
  return {
    isLoading: false,
    trades: []
  }
}

export const TradesPanel: React.FC = () => {
  const { isLoading, trades } = useTradesData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading trades…
      </div>
    )
  }

  // Empty state (v2)
  if (!trades || trades.length === 0) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_trades.title}</h4>
        <p>{emptyStatesV2.empty_trades.description}</p>
      </div>
    )
  }

  // Normal render (когато има сделки)
  return (
    <div style={{ padding: 12 }}>
      <h4>Trade History</h4>
      {/* тук по-късно ще се рендерират trades */}
    </div>
  )
}
