import random, time, requests, json, html
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import browsercookie
import argparse
from Modules.FlightFinder import FlightFinder
from Modules.FlightConstants import FlightConstants
from Modules.Flight import TheoreticalFlight

from random_user_agent.user_agent import UserAgent
# def get_flight_html(origin, date, session, cjs, roundtrip, start_index=0, destinations = all_destinations):

#     date_str = date.strftime("%b-%d,-%Y").replace("-", "%20")
#     #f = open("destinations.txt", "a")
#     #f.write("Origin: " + origin + "\n")
#     destination_keys = list(destinations.keys()) # Retrieve a list of destination keys
#     for i in range(start_index, len(destination_keys)):
#         dest = destination_keys[i]

#         if dest == origin:
#             print("cannot search between identical origin and destination")
#             continue

#         # Choose a random User-Agent header
#         header = {
#             "User-Agent": UserAgent().get_random_user_agent(),
#         }
#         cj = browsercookie.chrome() if cjs else None
#         time.sleep(random.uniform(0.5,1.5))
#         #time.sleep(random.uniform(0.5,1.5))
#         # Get schedule data for the route
#         schedule_url = f"https://booking.flyfrontier.com/Flight/RetrieveSchedule?calendarSelectableDays.Origin={origin}&calendarSelectableDays.Destination={dest}"
#         schedule_response = requests.Session().get(schedule_url, headers=header, cookies=cj) if cjs else requests.Session().get(schedule_url, headers=header)
            
#         if schedule_response.status_code == 200:
#             schedule_data = schedule_response.json()
#             disabled_dates = schedule_data["calendarSelectableDays"]["disabledDates"]
#             last_available_date = schedule_data["calendarSelectableDays"]["lastAvailableDate"]

#             # Convert the input date to the same format as the disabled dates list
#             formatted_date = date.strftime("%m/%d/%Y")

#             # Check if the date is in the list of disabled dates
#             if formatted_date in disabled_dates or last_available_date == "0001-01-01 00:00:00":
#                 print(f"{i}. No flights available on {formatted_date} from {origin} to {dest}. Date skipped.")
#                 continue
#         else:
#             print(f"{i}. Problem accessing URL: code {schedule_response.status_code}\n url = " + schedule_url)

        
#         # Mimic human-like behavior by adding delays between requests
#         #delay = random.uniform(2, 5)  # Random delay between 2 to 5 seconds
#         #time.sleep(delay)
#         time.sleep(random.uniform(0.5,1.5))
#         url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={origin}&d1={dest}&dd1={date_str}&ADT=1&mon=true&promo="
#         response = session.get(url, headers=header, cookies=cj) if cjs else session.get(url, headers=header)
#         if (response.status_code == 200):
#             decoded_data = extract_html(response)
#             if (decoded_data != "NoneType"):
#                 orgin_success = extract_json(decoded_data, origin, dest, date, roundtrip)
#                 if(roundtrip == 1 & orgin_success):
#                     new_dest = {origin: all_destinations[origin]}
#                     # 1 = trigger roundtrip
#                     # 0 = no roundtrip
#                     # -1 = in roundtrip recurssion 
#                     get_flight_html(dest, (date+timedelta(days=1)), session, cjs, -1, 0, new_dest)
#                     roundtrip = 1 # reset var for the next dest
#                 #f.write(dest + ",")
#         else:
#             print(f"{i}. Problem accessing URL: code {response.status_code}\n url = " + url)
#             break
#     #f.close()

# def extract_json(flight_data, origin, dest, date, roundtrip):
#     # Extract the flights with isGoWildFareEnabled as true
#     try:
#         flights = flight_data["journeys"][0]["flights"]
#     except (TypeError, KeyError):
#         return 0
#     if (flights == None):
#         return 0
#     go_wild_count = 0

