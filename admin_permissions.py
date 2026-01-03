from enum import Enum
from typing import Set, Dict


class AdminRole(Enum):
    SUPER_ADMIN = "super_admin"
    SUPPORT = "support"
    READ_ONLY = "read_only"


class AdminAction(Enum):
    VIEW_METRICS = "view_metrics"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    START_BOT = "start_bot"
    STOP_BOT = "stop_bot"
    OVERRIDE_LIMITS = "override_limits"
    MANAGE_USERS = "manage_users"


class AdminPermissions:
    """
    Central definition of admin roles and allowed actions.
    """

    def __init__(self) -> None:
        self._permissions: Dict[AdminRole, Set[AdminAction]] = {
            AdminRole.SUPER_ADMIN: set(AdminAction),
            AdminRole.SUPPORT: {
                AdminAction.VIEW_METRICS,
                AdminAction.VIEW_AUDIT_LOGS,
            },
            AdminRole.READ_ONLY: {
                AdminAction.VIEW_METRICS,
            },
        }

    def is_allowed(self, role: AdminRole, action: AdminAction) -> bool:
        if role == AdminRole.SUPER_ADMIN:
            return True
        return action in self._permissions.get(role, set())

    def allowed_actions(self, role: AdminRole) -> Set[AdminAction]:
        if role == AdminRole.SUPER_ADMIN:
            return set(AdminAction)
        return set(self._permissions.get(role, set()))
