// src/referral/referral_provider.tsx

import React, { createContext, useContext, useEffect, useMemo, useState } from "react"
import { referralTokens, ReferralLevel, ReferralRank } from "./referral_tokens"

export interface ReferralUserNode {
  userId: string
  parentId?: string
  level: ReferralLevel
  totalVolumeUSDT: number
  totalCommissionUSDT: number
  referrals: ReferralUserNode[]
}

export interface ReferralStats {
  totalReferrals: number
  totalVolumeUSDT: number
  totalEarningsUSDT: number
  rank: ReferralRank
}

export interface ReferralContextValue {
  tree: ReferralUserNode | null
  stats: ReferralStats | null
  calculateCommission: (tradeFeeUSDT: number, level: ReferralLevel) => number
  getRank: (totalReferrals: number, totalVolumeUSDT: number) => ReferralRank
  registerReferral: (parentId: string, userId: string) => void
}

const STORAGE_KEY = "dex_referral_tree"

const ReferralContext = createContext<ReferralContextValue | null>(null)

function computeRank(referrals: number, volume: number): ReferralRank {
  const sorted = [...referralTokens.ranks].sort(
    (a, b) => b.minVolumeUSDT - a.minVolumeUSDT
  )
  return (
    sorted.find(
      r => referrals >= r.minReferrals && volume >= r.minVolumeUSDT
    ) || sorted[0]
  )
}

function computeCommission(fee: number, level: ReferralLevel): number {
  const rule = referralTokens.commissions.find(c => c.level === level)
  if (!rule) return 0
  return (fee * rule.percent) / 100
}

export const ReferralProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [tree, setTree] = useState<ReferralUserNode | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  })

  const buildStats = (node: ReferralUserNode | null): ReferralStats | null => {
    if (!node) return null

    const walk = (n: ReferralUserNode): { count: number; volume: number; earnings: number } => {
      let count = n.referrals.length
      let volume = n.totalVolumeUSDT
      let earnings = n.totalCommissionUSDT

      for (const r of n.referrals) {
        const sub = walk(r)
        count += sub.count
        volume += sub.volume
        earnings += sub.earnings
      }
      return { count, volume, earnings }
    }

    const { count, volume, earnings } = walk(node)
    const rank = computeRank(count, volume)

    return {
      totalReferrals: count,
      totalVolumeUSDT: volume,
      totalEarningsUSDT: earnings * rank.commissionBoost,
      rank
    }
  }

  const stats = useMemo(() => buildStats(tree), [tree])

  useEffect(() => {
    if (tree) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tree))
    }
  }, [tree])

  const registerReferral = (parentId: string, userId: string) => {
    if (!tree) {
      setTree({
        userId: parentId,
        level: 1,
        totalVolumeUSDT: 0,
        totalCommissionUSDT: 0,
        referrals: [
          {
            userId,
            parentId,
            level: 1,
            totalVolumeUSDT: 0,
            totalCommissionUSDT: 0,
            referrals: []
          }
        ]
      })
      return
    }

    const addNode = (node: ReferralUserNode): boolean => {
      if (node.userId === parentId && node.referrals.length < referralTokens.limits.maxInvitesPerDay) {
        node.referrals.push({
          userId,
          parentId,
          level: Math.min(node.level + 1, referralTokens.ui.treeMaxDepth) as ReferralLevel,
          totalVolumeUSDT: 0,
          totalCommissionUSDT: 0,
          referrals: []
        })
        return true
      }
      return node.referrals.some(addNode)
    }

    const cloned = structuredClone(tree)
    addNode(cloned)
    setTree(cloned)
  }

  const value = useMemo<ReferralContextValue>(
    () => ({
      tree,
      stats,
      calculateCommission: computeCommission,
      getRank: computeRank,
      registerReferral
    }),
    [tree, stats]
  )

  return (
    <ReferralContext.Provider value={value}>
      {children}
    </ReferralContext.Provider>
  )
}

export const useReferral = (): ReferralContextValue => {
  const ctx = useContext(ReferralContext)
  if (!ctx) {
    throw new Error("useReferral must be used within ReferralProvider")
  }
  return ctx
}
