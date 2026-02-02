import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се замени с реален chart / market data hook
const useChartData = () => {
  return {
    isLoading: false,
    data: null
  }
}

export const ChartPanel: React.FC = () => {
  const { isLoading, data } = useChartData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading chart data…
      </div>
    )
  }

  // Empty state (v2)
  if (!data) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_chart.title}</h4>
        <p>{emptyStatesV2.empty_chart.description}</p>
      </div>
    )
  }

  // Normal render (когато има данни)
  return (
    <div style={{ padding: 12 }}>
      <h4>Chart</h4>
      {/* тук по-късно ще се рендерира реалният chart (TradingView / Lightweight Charts) */}
    </div>
  )
}
