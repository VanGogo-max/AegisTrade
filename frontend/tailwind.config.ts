import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./stores/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0B0E11",
          secondary: "#12161C",
          panel: "#161A21",
          border: "#1F2630"
        },
        text: {
          primary: "#E5E7EB",
          secondary: "#9CA3AF",
          muted: "#6B7280"
        },
        accent: {
          blue: "#3B82F6",
          green: "#22C55E",
          red: "#EF4444",
          yellow: "#FACC15",
          purple: "#A855F7",
          cyan: "#22D3EE"
        },
        neon: {
          pnlPositive: "#00FFA3",
          pnlNegative: "#FF4D4D",
          liquidation: "#FF1E1E"
        }
      },
      boxShadow: {
        panel: "0 0 0 1px rgba(255,255,255,0.04), 0 8px 24px rgba(0,0,0,0.6)",
        glow: "0 0 20px rgba(0,255,163,0.25)"
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px"
      },
      fontFamily: {
        mono: ["JetBrains Mono", "monospace"],
        ui: ["Inter", "sans-serif"]
      },
      animation: {
        pulseSlow: "pulse 3s ease-in-out infinite",
        glow: "glow 2s ease-in-out infinite alternate"
      },
      keyframes: {
        glow: {
          from: { boxShadow: "0 0 10px rgba(0,255,163,0.2)" },
          to: { boxShadow: "0 0 20px rgba(0,255,163,0.5)" }
        }
      }
    }
  },
  plugins: []
};

export default config;
