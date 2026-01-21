// src/referral/referral_tokens.ts

export type ReferralLevel = 1 | 2 | 3 | 4 | 5

export interface ReferralCommission {
  level: ReferralLevel
  percent: number          // % от trading fees
  maxDepthReward: boolean // дали получава от под-нива
}

export interface ReferralRank {
  id: string
  name: string
  minReferrals: number
  minVolumeUSDT: number
  commissionBoost: number // множител
  badgeColor: string
  glow?: boolean
}

export interface ReferralLimits {
  maxInvitesPerDay: number
  maxAccountsPerIP: number
  minTradingVolumeForReward: number
  cooldownHours: number
}

export interface ReferralUI {
  treeMaxDepth: number
  highlightColor: string
  activeNodeColor: string
  inactiveNodeColor: string
}

export interface ReferralToken {
  commissions: ReferralCommission[]
  ranks: ReferralRank[]
  limits: ReferralLimits
  ui: ReferralUI
}

export const referralTokens: ReferralToken = {
  commissions: [
    { level: 1, percent: 20, maxDepthReward: true },
    { level: 2, percent: 10, maxDepthReward: true },
    { level: 3, percent: 5,  maxDepthReward: true },
    { level: 4, percent: 3,  maxDepthReward: false },
    { level: 5, percent: 2,  maxDepthReward: false }
  ],

  ranks: [
    {
      id: "starter",
      name: "Starter",
      minReferrals: 1,
      minVolumeUSDT: 1_000,
      commissionBoost: 1,
      badgeColor: "#6B7280"
    },
    {
      id: "bronze",
      name: "Bronze Partner",
      minReferrals: 10,
      minVolumeUSDT: 25_000,
      commissionBoost: 1.1,
      badgeColor: "#CD7F32",
      glow: true
    },
    {
      id: "silver",
      name: "Silver Partner",
      minReferrals: 50,
      minVolumeUSDT: 100_000,
      commissionBoost: 1.25,
      badgeColor: "#C0C0C0",
      glow: true
    },
    {
      id: "gold",
      name: "Gold Partner",
      minReferrals: 200,
      minVolumeUSDT: 500_000,
      commissionBoost: 1.5,
      badgeColor: "#FFD700",
      glow: true
    },
    {
      id: "platinum",
      name: "Platinum Partner",
      minReferrals: 1000,
      minVolumeUSDT: 2_000_000,
      commissionBoost: 2,
      badgeColor: "#A855F7",
      glow: true
    }
  ],

  limits: {
    maxInvitesPerDay: 100,
    maxAccountsPerIP: 3,
    minTradingVolumeForReward: 50, // USDT
    cooldownHours: 24
  },

  ui: {
    treeMaxDepth: 5,
    highlightColor: "#3B82F6",
    activeNodeColor: "#22C55E",
    inactiveNodeColor: "#6B7280"
  }
}
