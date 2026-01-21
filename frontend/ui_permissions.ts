// src/permissions/ui_permissions.ts

import { subscriptionTokens } from "../subscription/subscription_tokens"
import { referralTokens } from "../referral/referral_tokens"

export type FeatureKey =
  | "spot_trading"
  | "futures_trading"
  | "grid_trading"
  | "arbitrage"
  | "copy_trading"
  | "priority_execution"
  | "advanced_charts"
  | "alerts"
  | "referral_program"
  | "dedicated_nodes"
  | "custom_integrations"

export type PanelKey =
  | "orderbook"
  | "chart"
  | "trades"
  | "positions"
  | "orders"
  | "balances"
  | "subscription"
  | "referral_dashboard"

export interface UIPermissionToken {
  feature: FeatureKey | PanelKey
  requiredSubscription?: keyof typeof subscriptionTokens
  minReferralRank?: string
  kycRequired?: boolean
  maxRiskLevel?: number
}

export const uiPermissions: UIPermissionToken[] = [
  { feature: "spot_trading" }, // free tier has access
  { feature: "futures_trading", requiredSubscription: "pro" },
  { feature: "grid_trading", requiredSubscription: "pro_plus" },
  { feature: "arbitrage", requiredSubscription: "pro_plus" },
  { feature: "copy_trading", requiredSubscription: "pro_plus" },
  { feature: "priority_execution", requiredSubscription: "pro_plus", minReferralRank: "gold" },
  { feature: "advanced_charts", requiredSubscription: "pro" },
  { feature: "alerts", requiredSubscription: "pro" },
  { feature: "referral_program", requiredSubscription: "pro" },
  { feature: "dedicated_nodes", requiredSubscription: "enterprise", kycRequired: true },
  { feature: "custom_integrations", requiredSubscription: "enterprise", kycRequired: true },

  // Panels
  { feature: "orderbook" },
  { feature: "chart" },
  { feature: "trades" },
  { feature: "positions" },
  { feature: "orders" },
  { feature: "balances" },
  { feature: "subscription" },
  { feature: "referral_dashboard", minReferralRank: "starter" }
]

export const checkUIPermission = (
  feature: FeatureKey | PanelKey,
  subscriptionTier: keyof typeof subscriptionTokens,
  referralRankId?: string,
  kycCompleted: boolean = false,
  riskLevel: number = 0
): boolean => {
  const token = uiPermissions.find(t => t.feature === feature)
  if (!token) return true // default allow

  if (token.requiredSubscription) {
    const tiers = Object.keys(subscriptionTokens)
    const requiredIndex = tiers.indexOf(token.requiredSubscription)
    const userIndex = tiers.indexOf(subscriptionTier)
    if (userIndex < requiredIndex) return false
  }

  if (token.minReferralRank && referralRankId) {
    const rankOrder = referralTokens.ranks.map(r => r.id)
    const requiredIndex = rankOrder.indexOf(token.minReferralRank)
    const userIndex = rankOrder.indexOf(referralRankId)
    if (userIndex < requiredIndex) return false
  }

  if (token.kycRequired && !kycCompleted) return false
  if (token.maxRiskLevel !== undefined && riskLevel > token.maxRiskLevel) return false

  return true
}
