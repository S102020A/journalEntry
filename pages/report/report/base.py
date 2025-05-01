from datetime import date


class ReportBase:
    anchor_date: date

    def __init__(self, anchor_date: date):
        self.anchor_date = anchor_date
