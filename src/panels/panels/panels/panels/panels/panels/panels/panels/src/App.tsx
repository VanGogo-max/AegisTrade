// src/App.tsx

import React, { useEffect } from "react"
import { UIContextsProvider, useUIContexts } from "./ui/ui_contexts"
import { hyperliquidTheme } from "./theme/theme_tokens"
import { i18nTokens } from "./i18n/i18n_tokens"
import { PanelKey } from "./permissions/ui_permissions"
import { ResponsiveDragLayout } from "./layout/responsive_drag_layout"

// Panels
import { OrderbookPanel } from "./panels/OrderbookPanel"
import { ChartPanel } from "./panels/ChartPanel"
import { PositionsPanel } from "./panels/PositionsPanel"
import { TradesPanel } from "./panels/TradesPanel"
import { OrdersPanel } from "./panels/OrdersPanel"
import { BalancesPanel } from "./panels/BalancesPanel"
import { SubscriptionPanel } from "./panels/SubscriptionPanel"
import { ReferralPanel } from "./panels/ReferralPanel"

// --- Persistent Layout Hook ---
const usePersistedLayout = () => {
  const { layoutState } = useUIContexts()
  useEffect(() => {
    const serialized = JSON.stringify(layoutState)
    localStorage.setItem("dexLayout", serialized)
  }, [layoutState])
}

// --- Responsive Breakpoints ---
const responsiveBreakpoints = {
  lg: 1200,
  md: 996,
  sm: 768,
  xs: 480
}

// --- App Content ---
const AppContent: React.FC = () => {
  usePersistedLayout()

  const children: Record<PanelKey, React.ReactNode> = {
    orderbook: <OrderbookPanel />,
    chart: <ChartPanel />,
    positions: <PositionsPanel />,
    trades: <TradesPanel />,
    orders: <OrdersPanel />,
    balances: <BalancesPanel />,
    subscription: <SubscriptionPanel />,
    referral_dashboard: <ReferralPanel />
  }

  return (
    <ResponsiveDragLayout
      children={children}
      breakpoints={responsiveBreakpoints} // adaptive mobile layout
      rowHeight={30}
      cols={{ lg: 12, md: 12, sm: 6, xs: 4 }} // responsive columns
    />
  )
}

// --- Final App ---
const App: React.FC = () => {
  return (
    <UIContextsProvider
      theme={hyperliquidTheme}
      i18n={i18nTokens}
      device="desktop"
      kycCompleted={true}
      riskLevel={20}
      subscriptionTier="Basic"
      referralRank={{ name: "Bronze", rewards: 5 }}
    >
      <AppContent />
    </UIContextsProvider>
  )
}

export default App
