from pages.report.report.base import Base
from datetime import date


class ProfitLoss(Base):
    def __init__(self, anchor_date: date):
        self.anchor_date = anch
