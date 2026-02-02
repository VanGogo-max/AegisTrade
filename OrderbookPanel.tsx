import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Тук приемаме, че по-късно ще има реален hook за orderbook
// Засега симулираме липса на данни
const useOrderbookData = () => {
  return {
    isLoading: false,
    data: []
  }
}

export const OrderbookPanel: React.FC = () => {
  const { isLoading, data } = useOrderbookData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading orderbook…
      </div>
    )
  }

  // Empty state (v2)
  if (!data || data.length === 0) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_orderbook.title}</h4>
        <p>{emptyStatesV2.empty_orderbook.description}</p>
      </div>
    )
  }

  // Normal render (когато има данни)
  return (
    <div style={{ padding: 12 }}>
      <h4>Orderbook</h4>
      {/* тук по-късно ще се рендерират bid/ask редове */}
    </div>
  )
}
