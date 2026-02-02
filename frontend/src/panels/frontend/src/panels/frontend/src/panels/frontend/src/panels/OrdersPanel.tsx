import React from "react"
import emptyStatesV2 from "../empty_states_v2.json"

// ⚠️ Placeholder hook – по-късно ще се замени с реален orders hook
const useOrdersData = () => {
  return {
    isLoading: false,
    orders: []
  }
}

export const OrdersPanel: React.FC = () => {
  const { isLoading, orders } = useOrdersData()

  // Loading state
  if (isLoading) {
    return (
      <div style={{ padding: 12, opacity: 0.7 }}>
        Loading orders…
      </div>
    )
  }

  // Empty state (v2)
  if (!orders || orders.length === 0) {
    return (
      <div style={{ padding: 12 }}>
        <h4>{emptyStatesV2.empty_orders.title}</h4>
        <p>{emptyStatesV2.empty_orders.description}</p>
      </div>
    )
  }

  // Normal render (когато има активни поръчки)
  return (
    <div style={{ padding: 12 }}>
      <h4>Open Orders</h4>
      {/* тук по-късно ще се рендерират поръчките */}
    </div>
  )
}
