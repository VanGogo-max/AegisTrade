"""
feature_flags.py

Enterprise-grade Feature Flag system.

ЦЕЛ:
- Контролирано включване/изключване на функционалности
- Без redeploy
- Без промени в бизнес логиката
- Поддържа subscription, admin override и глобални kill-switch

ЗАВИСИМОСТИ:
- subscription_plan.py
- admin_permissions.py

НЕ:
- съдържа бизнес логика
- изпълнява стратегии
"""

from enum import Enum
from typing import Optional

from subscription_plan import SubscriptionPlan, get_user_plan
from admin_permissions import is_admin


# ============================================================
# 1️⃣ ДЕФИНИЦИЯ НА FEATURE-И (ЕДИНСТВЕН ИЗТОЧНИК НА ИСТИНА)
# ============================================================

class Feature(Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    GRID_BOT = "grid_bot"
    ADVANCED_STRATEGIES = "advanced_strategies"
    API_ACCESS = "api_access"
    REFERRAL_SYSTEM = "referral_system"
    ADMIN_DASHBOARD = "admin_dashboard"


# ============================================================
# 2️⃣ ГЛОБАЛНИ FEATURE FLAGS (KILL SWITCH)
# ============================================================
# ⚠️ При инцидент тук се изключва функционалност
# ⚠️ НЕ се използва за subscription логика

GLOBAL_FEATURE_FLAGS = {
    Feature.SPOT_TRADING: True,
    Feature.FUTURES_TRADING: True,
    Feature.GRID_BOT: True,
    Feature.ADVANCED_STRATEGIES: True,
    Feature.API_ACCESS: True,
    Feature.REFERRAL_SYSTEM: True,
    Feature.ADMIN_DASHBOARD: True,
}


# ============================================================
# 3️⃣ ДОСТЪП ПО SUBSCRIPTION PLAN
# ============================================================

PLAN_FEATURE_MATRIX = {
    SubscriptionPlan.FREE: {
        Feature.SPOT_TRADING,
    },
    SubscriptionPlan.BASIC: {
        Feature.SPOT_TRADING,
        Feature.GRID_BOT,
    },
    SubscriptionPlan.PRO: {
        Feature.SPOT_TRADING,
        Feature.GRID_BOT,
        Feature.FUTURES_TRADING,
        Feature.API_ACCESS,
    },
    SubscriptionPlan.ENTERPRISE: {
        Feature.SPOT_TRADING,
        Feature.GRID_BOT,
        Feature.FUTURES_TRADING,
        Feature.API_ACCESS,
        Feature.ADVANCED_STRATEGIES,
        Feature.REFERRAL_SYSTEM,
    },
}


# ============================================================
# 4️⃣ ТРИСТЕПЕННА ПРОВЕРКА (CORE LOGIC)
# ============================================================

def is_feature_enabled(
    user_id: str,
    feature: Feature,
    *,
    admin_override: Optional[bool] = None
) -> bool:
    """
    ТРИСТЕПЕННА ПРОВЕРКА:

    1️⃣ Global flag (kill switch)
    2️⃣ Admin override
    3️⃣ Subscription plan

    ВРЪЩА:
    - True  -> feature е разрешен
    - False -> feature е забранен
    """

    # ---------- STEP 1: GLOBAL KILL SWITCH ----------
    global_enabled = GLOBAL_FEATURE_FLAGS.get(feature, False)
    if not global_enabled:
        return False

    # ---------- STEP 2: ADMIN OVERRIDE ----------
    if is_admin(user_id):
        if admin_override is not None:
            return admin_override
        return True

    # ---------- STEP 3: SUBSCRIPTION PLAN ----------
    user_plan = get_user_plan(user_id)
    allowed_features = PLAN_FEATURE_MATRIX.get(user_plan, set())

    return feature in allowed_features


# ============================================================
# 5️⃣ SAFE CHECK (ЗА ВЪНШНИ МОДУЛИ)
# ============================================================

def require_feature(user_id: str, feature: Feature) -> None:
    """
    Guard helper.
    Използва се от:
    - routers
    - services
    - strategy loaders

    Вдига PermissionError при забрана.
    """
    if not is_feature_enabled(user_id, feature):
        raise PermissionError(
            f"Feature '{feature.value}' is not enabled for user '{user_id}'"
        )
