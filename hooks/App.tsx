import React from "react"
import { UIContextsProvider } from "./ui/ui_contexts"
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

const AppContent: React.FC = () => {
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

  return <ResponsiveDragLayout children={children} />
}

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
