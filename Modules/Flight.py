import random, time, requests, json, html
import browsercookie
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import os
from Modules.FlightConstants import FlightConstants
from random_user_agent.user_agent import UserAgent
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Flight():
    
    def __init__(self, cost, path) -> None:
        self.cost = cost
        self.path = path

    def getOrigin(self):
        return self.path[0].origin

    def getDestination(self):
        return self.path[-1].destination

    def getTimeDepart(self):
        return self.path[0].time_depart

    def getTimeArrive(self):
        return self.path[-1].time_arrive
    
    def getAirlines(self):
        return set([flight_segment.airline for flight_segment in self.path])
    
    def getDuration(self):
        flight_duration = self.getTimeArrive() - self.getTimeDepart()
        return flight_duration.days*24 + flight_duration.seconds // (60*60)
    
    def hasValidPath(self):
        last_airport = None
        last_timearrive = datetime(1,1,1)

        for fs in self.path:

            if last_airport in [None, fs.getOrigin()]: last_airport = fs.getDestination()
            else: return False

            if last_timearrive < fs.getTimeDepart() - timedelta(minutes=FlightConstants.min_layover_minutes): last_timearrive = fs.getTimeArrive()
            else: return False

        return True

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return f"{self.cost} ({self.getOrigin()}) -> ({self.getDestination()}) [Duration: {self.getDuration()} hours]"
    
    def __lt__(self, other):
        return self.cost < other.cost
    
    def toJSON(self):
        return {
            'cost': self.cost,
            'path': [flight_segment.toJSON() for flight_segment in self.path],
        }
    
    def fromJSON(data):
        return Flight(data["cost"], [FlightSegment.fromJSON(fs) for fs in data["path"]] )
    
class FlightSegment(Flight):
    def __init__(self, origin, destination, time_depart, time_arrive, airline) -> None:
        self.origin=origin
        self.destination=destination
        self.time_depart=time_depart
        self.time_arrive=time_arrive
        self.airline=airline

    def getOrigin(self):
        return self.origin

    def getDestination(self):
        return self.destination

    def getTimeDepart(self):
        return self.time_depart

    def getTimeArrive(self):
        return self.time_arrive
    
    def toJSON(self):
        return {
            'origin': self.origin,
            'destination': self.destination,
            'time_depart': self.time_depart.strftime("%Y-%m-%d %H:%M"),
            'time_arrive': self.time_arrive.strftime("%Y-%m-%d %H:%M"),
            'airline': self.airline,
        }
    
    def fromJSON(data):
        convertStrToDatetime = lambda str: datetime.strptime(str, '%Y-%m-%d %H:%M')
        return FlightSegment(
            data["origin"], 
            data["destination"], 
            convertStrToDatetime(data["time_depart"]), 
            convertStrToDatetime(data["time_arrive"]), 
            data["airline"]
        )

class TheoreticalFlight(FlightSegment):
    def __init__(self, origin, destination, airline) -> None:
        super().__init__(origin, destination, None, None, airline)

    def get_real_flights_from_date(self, date):
        # path = "yyyy-mm-dd origin destination"
        filepath = f"FlightData/{self.airline}_{date.strftime('%Y-%m-%d')}_{self.origin}_{self.destination}.json"
        if os.path.isfile(filepath): # get flight info from file stored json
            # Opening JSON file
            output = []
            with open(filepath, "r") as f:
                for flight in json.load(f):
                    output.append(
                        Flight.fromJSON(flight)
                    )
            return output
        
        getHeader = lambda: {
            "User-Agent": UserAgent().get_random_user_agent(),
        }
        request_wrapper = lambda url: requests.Session().get(url, headers=getHeader(), cookies=random.choice([browsercookie.chrome(), None]))

        shouldFetchNewData = input(f"You are missing data for {filepath} and are about to make a request to fetch it from the internet. Type `yes` to continue or anything else to abort.\n\t")
        if not shouldFetchNewData in ['yes', 'skip']:
            exit("Did not type `yes`... returning no info now!")
        if shouldFetchNewData in ['skip']:
            return []
        
        # request to get new data
        time.sleep(random.uniform(5, 20))
        if self.airline == "FFT":
            # check to see if there's GoWild availability
            from Modules.selenium import initializeSelenium
            service, driver = initializeSelenium()

            goWild_url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={self.origin}&d1={self.destination}&dd1={date.strftime('%b-%d,-%Y').replace('-', '%20')}&ADT=1&mon=true&promo="
            driver.get(goWild_url)
            WebDriverWait(driver, 60*60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ibe-flight-info-container")))
            html_data = driver.page_source
            soup = BeautifulSoup(html_data, 'html.parser')

            
            real_flights = []
            for row in soup.find_all('div', class_ = 'ibe-flight-info-row'):
                setStringIfReal = lambda x: x if not x else x.string
                getFairAsOptionalString = lambda suffix: setStringIfReal(row.find('div', class_ = f"ibe-flight-farebox{suffix}").find('div', class_ = 'ibe-text-like-h4'))
                standard = getFairAsOptionalString("")
                discount_den = getFairAsOptionalString("-special-fare-green")
                gowild = getFairAsOptionalString("-special-fare-brown")

                cost_list = []
                for price in [standard, discount_den, gowild]:
                    if price != None: cost_list.append(price)
                
                # skip items with no price (unavailable, for some reason) -> could just be the last flight in flights is always the issue
                if not len(cost_list): continue
                
                cost = min([c[1:] for c in cost_list])
                isGoWild = cost == gowild[1:]
                
                flights = row.find_all('div', class_ = 'ibe-flight--segment')
                if not flights: flights = [row]

                global last_datetime
                last_datetime = datetime(1, 1, 1)
                def getNextDatetime(time):
                    global last_datetime
                    d = datetime.strptime(date.strftime('%Y-%m-%d ')+time, '%Y-%m-%d %I:%M %p')
                    while d < last_datetime: d = d + timedelta(days=1)

                    return (last_datetime := d)

                flight_segments = []
                for flight in flights:
                    clear_nl = lambda str: map(lambda content: content.string, filter(lambda content: content != "\n", flight.find('div', class_ = f"ibe-flight-time-{str}").contents))
                    c1, t1 = clear_nl('depart')
                    c2, t2 = clear_nl('arrive')

                    flight_segments.append(
                        FlightSegment(c1, c2, getNextDatetime(t1), getNextDatetime(t2), self.airline)
                    )
                
                real_flights.append(
                    Flight(cost, flight_segments)
                )
            
            # set realFlights to json
            with open(filepath, "w") as f:
                f.write(json.dumps([real_flight.toJSON() for real_flight in real_flights]))
            
            return self.get_real_flights_from_date(date)
        else:
            # TODO: search google flights / some other web scraper to get these flights
            exit("Cannot get real flight from date -- please wait for update where this is implemented")


    def get_real_flights(self, start, end):
        flights = []
        
        day = timedelta(days=1)
        for i in range( (end - start).days+1):
            date = start + i*day
            flights += self.get_real_flights_from_date(date)
        return flights

    def getOrigin(self):
        return self.origin

    def getDestination(self):
        return self.destination
    
    def __str__(self) -> str:
        return f"({self.origin}) -> ({self.destination}) w/ {self.airline}"