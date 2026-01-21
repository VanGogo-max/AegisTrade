// src/App.tsx

import React from "react"
import { UIContextsProvider, useUIContexts } from "./ui/ui_contexts"
import { hyperliquidTheme } from "./theme/theme_tokens"
import { i18nTokens } from "./i18n/i18n_tokens"
import { generateChartTheme } from "./chart/trading_chart_theme"
import { orderbookTokens } from "./orderbook/orderbook_tokens"
import { positionPanelTokens } from "./positions/position_panel_tokens"

// --- Sample Panel Components ---
const OrderbookPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const collapsed = layoutState.collapsed["orderbook"]
  if (collapsed) return null

  return (
    <div style={{ background: orderbookTokens.colors.backgroundColor, padding: 8 }}>
      <h4>Orderbook</h4>
      {/* Render orderbook rows here */}
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
      {/* Render chart using LightweightCharts or TradingView */}
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
      {/* Render positions */}
    </div>
  )
}

// --- Main App Component ---
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
      {/* Add other panels: trades, orders, balances, subscription, referral_dashboard */}
    </div>
  )
}

// --- Wrap with UI Contexts Provider ---
const App: React.FC = () => {
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
