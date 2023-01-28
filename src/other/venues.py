import numpy as np
import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import time
from src.other.selenium_init import selenium_driver
from src.other.google_maps_api import google_maps_api_key
import googlemaps
import re


BASE_URL = "https://www.google.com"
s = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}


class VenueScraper:
    def __init__(self, data_dir, chrome_driver_path, sport, venue_type):
        self.data_dir = data_dir
        main_info_path = f"{self.data_dir}/games/games.csv"
        self.main_info = pd.read_csv(main_info_path)
        self.unique_venues = pd.DataFrame(self.main_info["VENUE"].unique(), columns=["VENUE"]).dropna()
        self.full_venues = self.main_info.groupby(['VENUE', 'H_TEAM']).size().reset_index().drop(0, axis=1)
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        self.sport = sport
        self.venue_type = venue_type

    def get_capacity_data(self):
        self.driver = selenium_driver(BASE_URL, self.chrome_driver_path)
        capacities = []
        for index, venue in enumerate(self.unique_venues["VENUE"]):
            print(index, venue, end=" ")
            search_value = f"{venue} {self.venue_type} wikipedia" \
                if f"{self.venue_type.upper()}" not in venue else venue
            capacity = 0
            missing = True

            self.driver.get(f"{BASE_URL}/search?&q={search_value}")
            time.sleep(1)
            google_search = bs(self.driver.page_source, "html.parser")
            side_info = google_search.find("div", {"id": "rhs"})
            if side_info:
                hrefs = [a.get("href") for a in side_info.find_all("a")]
                wiki = [href for href in hrefs if href and "en.wikipedia" in href]
            else:
                hrefs = [a.get("href") for a in google_search.find_all("a")]
                wiki = [href for href in hrefs if href and "en.wikipedia" in href]

            if len(wiki) > 0:
                self.driver.get(wiki[0])
                time.sleep(1)
                wiki_page = bs(self.driver.page_source, "html.parser")
                capacity_string = wiki_page.find("th", string="Capacity")
                if capacity_string:
                    capacity_info = capacity_string.nextSibling.get_text("\n").replace("\n:", "")
                    capacity_info_list = capacity_info.split("\n")
                    basketball_strings = [info for info in capacity_info_list
                                          if self.sport in info or self.sport.capitalize() in info]
                    if len(basketball_strings) > 0:
                        capacity_re = re.findall('[0-9]+', basketball_strings[0].replace(",", ""))
                        capacity = capacity_re[0] if len(capacity_re) > 0 else capacity
                    else:
                        capacity = int(re.findall('[0-9]+', "".join(capacity_info).replace(",", ""))[0])
                missing = False
            capacities.append([venue, capacity, missing])
            print(capacity)

        self.driver.close()
        capacity_df = pd.DataFrame(data=capacities, columns=["VENUE", "CAPACITY", "MANUAL_ENTRY"])
        capacity_df.to_csv(f"{self.data_dir}/venues/capacity_download.csv", index=False)

    def get_location_data(self):
        location_data = []
        gmaps = googlemaps.Client(key=google_maps_api_key)
        for index, venue in enumerate(self.unique_venues["VENUE"]):
            search = f"{venue.replace('ARENA', '').strip()} Basketball Arena"
            geocode_result = gmaps.geocode(search)
            if len(geocode_result) > 0:
                loc = geocode_result[0]["geometry"]["location"]
                lat, lng = loc["lat"], loc["lng"]
                location = ", ".join([comp["long_name"] for comp in geocode_result[0]["address_components"] if
                                      "political" in comp["types"]])
                location_data.append([lat, lng, location, False])
            else:
                location_data.append([None, None, None, True])
        location_df = pd.DataFrame(data=location_data, columns=["LAT", "LNG", "LOCATION", "MANUAL_ENTRY"])
        location_df = pd.concat([self.unique_venues, location_df], axis=1)
        location_df = pd.merge(self.full_venues, location_df, on="VENUE")
        location_df.to_csv(f"{self.data_dir}/venues/location_download.csv", index=False)

    def merge_files(self):
        location_df = pd.read_csv(f"{self.data_dir}/venues/location.csv")
        capacity_df = pd.read_csv(f"{self.data_dir}/venues/capacity.csv")
        df_venues = pd.merge(location_df, capacity_df, on="VENUE")
        df_venues.to_csv(f"{self.data_dir}/venues/venues.csv")


if __name__ == "__main__":
    league = "bundesliga"
    data_dir = os.path.join(f"../../data/{league}")
    chrome_driver_path = "./chromedriver"
    venue_scraper = VenueScraper(data_dir, chrome_driver_path, "football", "arena")
    venue_scraper.get_capacity_data()
    venue_scraper.get_location_data()
    venue_scraper.merge_files()
