class ReplayEngine:
    def __init__(self):
        self.event_log = []

    def log_event(self, event, pre_hash, post_hash):
        """
        TODO:
        - log на event със snapshot хешове
        - необходим за deterministic recovery
        """
        pass

    def replay(self, shadow_ledger):
        """
        TODO:
        - replay на event_log върху shadow ledger
        - възстановяване на state при срив или рестарт
        """
        pass
