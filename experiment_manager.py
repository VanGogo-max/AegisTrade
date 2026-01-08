"""
experiment_manager.py

Enterprise-grade experiment & rollout manager.

ЦЕЛ:
- A/B тестове
- Gradual rollout
- Feature validation в production
- Без промени в subscription или billing логика

ЗАВИСИМОСТИ:
- feature_flags.py

НЕ:
- не активира feature самостоятелно
- не заобикаля security
"""

import hashlib
from typing import Dict

from feature_flags import Feature, is_feature_enabled


# ============================================================
# 1️⃣ EXPERIMENT CONFIGURATION (SOURCE OF TRUTH)
# ============================================================

# rollout_percentage: 0–100
EXPERIMENTS: Dict[Feature, int] = {
    Feature.ADVANCED_STRATEGIES: 20,   # 20% rollout
    Feature.API_ACCESS: 50,            # 50% rollout
}


# ============================================================
# 2️⃣ DETERMINISTIC USER BUCKETING
# ============================================================

def _user_hash_bucket(user_id: str) -> int:
    """
    Връща стабилен bucket (0–99) за даден user.
    Един и същ user винаги попада в същата група.
    """
    digest = hashlib.sha256(user_id.encode()).hexdigest()
    return int(digest[:2], 16) % 100


# ============================================================
# 3️⃣ EXPERIMENT CHECK
# ============================================================

def is_user_in_experiment(user_id: str, feature: Feature) -> bool:
    """
    Проверява дали user участва в rollout експеримента.
    """

    rollout_percentage = EXPERIMENTS.get(feature)
    if rollout_percentage is None:
        return True  # няма експеримент → 100% достъп

    bucket = _user_hash_bucket(user_id)
    return bucket < rollout_percentage


# ============================================================
# 4️⃣ COMBINED FEATURE + EXPERIMENT GUARD
# ============================================================

def is_feature_available(user_id: str, feature: Feature) -> bool:
    """
    ФИНАЛНА ПРОВЕРКА:

    1️⃣ Feature flag (global/admin/subscription)
    2️⃣ Experiment rollout
    """

    if not is_feature_enabled(user_id, feature):
        return False

    return is_user_in_experiment(user_id, feature)
