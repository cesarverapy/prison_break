class ClinicalRules:
    def __init__(self, enforce_handwash=True):
        self.enforce_handwash = enforce_handwash

    def may_administer(self, tm) -> bool:
        handwash = tm._get('lavado_manos')
        pickmed  = tm._get('recoger_meds')
        return bool(handwash and handwash.done and pickmed and pickmed.done)
