// src/theme/theme_provider.tsx

import React, { createContext, useContext, useEffect, useMemo, useState } from "react"
import { ThemeTokens, darkTradingTheme } from "./theme_tokens"

type ThemeContextValue = {
  theme: ThemeTokens
  setTheme: (theme: ThemeTokens) => void
  mode: "dark" | "light"
  toggleMode: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

const THEME_STORAGE_KEY = "dex_ui_theme"

function applyThemeToCSSVariables(theme: ThemeTokens) {
  const root = document.documentElement

  const setVar = (key: string, value: string | number) => {
    root.style.setProperty(`--${key}`, String(value))
  }

  // Recursive flattening of tokens to CSS vars
  const walk = (obj: any, path: string[] = []) => {
    Object.entries(obj).forEach(([key, value]) => {
      const nextPath = [...path, key]
      if (typeof value === "object" && value !== null) {
        walk(value, nextPath)
      } else {
        setVar(nextPath.join("-"), value)
      }
    })
  }

  walk(theme.colors, ["color"])
  walk(theme.typography, ["font"])
  walk(theme.spacing, ["space"])
  walk(theme.radius, ["radius"])
  walk(theme.shadow, ["shadow"])
  walk(theme.zIndex, ["z"])
  walk(theme.motion, ["motion"])
}

export const ThemeProvider: React.FC<{
  initialTheme?: ThemeTokens
  children: React.ReactNode
}> = ({ initialTheme = darkTradingTheme, children }) => {
  const [theme, setThemeState] = useState<ThemeTokens>(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored) {
      try {
        return JSON.parse(stored)
      } catch {
        return initialTheme
      }
    }
    return initialTheme
  })

  const mode: "dark" | "light" =
    theme.name.includes("dark") ? "dark" : "light"

  useEffect(() => {
    applyThemeToCSSVariables(theme)
    localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(theme))
    document.documentElement.setAttribute("data-theme", theme.name)
  }, [theme])

  const setTheme = (newTheme: ThemeTokens) => {
    setThemeState(newTheme)
  }

  const toggleMode = () => {
    // Placeholder: when lightTheme exists, switch here
    console.warn("Light theme not yet registered")
  }

  const value = useMemo(
    () => ({
      theme,
      setTheme,
      mode,
      toggleMode
    }),
    [theme, mode]
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export const useTheme = (): ThemeContextValue => {
  const ctx = useContext(ThemeContext)
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider")
  }
  return ctx
}
