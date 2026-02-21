from typing import Dict


class ExposureController:

    def __init__(
        self,
        max_position_size_pct: float = 0.1,
        max_total_exposure_pct: float = 0.5,
        max_positions: int = 10,
    ):
        """
        max_position_size_pct = максимален размер на една позиция (10% от капитала)
        max_total_exposure_pct = максимална обща експозиция
        """

        self.max_position_size_pct = max_position_size_pct
        self.max_total_exposure_pct = max_total_exposure_pct
        self.max_positions = max_positions

    # -----------------------------------------------------

    def check_new_position(
        self,
        equity: float,
        position_size: float,
        current_exposure: float,
        open_positions: int,
    ) -> bool:

        # твърде много позиции
        if open_positions >= self.max_positions:
            return False

        # позицията е твърде голяма
        if position_size > equity * self.max_position_size_pct:
            return False

        # прекалено голяма обща експозиция
        if current_exposure + position_size > equity * self.max_total_exposure_pct:
            return False

        return True

    # -----------------------------------------------------

    def adjust_position_size(
        self,
        equity: float,
        requested_size: float,
    ) -> float:

        max_allowed = equity * self.max_position_size_pct

        return min(requested_size, max_allowed)

    # -----------------------------------------------------

    def calculate_leverage_limit(
        self,
        volatility: float,
    ) -> float:
        """
        Намалява leverage при висока волатилност
        """

        if volatility > 0.05:
            return 2

        if volatility > 0.03:
            return 3

        return 5
