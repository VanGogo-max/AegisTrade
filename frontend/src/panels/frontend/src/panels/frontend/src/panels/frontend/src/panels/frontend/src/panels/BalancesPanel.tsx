import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се замени с реален balances hook
const useBalancesData = () => {
  return {
    isLoading: false,
    balances: []
  }
}

export const BalancesPanel: React.FC = () => {
  const { isLoading, balances } = useBalancesData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading balances…
      </div>
    )
  }

  // Empty state (v2)
  if (!balances || balances.length === 0) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_balances.title}</h4>
        <p>{emptyStatesV2.empty_balances.description}</p>
      </div>
    )
  }

  // Normal render (когато има баланси)
  return (
    <div style={{ padding: 12 }}>
      <h4>Balances</h4>
      {/* тук по-късно ще се рендерират балансите */}
    </div>
  )
}
