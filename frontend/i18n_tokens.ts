// src/i18n/i18n_tokens.ts

export type TextDirection = "ltr" | "rtl"

export interface LocaleFormat {
  decimalSeparator: string
  thousandSeparator: string
  dateFormat: string
  timeFormat: string
  percentFormat: Intl.NumberFormatOptions
  currencyFormat: Intl.NumberFormatOptions
}

export interface LocaleTypography {
  fontFamily: string
  monoFont: string
}

export interface I18nLocaleToken {
  code: string
  name: string
  nativeName: string
  direction: TextDirection
  typography: LocaleTypography
  format: LocaleFormat
}

export type SupportedLocale =
  | "en"
  | "bg"
  | "ru"
  | "de"
  | "fr"
  | "es"
  | "it"
  | "tr"
  | "ar"
  | "zh"

export const i18nTokens: Record<SupportedLocale, I18nLocaleToken> = {
  en: {
    code: "en",
    name: "English",
    nativeName: "English",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ".",
      thousandSeparator: ",",
      dateFormat: "YYYY-MM-DD",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "USD" }
    }
  },

  bg: {
    code: "bg",
    name: "Bulgarian",
    nativeName: "Български",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: " ",
      dateFormat: "DD.MM.YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "BGN" }
    }
  },

  ru: {
    code: "ru",
    name: "Russian",
    nativeName: "Русский",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: " ",
      dateFormat: "DD.MM.YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "RUB" }
    }
  },

  de: {
    code: "de",
    name: "German",
    nativeName: "Deutsch",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: ".",
      dateFormat: "DD.MM.YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "EUR" }
    }
  },

  fr: {
    code: "fr",
    name: "French",
    nativeName: "Français",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: " ",
      dateFormat: "DD/MM/YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "EUR" }
    }
  },

  es: {
    code: "es",
    name: "Spanish",
    nativeName: "Español",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: ".",
      dateFormat: "DD/MM/YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "EUR" }
    }
  },

  it: {
    code: "it",
    name: "Italian",
    nativeName: "Italiano",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: ".",
      dateFormat: "DD/MM/YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "EUR" }
    }
  },

  tr: {
    code: "tr",
    name: "Turkish",
    nativeName: "Türkçe",
    direction: "ltr",
    typography: {
      fontFamily: "Inter, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ",",
      thousandSeparator: ".",
      dateFormat: "DD.MM.YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "TRY" }
    }
  },

  ar: {
    code: "ar",
    name: "Arabic",
    nativeName: "العربية",
    direction: "rtl",
    typography: {
      fontFamily: "Cairo, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: "٫",
      thousandSeparator: "٬",
      dateFormat: "DD/MM/YYYY",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "USD" }
    }
  },

  zh: {
    code: "zh",
    name: "Chinese",
    nativeName: "中文",
    direction: "ltr",
    typography: {
      fontFamily: "Noto Sans SC, system-ui, sans-serif",
      monoFont: "JetBrains Mono, monospace"
    },
    format: {
      decimalSeparator: ".",
      thousandSeparator: ",",
      dateFormat: "YYYY-MM-DD",
      timeFormat: "HH:mm:ss",
      percentFormat: { style: "percent", minimumFractionDigits: 2 },
      currencyFormat: { style: "currency", currency: "CNY" }
    }
  }
}
