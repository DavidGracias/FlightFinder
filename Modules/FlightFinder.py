from datetime import datetime, timedelta
from Modules.FlightConstants import FlightConstants

class FlightFinder():
    # AIRLINE: Get airline(s) to fly from
    def get_airline_codes(airlines, airline_choices):
        if airlines: return airlines
        elif airline_choices: return FlightConstants.airlines[airline_choices]
        return FlightConstants.airlines[FlightConstants.ALL_AIRLINES]

    # AIRPORTS: Get all airports that match the first given parameter
    def get_airports(airports, coordinates, address, region, distance, default):
        if airports:
            desired_airports = [FlightConstants.get_airport_from_code(airport) for airport in airports]
        elif coordinates:
            latitude, longitude = coordinates
            desired_airports = FlightFinder.get_all_airports_within_circle(latitude, longitude, distance)
        elif address:
            from geopy.geocoders import Nominatim
            geo = Nominatim(user_agent="my_request").geocode(address)
            latitude, longitude = geo.latitude, geo.longitude

            desired_airports = FlightFinder.get_all_airports_within_circle(latitude, longitude, distance)
        elif region:
            desired_airports = FlightConstants.regions[region]
        else:
            desired_airports = default

        return desired_airports
    
    def get_airports_nearme(distance, debug=False):
        import geocoder
        latlng = geocoder.ip('me').latlng
        if latlng == None:
            if debug:
                print("You are not connected to the internet; defaulting the the coordinates for PHX airport")
                latlng = (33.433333, -112.033333)
            else:
                exit("You are not connected to the internet; please reconnect and try again")
        latitude, longitude = latlng
        
        return FlightFinder.get_all_airports_within_circle(latitude, longitude, distance)

    def get_airports_anywhere(distance):
        return FlightFinder.get_all_airports_within_circle(0, 0, float('inf'))


    # DATES: Get start and end date for desired flights
    def get_start_end_date(startdate, length):
        start = datetime.strptime(startdate, '%m-%d-%Y')
        return start, start + timedelta(days=length)


    def get_all_airports_within_circle(latitude, longitude, radius):
        if radius == float('inf'): return FlightConstants.get_all_airports()
        
        origin = (latitude, longitude)
        from geopy.distance import geodesic

        dist_airports = [(geodesic(origin, a.coordinates).miles, a) for a in FlightConstants.get_all_airports()]
        airports_in_range = filter(lambda a: a[0] <= radius, dist_airports)
        airports_in_range_sorted = sorted(airports_in_range, key=lambda a: a[0])
        return [a for dist, a in airports_in_range_sorted]


    def get_all_airports_with_airlines(airlines):
        all_airports = FlightConstants.get_all_airports()
        airline_airports = set()
        for airline in airlines:
            for a1, a2 in FlightConstants.city_to_city_by_airline[airline]:
                airline_airports.add(a1)
                airline_airports.add(a2)

        return [airport for airport in all_airports if airport.airport_code in airline_airports]
            
    
    def flight_exists(airline, origin, destination):
        origin_to_destination = FlightConstants.city_to_city_by_airline[airline]
        for o1, d1 in origin_to_destination:
            if o1 == origin and d1 == destination: return True
        return False