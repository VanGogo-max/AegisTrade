// src/layout/trading_view_layout_map.ts

import { PanelKey } from "../permissions/ui_permissions"

export interface PanelConfig {
  key: PanelKey
  title: string
  defaultWidth: number // в grid units
  defaultHeight: number
  minWidth?: number
  minHeight?: number
  resizable?: boolean
  collapsible?: boolean
  position?: { x: number; y: number }
}

export const tradingViewLayoutMap: Record<PanelKey, PanelConfig> = {
  orderbook: {
    key: "orderbook",
    title: "Order Book",
    defaultWidth: 3,
    defaultHeight: 6,
    resizable: true,
    collapsible: true,
    position: { x: 0, y: 0 }
  },
  chart: {
    key: "chart",
    title: "Chart",
    defaultWidth: 6,
    defaultHeight: 6,
    resizable: true,
    collapsible: false,
    position: { x: 3, y: 0 }
  },
  trades: {
    key: "trades",
    title: "Recent Trades",
    defaultWidth: 3,
    defaultHeight: 3,
    resizable: true,
    collapsible: true,
    position: { x: 0, y: 6 }
  },
  positions: {
    key: "positions",
    title: "Open Positions",
    defaultWidth: 3,
    defaultHeight: 3,
    resizable: true,
    collapsible: true,
    position: { x: 3, y: 6 }
  },
  orders: {
    key: "orders",
    title: "Orders",
    defaultWidth: 3,
    defaultHeight: 3,
    resizable: true,
    collapsible: true,
    position: { x: 6, y: 6 }
  },
  balances: {
    key: "balances",
    title: "Balances",
    defaultWidth: 3,
    defaultHeight: 3,
    resizable: true,
    collapsible: true,
    position: { x: 9, y: 6 }
  },
  subscription: {
    key: "subscription",
    title: "Subscription",
    defaultWidth: 3,
    defaultHeight: 2,
    resizable: true,
    collapsible: true,
    position: { x: 0, y: 9 }
  },
  referral_dashboard: {
    key: "referral_dashboard",
    title: "Referral Dashboard",
    defaultWidth: 3,
    defaultHeight: 3,
    resizable: true,
    collapsible: true,
    position: { x: 3, y: 9 }
  }
}
