import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се замени с реален positions hook
const usePositionsData = () => {
  return {
    isLoading: false,
    positions: []
  }
}

export const PositionsPanel: React.FC = () => {
  const { isLoading, positions } = usePositionsData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading positions…
      </div>
    )
  }

  // Empty state (v2)
  if (!positions || positions.length === 0) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_positions.title}</h4>
        <p>{emptyStatesV2.empty_positions.description}</p>
      </div>
    )
  }

  // Normal render (когато има позиции)
  return (
    <div style={{ padding: 12 }}>
      <h4>Open Positions</h4>
      {/* тук по-късно ще се рендерират позициите */}
    </div>
  )
}
