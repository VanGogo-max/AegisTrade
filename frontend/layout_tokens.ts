// src/layout/layout_tokens.ts

export interface PanelSize {
  min: number
  max: number
  default: number
  collapsible: boolean
}

export interface LayoutTokens {
  appShell: {
    headerHeight: number
    footerHeight: number
    sidebarWidth: PanelSize
    rightbarWidth: PanelSize
  }

  tradingGrid: {
    columns: number
    rows: number
    gap: number
    areas: {
      orderbook: string
      chart: string
      trades: string
      positions: string
      orders: string
      balances: string
    }
  }

  panels: {
    orderbook: PanelSize
    chart: PanelSize
    trades: PanelSize
    positions: PanelSize
    orders: PanelSize
    balances: PanelSize
  }

  breakpoints: {
    mobile: number
    tablet: number
    desktop: number
    wide: number
    ultra: number
  }

  zLayers: {
    header: number
    sidebar: number
    modal: number
    drawer: number
    contextMenu: number
    tooltip: number
  }

  animations: {
    panelResize: string
    collapse: string
    expand: string
    drawerSlide: string
  }
}

// ------------------------------------------------------------
// Hyperliquid-style Trading Layout
// ------------------------------------------------------------

export const hyperliquidLayout: LayoutTokens = {
  appShell: {
    headerHeight: 56,
    footerHeight: 28,

    sidebarWidth: {
      min: 56,
      max: 280,
      default: 72,
      collapsible: true
    },

    rightbarWidth: {
      min: 260,
      max: 420,
      default: 320,
      collapsible: true
    }
  },

  tradingGrid: {
    columns: 12,
    rows: 12,
    gap: 8,

    areas: {
      orderbook: "col-start-1 col-end-4 row-start-1 row-end-9",
      chart: "col-start-4 col-end-10 row-start-1 row-end-7",
      trades: "col-start-10 col-end-13 row-start-1 row-end-7",
      positions: "col-start-4 col-end-13 row-start-7 row-end-10",
      orders: "col-start-1 col-end-7 row-start-9 row-end-13",
      balances: "col-start-7 col-end-13 row-start-9 row-end-13"
    }
  },

  panels: {
    orderbook: {
      min: 220,
      max: 380,
      default: 280,
      collapsible: true
    },

    chart: {
      min: 420,
      max: 1200,
      default: 720,
      collapsible: false
    },

    trades: {
      min: 180,
      max: 320,
      default: 240,
      collapsible: true
    },

    positions: {
      min: 260,
      max: 600,
      default: 360,
      collapsible: false
    },

    orders: {
      min: 260,
      max: 600,
      default: 360,
      collapsible: true
    },

    balances: {
      min: 240,
      max: 480,
      default: 320,
      collapsible: true
    }
  },

  breakpoints: {
    mobile: 480,
    tablet: 768,
    desktop: 1280,
    wide: 1600,
    ultra: 1920
  },

  zLayers: {
    header: 100,
    sidebar: 200,
    modal: 1000,
    drawer: 900,
    contextMenu: 1500,
    tooltip: 2000
  },

  animations: {
    panelResize: "200ms cubic-bezier(0.4, 0, 0.2, 1)",
    collapse: "160ms ease-in-out",
    expand: "220ms ease-out",
    drawerSlide: "260ms cubic-bezier(0.4, 0, 0.2, 1)"
  }
}