#     for flight in flights:
#         if flight["isGoWildFareEnabled"]:
#             if (go_wild_count == 0):
#                 print(f"\n{"{} to {}: {}".format(origin, dest, all_destinations[dest]) if roundtrip != -1 else "**Return flight"} available:")
#                 #print(f"\n{"{origin} to {dest}: {all_destinations[dest]}" if roundtrip!=-1 else "Return flight"} available:")
#             go_wild_count+=1
#             info = flight["legs"][0]
#             print(f"flight {go_wild_count}. {flight["stopsText"]}")
#             print(f"\tDate: {info["departureDate"][5:10]}")
#             print(f"\tDepart: {info["departureDateFormatted"]}")
#             print(f"\tTotal flight time: {flight["duration"]}")
#             print(f"Price: ${flight["goWildFare"]}")
#             # if go wild seats value is provided
#             if flight["goWildFareSeatsRemaining"] is not None:
#                 print(f"Go Wild: {flight["goWildFareSeatsRemaining"]}\n")
    
#     if (go_wild_count == 0):
#         print(f"No {"next day return " if roundtrip==-1 else ""}flights from {origin} to {dest}")
#         return 0
#     else:
#         if(roundtrip==-1):
#             roundtrip_avail[origin] = all_destinations.get(origin)
#         else:
#             destinations_avail[dest] = all_destinations.get(dest)
#         print(f"{origin} to {dest}: {go_wild_count} GoWild {"return " if roundtrip==-1 else""}flights available for {date.strftime("%A, %m-%d-%y")}")
#     return 1

# def extract_html(response):
#     # Parse the HTML source using BeautifulSoup
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     # Find all <script> tags with type="text/javascript" and extract their contents
#     scripts = soup.find("script", type="text/javascript")
#     decoded_data = html.unescape(scripts.text)
#     decoded_data = decoded_data[decoded_data.index("{"):decoded_data.index(";")-1]
#     return json.loads(decoded_data)

# def print_dests(origin):
#     print(f"\n{len(destinations_avail)} destinations found from {origin}:")
#     for dest, name in destinations_avail.items():
#         print(f"{"**" if dest in roundtrip_avail else ""}{dest}: {name}")
#     print("** = next day return flight available")

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

    max_connections = 1 # TODO: make parameter later
    # make chains of length up to max_connections with no repititions
    all_airports = FlightFinder.get_airports()
    flight_graph = {}
    def addFlightGraphLayers(graph, path, layer):
        if layer == max_connections: return
        for airport in all_airports:
            if airport in path: continue
            graph[airport] = {}
            addFlightGraphLayers(graph[airport], path + [airport], layer+1)

    addFlightGraphLayers(flight_graph, [], 0)

    

    # filter out all impossible origin-to-destination (due to airline not currently flying those routes)
    
    theoretical_flights = [] # List[from, to]
    for origin in airports_origin:
        for destination in airports_destination:
            for airline in airlines:
                if FlightFinder.flight_exists(airline, origin, destination):
                    theoretical_flights.append(
                        TheoreticalFlight(origin, destination, airline)
                    )

    startdate, enddate = FlightFinder.get_start_end_date(args.startdate, args.length)
    if len(theoretical_flights) * ((enddate-startdate).days + 1) > 10:
        s = "[flight_scaper.py] You are trying to print out too many flights -- comment this line out if this is intentional, otherwise adjust your search"
        s += f"\n We've found {len(theoretical_flights)} city-to-city possibilities with {((enddate-startdate).days + 1)} dates to look at!"
        if args.debug: print(f"Debug mode enabled, bypassing this exit code: {s}")
        else: exit(s)

    # filter flights based on all google flights available for this airline
    possible_real_flights = []
    for tf in theoretical_flights:
        possible_real_flights += tf.get_real_flights(startdate, enddate)

    print(possible_real_flights)


    exit()
    
    origins = [o.upper() for o in args.origin]
    startdate = datetime.strptime(args.startdate, "%m-%d-%Y")
        
    enddate = startdate + timedelta(days=args.length)
    # session = requests.Session()

    # fly_date = startdate
    # while fly_date <= enddate:
    #     print(f"\nFlights for {fly_date.strftime("%A, %m-%d-%y")}:")
    #     for origin in origins:
    #         get_flight_html(origin, fly_date, session, cjs, roundtrip, resume)
    #         print_dests(origin)
    #     fly_date = fly_date + timedelta(days=1)



if __name__ == "__main__":

    # output = FlightConstants.get_all_airports()
    # for airport in output:
    #     def get_address_from_IACA(airport):
    #         return ""
    #     print(f"\"{airport}\": \"{get_address_from_IACA(airport)}\",")
    # print(output)

    main()
