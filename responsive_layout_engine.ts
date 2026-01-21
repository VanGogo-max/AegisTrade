// src/layout/responsive_layout_engine.ts

import { PanelConfig, tradingViewLayoutMap } from "./trading_view_layout_map"
import { PanelKey, checkUIPermission } from "../permissions/ui_permissions"
import { SubscriptionTier } from "../subscription/subscription_tokens"
import { ReferralRank } from "../referral/referral_tokens"

export type DeviceType = "desktop" | "tablet" | "mobile"

export interface LayoutState {
  panelPositions: Record<PanelKey, { x: number; y: number }>
  panelSizes: Record<PanelKey, { width: number; height: number }>
  collapsed: Record<PanelKey, boolean>
}

export interface LayoutEngineProps {
  subscriptionTier: SubscriptionTier
  referralRankId?: string
  kycCompleted?: boolean
  riskLevel?: number
  device?: DeviceType
}

export const initializeLayout = (props: LayoutEngineProps): LayoutState => {
  const { subscriptionTier, referralRankId, kycCompleted = false, riskLevel = 0, device = "desktop" } = props

  const panelPositions: LayoutState["panelPositions"] = {}
  const panelSizes: LayoutState["panelSizes"] = {}
  const collapsed: LayoutState["collapsed"] = {}

  Object.values(tradingViewLayoutMap).forEach((panel: PanelConfig) => {
    // Feature gating
    const visible = checkUIPermission(panel.key, subscriptionTier, referralRankId, kycCompleted, riskLevel)
    collapsed[panel.key] = !visible

    // Device-specific adjustments
    let width = panel.defaultWidth
    let height = panel.defaultHeight
    let x = panel.position?.x || 0
    let y = panel.position?.y || 0

    if (device === "tablet") {
      width = Math.min(width, 4)
      height = Math.min(height, 5)
      x = x % 12
    } else if (device === "mobile") {
      width = 12
      height = height
      x = 0
      y = y
    }

    panelPositions[panel.key] = { x, y }
    panelSizes[panel.key] = { width, height }
  })

  return { panelPositions, panelSizes, collapsed }
}

// Collapse / Expand toggle
export const togglePanelCollapse = (state: LayoutState, panelKey: PanelKey): LayoutState => {
  const newCollapsed = { ...state.collapsed, [panelKey]: !state.collapsed[panelKey] }
  return { ...state, collapsed: newCollapsed }
}

// Drag & Drop update
export const updatePanelPosition = (
  state: LayoutState,
  panelKey: PanelKey,
  newX: number,
  newY: number
): LayoutState => {
  const newPositions = { ...state.panelPositions, [panelKey]: { x: newX, y: newY } }
  return { ...state, panelPositions: newPositions }
}

// Resize update
export const updatePanelSize = (
  state: LayoutState,
  panelKey: PanelKey,
  newWidth: number,
  newHeight: number
): LayoutState => {
  const newSizes = { ...state.panelSizes, [panelKey]: { width: newWidth, height: newHeight } }
  return { ...state, panelSizes: newSizes }
}
