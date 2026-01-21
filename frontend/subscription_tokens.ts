// src/subscription/subscription_tokens.ts

export type BillingInterval = "monthly" | "yearly"

export type SubscriptionTier =
  | "free"
  | "pro"
  | "pro_plus"
  | "enterprise"

export interface FeatureFlag {
  key: string
  label: string
  description: string
}

export interface SubscriptionLimits {
  maxBots: number
  maxPairs: number
  maxStrategies: number
  apiRateLimit: number // req/min
  maxOpenPositions: number
  maxWebhooks: number
}

export interface SubscriptionPricing {
  priceUSD: number
  priceUSDT: number
  interval: BillingInterval
  trialDays?: number
}

export interface SubscriptionBadge {
  label: string
  color: string
  glow?: boolean
}

export interface SubscriptionTierToken {
  id: SubscriptionTier
  name: string
  description: string
  pricing: SubscriptionPricing
  limits: SubscriptionLimits
  features: FeatureFlag[]
  badge: SubscriptionBadge
  prioritySupport: boolean
  referralMultiplier: number
}

export const subscriptionTokens: Record<SubscriptionTier, SubscriptionTierToken> =
  {
    free: {
      id: "free",
      name: "Free",
      description: "Basic trading access with limited features",
      pricing: {
        priceUSD: 0,
        priceUSDT: 0,
        interval: "monthly"
      },
      limits: {
        maxBots: 1,
        maxPairs: 3,
        maxStrategies: 1,
        apiRateLimit: 60,
        maxOpenPositions: 2,
        maxWebhooks: 0
      },
      features: [
        { key: "spot_trading", label: "Spot Trading", description: "Basic spot trading" },
        { key: "paper_trading", label: "Paper Trading", description: "Simulation mode" }
      ],
      badge: {
        label: "FREE",
        color: "#6B7280"
      },
      prioritySupport: false,
      referralMultiplier: 1
    },

    pro: {
      id: "pro",
      name: "Pro",
      description: "Advanced trading tools and automation",
      pricing: {
        priceUSD: 5,
        priceUSDT: 5,
        interval: "monthly",
        trialDays: 7
      },
      limits: {
        maxBots: 5,
        maxPairs: 20,
        maxStrategies: 10,
        apiRateLimit: 300,
        maxOpenPositions: 20,
        maxWebhooks: 10
      },
      features: [
        { key: "futures_trading", label: "Futures Trading", description: "Perpetuals & leverage" },
        { key: "advanced_charts", label: "Advanced Charts", description: "Indicators, drawing tools" },
        { key: "alerts", label: "Price Alerts", description: "Custom notifications" },
        { key: "referral_program", label: "Referral Program", description: "Earn from invites" }
      ],
      badge: {
        label: "PRO",
        color: "#3B82F6",
        glow: true
      },
      prioritySupport: true,
      referralMultiplier: 1.5
    },

    pro_plus: {
      id: "pro_plus",
      name: "Pro+",
      description: "High-frequency trading & automation suite",
      pricing: {
        priceUSD: 15,
        priceUSDT: 15,
        interval: "monthly",
        trialDays: 7
      },
      limits: {
        maxBots: 20,
        maxPairs: 100,
        maxStrategies: 50,
        apiRateLimit: 1200,
        maxOpenPositions: 100,
        maxWebhooks: 50
      },
      features: [
        { key: "grid_trading", label: "Grid Bots", description: "Automated grid strategies" },
        { key: "arbitrage", label: "Arbitrage Engine", description: "Cross-DEX & CEX arbitrage" },
        { key: "copy_trading", label: "Copy Trading", description: "Mirror top traders" },
        { key: "priority_execution", label: "Priority Execution", description: "Low latency order routing" }
      ],
      badge: {
        label: "PRO+",
        color: "#A855F7",
        glow: true
      },
      prioritySupport: true,
      referralMultiplier: 2
    },

    enterprise: {
      id: "enterprise",
      name: "Enterprise",
      description: "Institutional-grade infrastructure & support",
      pricing: {
        priceUSD: 0,
        priceUSDT: 0,
        interval: "monthly"
      },
      limits: {
        maxBots: 999,
        maxPairs: 999,
        maxStrategies: 999,
        apiRateLimit: 10000,
        maxOpenPositions: 1000,
        maxWebhooks: 999
      },
      features: [
        { key: "dedicated_nodes", label: "Dedicated Nodes", description: "Private RPC & execution nodes" },
        { key: "custom_integrations", label: "Custom Integrations", description: "API, FIX, OMS, risk systems" },
        { key: "sla", label: "SLA", description: "99.99% uptime guarantee" }
      ],
      badge: {
        label: "ENTERPRISE",
        color: "#F97316",
        glow: true
      },
      prioritySupport: true,
      referralMultiplier: 3
    }
  }
