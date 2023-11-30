import random, time, requests, json, html
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse
from Modules.FlightFinder import FlightFinder
from Modules.FlightConstants import FlightConstants
from Modules.Flight import TheoreticalFlight, Flight, FlightSegment
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description="Check flight availability for ORIGIN -> DESTINATION for a given date and airline")

    # AIRLINE: determine the airline(s) we want to fly with
    airlines = parser.add_argument_group(title="Airline", description="Set the airline(s) we want to fly with")
    airlines.add_argument("--airline", nargs="+", dest="airlines", metavar="AIRLINE", help="Desired Airline ICAO code")
    airlines.add_argument("--airlines", nargs="+", metavar="AIRLINE", help="Desired Airline ICAO code")
    airlines.add_argument("--airline_choice", choices=[code for code in FlightConstants.airlines], metavar="AIRLINE_CHOICE")


    # STOPS: currently only supporting 2 (i.e. Origin & Destination)
    stops = ["origin", "destination"]
    for stop in stops:
        group = parser.add_argument_group(title=stop.capitalize(), description=f"Set the {stop} for a flight")
    
        # search location is a fixed-sized
        group.add_argument(f"--{stop}_airport", nargs="+", dest=f"{stop}_airports", metavar="AIRPORT", help="Desired Airport IATA code")
        group.add_argument(f"--{stop}_airports", nargs="+", metavar="AIRPORT", help="Desired Airport(s) IATA code")
        group.add_argument(f"--{stop}_region", choices=[code for code in FlightConstants.regions], metavar="REGION")

        # search location is "distance"-sized
        group.add_argument(f"--{stop}_coordinates", nargs=2, metavar=("LATITUDE", "LONGITUDE"), help=f"{stop.capitalize()} Latitude and Longitude")
        group.add_argument(f"--{stop}_address", type=str, help="The address that you want to center your search around")
    
        group.add_argument(f"--{stop}_distance", type=int, help="Distance (in miles) to search around your city", default=FlightConstants.DEFAULT_TRAVEL_DISTANCE)


    # DATE: determine the dates we"re trying to book the flight for:
    date = parser.add_argument_group(title="Date", description="Set the date interval we'd like to look for flights for")
    date.add_argument("-s", "--startdate", type=str, required=True, help="Date on format mm-dd-yyyy")
    date.add_argument("-l", "--length", type=int, required=False, default=0, help="Number of days (past startdate) to look for flights")

    # MAX_LAYOVERS: the number of layovers
    parser.add_argument("--max_layovers", type=int, required=False, default=0, help="Number of layovers to get from origin to destination")

    # FILTERS: determine the price or location or other factors that affect your flight decision
    filters = parser.add_argument_group(title="Filter", description="Add filters to narrow down your eventual flights")
    filters.add_argument("--filter_price", type=int, required=False, default=float('inf'), help="Filters out all potential (Origin -> Destination) flights that cost more than this amount")
    filters.add_argument("--filter_duration", type=int, required=False, default=float('inf'), help="Filters out all potential (Origin -> Destination) flights that take more than this many hours")

    # debug mode: bypass all exit codes
    parser.add_argument("--debug", action='store_true')
    

    return parser.parse_args()

def main():
    args = parse_args()

    # get the airline codes of whichever airlines were interested in flying with
    airlines = FlightFinder.get_airline_codes(args.airlines, args.airline_choice)

    # get origin airports were interested in flying from
    airports_origin = FlightFinder.get_airports(
        args.origin_airports, args.origin_coordinates, args.origin_address, args.origin_region, args.origin_distance, FlightFinder.get_airports_nearme(args.origin_distance, args.debug)
    )
    # get destination airports were interested in flying to
    airports_destination = FlightFinder.get_airports(
        args.destination_airports, args.destination_coordinates, args.destination_address, args.destination_region, args.destination_distance, FlightFinder.get_airports_anywhere(args.origin_distance)
    )
    # make chains of length up to max_connections with no repititions
    all_airports = FlightFinder.get_all_airports_with_airlines(airlines)

    routes = []
    def route_finder(flight_path, airline_path, num_connections):
        # base case: origin -> destination route found 
        if flight_path[-1] in airports_destination:
            theoretical_route = []
            for i in range(len(flight_path)-1):
                theoretical_route.append(
                    TheoreticalFlight(flight_path[i], flight_path[i+1], airline_path[i])
                )
            routes.append(theoretical_route)
        # base case: origin -> destination routes not found (with max_connections-many connections or less)
        if num_connections == args.max_layovers: return

        # for airport in set of all_airports
        for airport in all_airports:
            if airport in flight_path: continue # prevent cyclical routes
            for airline in airlines:
                if FlightFinder.flight_exists(airline, flight_path[-1], airport):
                    route_finder(flight_path + [airport], airline_path + [airline], num_connections+1)

    for airport in airports_origin: route_finder([airport], [], -1)

    startdate, enddate = FlightFinder.get_start_end_date(args.startdate, args.length)
    if len(routes) * ((enddate-startdate).days + 1) > 18:
        s = "[flight_scaper.py] You are trying to print out too many flights -- comment this line out if this is intentional, otherwise adjust your search"
        s += f"\n We've found {len(routes)} city-to-city possibilities with {((enddate-startdate).days + 1)} dates to look at!"
        if args.debug: print(f"Debug mode enabled, bypassing this exit code: {s}")
        else: exit(s)

    routes = sorted(routes, key=lambda route: len(route))

    # print(routes)
    for route in routes:
        print(route)
    exit()

    stopLoop = False
    real_routes = []
    for route in routes:
        real_flights = []
        for theoretical_flight in route:
            # try:
                real_flights.append(
                    theoretical_flight.get_real_flights(startdate, enddate) # all flights from origin to route on this day
                )
            # except:
            #     print("Exception encountered -- exitting now")
            #     stopLoop = True
            #     break
        real_routes.append(real_flights)
        if stopLoop: break

    full_real_routes = defaultdict(lambda: [])
    def getFullRealRoutes(route, path):
        if route == []:
            temp_flight = Flight(
                sum([ int(flight.cost) for flight in path]),
                [ FlightSegment(f.getOrigin(), f.getDestination(), f.getTimeDepart(), f.getTimeArrive(), list(f.getAirlines())[0]) for f in path ]
            )
            if temp_flight.hasValidPath():
                try:
                    full_real_routes[(path[0].getOrigin(), path[-1].getDestination())].append(
                        temp_flight
                    )
                except:
                    print(route, path, sep="\n")
            return
        
        for o_to_d_option in route[0]: getFullRealRoutes(route[1:], path + [o_to_d_option])

    for route in real_routes:
        if route: getFullRealRoutes(route, [])

    # print filtered and sorted flights
    filter_flights = lambda flight: (flight.cost <= args.filter_price) and (flight.getDuration() <= args.filter_duration)
    time_cost = lambda flight: flight.cost + flight.getDuration()

    final_routes = {}
    num_final_routes = 0
    for k in full_real_routes:
        filtered = sorted(filter(filter_flights, full_real_routes[k]), key=time_cost)
        if filtered:
            final_routes[k] = filtered
            num_final_routes += len(final_routes[k])
    
    print(f"We've discovered {num_final_routes}-many flights that fit your needs!")
    if num_final_routes < 30: print("You way want to add filters (if you haven't) below to help narrow down your search :)")

    for (o, d) in final_routes:
        if not (o in airports_origin and d in airports_destination): continue

        print(f"{o} -> {d}")
        for f in final_routes[(o,d)]: print(f"\t{f}")

if __name__ == "__main__":
    main()
