class Airport():
    def __init__(self, airport_code: str, latitude: float, longitude: float, country_code: str) -> None:
        self.airport_code = airport_code
        self.latitude = latitude
        self.longitude = longitude
        self.coordinates = (latitude, longitude)
        self.country_code = country_code

    def __eq__(self, other) -> bool:
        if type(other) == type(""): return self.airport_code == other
        if type(other) == type(self): return self.airport_code == other.airport_code
        return False

    def __lt__(self, other) -> bool:
        if type(other) == type(""): return self.airport_code < other
        if type(other) == type(self): return self.airport_code < other.airport_code
        return False

    def getCodeAndCoord(self):
        return self.airport_code, self.coordinates
    
    def __repr__(self) -> str: return str(self)
    def __str__(self) -> str: return self.airport_code