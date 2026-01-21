// src/theme/theme_tokens.ts

export type ColorScale = {
  50: string
  100: string
  200: string
  300: string
  400: string
  500: string
  600: string
  700: string
  800: string
  900: string
}

export interface ThemeTokens {
  name: string

  colors: {
    background: {
      primary: string
      secondary: string
      tertiary: string
      elevated: string
      overlay: string
    }

    text: {
      primary: string
      secondary: string
      muted: string
      inverse: string
      danger: string
      success: string
      warning: string
    }

    border: {
      default: string
      subtle: string
      strong: string
      focus: string
    }

    accent: {
      brand: string
      brandMuted: string
      brandStrong: string
    }

    trading: {
      long: ColorScale
      short: ColorScale
      pnlPositive: string
      pnlNegative: string
      liquidation: string
      funding: string
      markPrice: string
      indexPrice: string
    }

    chart: {
      grid: string
      axis: string
      crosshair: string
      volumeUp: string
      volumeDown: string
    }

    status: {
      online: string
      offline: string
      maintenance: string
      syncing: string
    }
  }

  typography: {
    fontFamily: {
      base: string
      mono: string
      ui: string
    }
    fontSize: {
      xs: string
      sm: string
      md: string
      lg: string
      xl: string
      xxl: string
    }
    lineHeight: {
      tight: number
      normal: number
      relaxed: number
    }
    weight: {
      regular: number
      medium: number
      semibold: number
      bold: number
    }
  }

  spacing: {
    xs: number
    sm: number
    md: number
    lg: number
    xl: number
    xxl: number
  }

  radius: {
    sm: number
    md: number
    lg: number
    xl: number
    pill: number
  }

  shadow: {
    sm: string
    md: string
    lg: string
    xl: string
    glow: string
  }

  zIndex: {
    dropdown: number
    modal: number
    popover: number
    toast: number
    tooltip: number
  }

  motion: {
    fast: string
    normal: string
    slow: string
    easing: string
  }
}

// ------------------------------------------------------------
// Hyperliquid-style Dark Trading Theme
// ------------------------------------------------------------

export const darkTradingTheme: ThemeTokens = {
  name: "dark-trading",

  colors: {
    background: {
      primary: "#0B0E11",
      secondary: "#11151A",
      tertiary: "#161B22",
      elevated: "#1C2128",
      overlay: "rgba(0,0,0,0.6)"
    },

    text: {
      primary: "#E6EDF3",
      secondary: "#9DA7B3",
      muted: "#6E7681",
      inverse: "#0B0E11",
      danger: "#FF5C5C",
      success: "#2ECC71",
      warning: "#F1C40F"
    },

    border: {
      default: "#30363D",
      subtle: "#21262D",
      strong: "#3D444D",
      focus: "#3B82F6"
    },

    accent: {
      brand: "#3B82F6",
      brandMuted: "#1D4ED8",
      brandStrong: "#60A5FA"
    },

    trading: {
      long: {
        50: "#ECFDF5",
        100: "#D1FAE5",
        200: "#A7F3D0",
        300: "#6EE7B7",
        400: "#34D399",
        500: "#10B981",
        600: "#059669",
        700: "#047857",
        800: "#065F46",
        900: "#064E3B"
      },
      short: {
        50: "#FEF2F2",
        100: "#FEE2E2",
        200: "#FECACA",
        300: "#FCA5A5",
        400: "#F87171",
        500: "#EF4444",
        600: "#DC2626",
        700: "#B91C1C",
        800: "#991B1B",
        900: "#7F1D1D"
      },
      pnlPositive: "#16C784",
      pnlNegative: "#EA3943",
      liquidation: "#F97316",
      funding: "#A855F7",
      markPrice: "#3B82F6",
      indexPrice: "#EAB308"
    },

    chart: {
      grid: "#1F2933",
      axis: "#374151",
      crosshair: "#9CA3AF",
      volumeUp: "#16C784",
      volumeDown: "#EA3943"
    },

    status: {
      online: "#22C55E",
      offline: "#6B7280",
      maintenance: "#F97316",
      syncing: "#38BDF8"
    }
  },

  typography: {
    fontFamily: {
      base: "Inter, system-ui, sans-serif",
      mono: "JetBrains Mono, monospace",
      ui: "IBM Plex Sans, system-ui"
    },
    fontSize: {
      xs: "11px",
      sm: "13px",
      md: "14px",
      lg: "16px",
      xl: "18px",
      xxl: "22px"
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.7
    },
    weight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    }
  },

  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32
  },

  radius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    pill: 999
  },

  shadow: {
    sm: "0 1px 2px rgba(0,0,0,0.4)",
    md: "0 4px 8px rgba(0,0,0,0.5)",
    lg: "0 10px 20px rgba(0,0,0,0.6)",
    xl: "0 20px 40px rgba(0,0,0,0.7)",
    glow: "0 0 12px rgba(59,130,246,0.6)"
  },

  zIndex: {
    dropdown: 1000,
    modal: 2000,
    popover: 3000,
    toast: 4000,
    tooltip: 5000
  },

  motion: {
    fast: "120ms",
    normal: "220ms",
    slow: "360ms",
    easing: "cubic-bezier(0.4, 0, 0.2, 1)"
  }
}
