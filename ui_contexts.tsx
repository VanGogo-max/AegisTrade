// src/ui/ui_contexts.tsx

import React, { ReactNode, useMemo } from "react"
import { ThemeProvider, ThemeTokens } from "../theme/theme_provider"
import { I18nProvider, I18nTokens } from "../i18n/i18n_provider"
import { SubscriptionProvider, useSubscription } from "../subscription/subscription_provider"
import { ReferralProvider, useReferral } from "../referral/referral_provider"
import { DeviceType, initializeLayout, LayoutState } from "../layout/responsive_layout_engine"
import { SubscriptionTier } from "../subscription/subscription_tokens"
import { ReferralRank } from "../referral/referral_tokens"

export interface UIContextsProps {
  theme: ThemeTokens
  i18n: I18nTokens
  device?: DeviceType
  kycCompleted?: boolean
  riskLevel?: number
  children: ReactNode
}

export interface UIContextState {
  subscriptionTier: SubscriptionTier
  referralRank?: ReferralRank
  layoutState: LayoutState
}

export const UIContext = React.createContext<UIContextState | null>(null)

export const UIContextsProvider: React.FC<UIContextsProps> = ({
  theme,
  i18n,
  device = "desktop",
  kycCompleted = false,
  riskLevel = 0,
  children
}) => {
  return (
    <ThemeProvider theme={theme}>
      <I18nProvider tokens={i18n}>
        <SubscriptionProvider>
          <ReferralProvider>
            <UIContextsInner
              device={device}
              kycCompleted={kycCompleted}
              riskLevel={riskLevel}
            >
              {children}
            </UIContextsInner>
          </ReferralProvider>
        </SubscriptionProvider>
      </I18nProvider>
    </ThemeProvider>
  )
}

const UIContextsInner: React.FC<{
  device: DeviceType
  kycCompleted: boolean
  riskLevel: number
  children: ReactNode
}> = ({ device, kycCompleted, riskLevel, children }) => {
  const { state: sub } = useSubscription()
  const { stats: referral } = useReferral()

  const layoutState = useMemo(
    () =>
      initializeLayout({
        subscriptionTier: sub.tier,
        referralRankId: referral?.rank.id,
        kycCompleted,
        riskLevel,
        device
      }),
    [sub.tier, referral?.rank.id, kycCompleted, riskLevel, device]
  )

  const contextValue: UIContextState = useMemo(
    () => ({
      subscriptionTier: sub.tier,
      referralRank: referral?.rank,
      layoutState
    }),
    [sub.tier, referral?.rank, layoutState]
  )

  return <UIContext.Provider value={contextValue}>{children}</UIContext.Provider>
}

export const useUIContexts = (): UIContextState => {
  const ctx = React.useContext(UIContext)
  if (!ctx) throw new Error("useUIContexts must be used within UIContextsProvider")
  return ctx
}
