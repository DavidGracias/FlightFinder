class Flight():
    
    def __init__(self, origin, destination, time_depart, time_arrive, airline, cost) -> None:
        self.origin=origin
        self.destination=destination
        self.time_depart=time_depart
        self.time_arrive=time_arrive
        self.airline=airline
        self.cost=cost

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return f"({self.origin})[{self.time_depart}] -> ({self.destination})[{self.time_arrive}] w/ {self.airline} for ${self.cost}"
    

class TheoreticalFlight(Flight):
    def __init__(self, origin, destination, airline) -> None:
        super().__init__(origin, destination, None, None, airline, None)

    def get_real_flights(self, start, end):
        return [] # TODO: search google flights / some other web scraper to get these flights
    
    def __str__(self) -> str:
        return f"({self.origin}) -> ({self.destination}) w/ {self.airline}"