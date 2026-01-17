class RiskRulesEngine:
    def __init__(self):
        self.rules = []  # TODO: plug-in list за различни правила

    def evaluate(self, shadow_account, shadow_positions, order):
        """
        TODO:
        - проверка margin, leverage, liquidation buffer
        - проверка drawdown и exposure
        - return "ALLOW" | "BLOCK" | "WARN" | "EMERGENCY"
        """
        pass

    # Пример за plug-in правило
    def margin_rule(self, shadow_account, order):
        """
        TODO:
        - calculate order_margin
        - compare с available margin
        - return decision
        """
        pass
