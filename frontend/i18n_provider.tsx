// src/i18n/i18n_provider.tsx

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react"
import {
  i18nTokens,
  SupportedLocale,
  I18nLocaleToken
} from "./i18n_tokens"

type I18nContextValue = {
  locale: SupportedLocale
  token: I18nLocaleToken
  setLocale: (locale: SupportedLocale) => void
  t: (key: string) => string
  formatNumber: (value: number) => string
  formatPercent: (value: number) => string
  formatCurrency: (value: number, currency?: string) => string
  formatDate: (date: Date) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

const STORAGE_KEY = "dex_ui_locale"

// Placeholder translation storage (по-късно ще е JSON lazy-load)
const translations: Record<string, Record<string, string>> = {
  en: {
    "app.title": "DEX Trading Platform",
    "menu.trade": "Trade",
    "menu.portfolio": "Portfolio",
    "menu.subscription": "Subscription",
    "menu.referral": "Referral"
  },
  bg: {
    "app.title": "DEX Платформа за търговия",
    "menu.trade": "Търговия",
    "menu.portfolio": "Портфейл",
    "menu.subscription": "Абонамент",
    "menu.referral": "Реферали"
  }
  // останалите езици ще се добавят като отделни namespace файлове
}

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [locale, setLocaleState] = useState<SupportedLocale>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return (stored as SupportedLocale) || "en"
  })

  const token = i18nTokens[locale]

  useEffect(() => {
    document.documentElement.lang = token.code
    document.documentElement.dir = token.direction
    document.documentElement.style.setProperty(
      "--font-locale-base",
      token.typography.fontFamily
    )
    document.documentElement.style.setProperty(
      "--font-locale-mono",
      token.typography.monoFont
    )
    localStorage.setItem(STORAGE_KEY, locale)
  }, [locale, token])

  const t = (key: string) => {
    return (
      translations[locale]?.[key] ||
      translations["en"]?.[key] ||
      key
    )
  }

  const formatNumber = (value: number) =>
    new Intl.NumberFormat(locale).format(value)

  const formatPercent = (value: number) =>
    new Intl.NumberFormat(locale, token.format.percentFormat).format(value)

  const formatCurrency = (value: number, currency?: string) =>
    new Intl.NumberFormat(locale, {
      ...token.format.currencyFormat,
      currency: currency || token.format.currencyFormat.currency
    }).format(value)

  const formatDate = (date: Date) =>
    new Intl.DateTimeFormat(locale).format(date)

  const setLocale = (newLocale: SupportedLocale) => {
    if (i18nTokens[newLocale]) {
      setLocaleState(newLocale)
    }
  }

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      token,
      setLocale,
      t,
      formatNumber,
      formatPercent,
      formatCurrency,
      formatDate
    }),
    [locale, token]
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export const useI18n = (): I18nContextValue => {
  const ctx = useContext(I18nContext)
  if (!ctx) {
    throw new Error("useI18n must be used within I18nProvider")
  }
  return ctx
}
