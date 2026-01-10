class Trip:
    def __init__(self, destination, start_date, end_date, budget):
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget


class Expense:
    def __init__(self, trip_id, category, amount):
        self.trip_id = trip_id
        self.category = category
        self.amount = amount
