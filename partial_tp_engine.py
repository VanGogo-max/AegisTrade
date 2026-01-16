# partial_tp_engine.py

from typing import Dict, List


class PartialTPEngine:
    """
    Управлява частично затваряне на позиция:
    - TP1, TP2, TP3 според волатилност профил
    - Премества SL в безубытък след TP1
    - Активира trailing stop за последната част (TP3)
    """

    def __init__(self, trailing_callback=None):
        """
        trailing_callback(price, size) -> стартира trailing стоп
        """
        self.trailing_callback = trailing_callback

    def build_tp_plan(
        self,
        entry_price: float,
        position_size: float,
        tp_levels: List[float],
        tp_profile: Dict[str, float]
    ) -> List[Dict]:
        """
        Създава план за изпълнение на TP ордери.
        """

        plan = []

        for i, (tp_price, key) in enumerate(zip(tp_levels, ["tp1", "tp2", "tp3"])):
            size_part = position_size * tp_profile[key]

            plan.append({
                "tp_id": key.upper(),
                "price": tp_price,
                "size": round(size_part, 8),
                "move_sl_to_be": key == "tp1",
                "enable_trailing": key == "tp3"
            })

        return plan

    def on_tp_filled(self, tp_event: Dict, position_state: Dict):
        """
        Извиква се при изпълнение на TP.
        """

        if tp_event["move_sl_to_be"]:
            position_state["stop_loss"] = position_state["entry_price"]
            position_state["sl_moved_to_be"] = True

        if tp_event["enable_trailing"] and self.trailing_callback:
            remaining_size = position_state["remaining_size"]
            self.trailing_callback(position_state["current_price"], remaining_size)
