// src/App.tsx

import React, { useState } from "react"
import { UIContextsProvider, useUIContexts } from "./ui/ui_contexts"
import { hyperliquidTheme } from "./theme/theme_tokens"
import { i18nTokens } from "./i18n/i18n_tokens"
import { generateChartTheme } from "./chart/trading_chart_theme"
import { orderbookTokens } from "./orderbook/orderbook_tokens"
import { positionPanelTokens } from "./positions/position_panel_tokens"

// --- User messages & empty states ---
import messages from "./user_messages.json"
import emptyStates from "./empty_states.json"

// --- Disclaimer ---
import DisclaimerScreen from "./disclaimer/DisclaimerScreen"

// --- Sample Panel Components ---
const OrderbookPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["orderbook"]
  if (collapsed) return null

  return (
    <div style={{ background: orderbookTokens.colors.backgroundColor, padding: 8 }}>
      <h4>Orderbook</h4>
      <p>{emptyStates.empty_orderbook.description}</p>
    </div>
  )
}

const ChartPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["chart"]
  if (collapsed) return null

  const chartTheme = generateChartTheme(hyperliquidTheme, true)

  return (
    <div style={{ background: chartTheme.backgroundColor, padding: 8 }}>
      <h4>Chart</h4>
      <p>{emptyStates.empty_chart.description}</p>
    </div>
  )
}

const PositionsPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["positions"]
  if (collapsed) return null

  return (
    <div style={{ background: positionPanelTokens.colors.backgroundColor, padding: 8 }}>
      <h4>Open Positions</h4>
      <p>{emptyStates.empty_positions.description}</p>
    </div>
  )
}

// --- Main App Content (НЕПРОМЕНЕНО) ---
const AppContent: React.FC = () => {
  return (
    <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(12, 1fr)" }}>
      <div style={{ gridColumn: "span 3" }}>
        <OrderbookPanel />
      </div>
      <div style={{ gridColumn: "span 6" }}>
        <ChartPanel />
      </div>
      <div style={{ gridColumn: "span 3" }}>
        <PositionsPanel />
      </div>
    </div>
  )
}

// --- Root App ---
const App: React.FC = () => {
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false)

  // 1️⃣ Disclaimer gate
  if (!disclaimerAccepted) {
    return <DisclaimerScreen onAccept={() => setDisclaimerAccepted(true)} />
  }

  // 2️⃣ Original application (unchanged)
  return (
    <UIContextsProvider
      theme={hyperliquidTheme}
      i18n={i18nTokens}
      device="desktop"
      kycCompleted={true}
      riskLevel={20}
    >
      <AppContent />
    </UIContextsProvider>
  )
}

export default App
