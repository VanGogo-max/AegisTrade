# core/risk/replay_engine.py

class ReplayEngine:
    def __init__(self):
        self.event_log = []  # list of dicts: {"order":..., "pre":..., "post":...}

    def log_event(self, order, pre_hash, post_hash):
        """Записва delta event"""
        self.event_log.append({"order": order, "pre": pre_hash, "post": post_hash})

    def replay(self, shadow_ledger, start_index=0):
        """
        Възстановява state чрез replay на event_log от start_index
        shadow_ledger: инстанция на ShadowLedger
        """
        for e in self.event_log[start_index:]:
            shadow_ledger.simulate_order(e["order"])
            # commit може да се направи, ако е safe
            # за по-сложни версии -> проверка на pre/post hash
