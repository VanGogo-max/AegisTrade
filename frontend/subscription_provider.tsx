// src/subscription/subscription_provider.tsx

import React, { createContext, useContext, useEffect, useMemo, useState } from "react"
import {
  subscriptionTokens,
  SubscriptionTier,
  SubscriptionTierToken
} from "./subscription_tokens"

export interface SubscriptionState {
  tier: SubscriptionTier
  token: SubscriptionTierToken
  expiresAt: number | null
  trialEndsAt: number | null
  isActive: boolean
  isTrial: boolean
  referralMultiplier: number
}

type SubscriptionContextValue = {
  state: SubscriptionState
  upgrade: (tier: SubscriptionTier, expiresAt: number) => void
  startTrial: (tier: SubscriptionTier, days: number) => void
  cancel: () => void
  hasFeature: (featureKey: string) => boolean
  hasLimit: (limit: keyof SubscriptionTierToken["limits"], value: number) => boolean
}

const STORAGE_KEY = "dex_subscription_state"

const SubscriptionContext = createContext<SubscriptionContextValue | null>(null)

export const SubscriptionProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [state, setState] = useState<SubscriptionState>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) return JSON.parse(stored)

    const free = subscriptionTokens.free
    return {
      tier: "free",
      token: free,
      expiresAt: null,
      trialEndsAt: null,
      isActive: true,
      isTrial: false,
      referralMultiplier: free.referralMultiplier
    }
  })

  useEffect(() => {
    const now = Date.now()
    let isActive = true
    let isTrial = false

    if (state.trialEndsAt && now < state.trialEndsAt) {
      isTrial = true
      isActive = true
    } else if (state.expiresAt && now > state.expiresAt) {
      isActive = false
    }

    const updated: SubscriptionState = {
      ...state,
      isActive,
      isTrial
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    setState(updated)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const upgrade = (tier: SubscriptionTier, expiresAt: number) => {
    const token = subscriptionTokens[tier]
    const newState: SubscriptionState = {
      tier,
      token,
      expiresAt,
      trialEndsAt: null,
      isActive: true,
      isTrial: false,
      referralMultiplier: token.referralMultiplier
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState))
    setState(newState)
  }

  const startTrial = (tier: SubscriptionTier, days: number) => {
    const token = subscriptionTokens[tier]
    const trialEndsAt = Date.now() + days * 24 * 60 * 60 * 1000

    const newState: SubscriptionState = {
      tier,
      token,
      expiresAt: null,
      trialEndsAt,
      isActive: true,
      isTrial: true,
      referralMultiplier: token.referralMultiplier
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState))
    setState(newState)
  }

  const cancel = () => {
    const free = subscriptionTokens.free
    const newState: SubscriptionState = {
      tier: "free",
      token: free,
      expiresAt: null,
      trialEndsAt: null,
      isActive: true,
      isTrial: false,
      referralMultiplier: free.referralMultiplier
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState))
    setState(newState)
  }

  const hasFeature = (featureKey: string): boolean => {
    return state.token.features.some(f => f.key === featureKey)
  }

  const hasLimit = (
    limit: keyof SubscriptionTierToken["limits"],
    value: number
  ): boolean => {
    return value <= state.token.limits[limit]
  }

  const value = useMemo<SubscriptionContextValue>(
    () => ({
      state,
      upgrade,
      startTrial,
      cancel,
      hasFeature,
      hasLimit
    }),
    [state]
  )

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  )
}

export const useSubscription = (): SubscriptionContextValue => {
  const ctx = useContext(SubscriptionContext)
  if (!ctx) {
    throw new Error("useSubscription must be used within SubscriptionProvider")
  }
  return ctx
}
