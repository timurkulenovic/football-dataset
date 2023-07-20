import pandas as pd
import selenium.common.exceptions
from bs4 import BeautifulSoup as bs
import time
import requests
from other.selenium_init import selenium_driver
from helpers import month_to_number, col_names, events_to_string
import os
import sys


def clean_parts(parts, lg):
    if lg == "champions_league" or "europa_league":
        parts = [(part, value) for part, value in parts if
                 all(el not in part for el in ["Grp", "grp", "Qualification"])]
    return parts


def get_links(driver, league, leagues_links, first_season, last_season):
    href = leagues_links[league]
    driver.get(f"{BASE_URL}{href}")
    time.sleep(1)
    try:
        cookie_button = driver.find_element("xpath", f"//button[@mode='primary']")
        cookie_button.click()
    except selenium.common.exceptions.NoSuchElementException:
        print("No cookie button")
    bs_main = bs(driver.page_source, "html.parser")
    possible_seasons = [(opt.text.strip(), opt.get("value")) for opt in
                        bs_main.find("select", {"id": "seasons"}).find_all("option")]
    chosen_seasons = [(seas, val) for seas, val in possible_seasons if first_season <= seas <= last_season]
    links = {}
    for i, (season_str, season_value) in enumerate(chosen_seasons):
        d.find_element("xpath", f"//select[@id='seasons']/option[@value='{season_value}']").click()
        time.sleep(1.5)
        source = d.page_source
        parts = [("regular", None)]
        bs_main = bs(driver.page_source, "html.parser")
        if bs_main.find("select", {"id": "stages"}):
            parts = [(opt.text.strip(), opt.get("value")) for opt in
                     bs_main.find("select", {"id": "stages"}).find_all("option")]
            parts = clean_parts(parts, league)
        # print([part for part, value in parts])
        for part, part_value in parts:
            if part != "regular":
                d.find_element("xpath", f"//select[@id='stages']/option[@value='{part_value}']").click()
                time.sleep(1.5)
            links[(season_str, part)] = []
            while True:
                bs_main = bs(d.page_source, "html.parser")
                links[(season_str, part)].extend([t.find("a").get("href") for t in bs_main.find_all("div", {"class": "result"})])
                d.find_element("xpath", f"//span[@class='ui-icon ui-icon-triangle-1-w']").click()
                time.sleep(1)
                if d.page_source != source:
                    source = d.page_source
                else:
                    break
    print(links)
    return links


def get_games_data(driver, leagues_links, league, first_season, end_season):
    links = get_links(driver, league, leagues_links, first_season, end_season)
    for (season, part) in links:
        matches = []
        for i, link in enumerate(links[(season, part)][350:]):
            print(i, end=" ")
            driver.get(f"{BASE_URL}{link}")
            time.sleep(10)
            bs_match = bs(d.page_source, "html.parser")
            if bs_match.find("div", {"class": "score"}) is None:
                continue
            if "Additional security check" in d.page_source:
                print("Security check")
                driver.find_element("xpath", f"//div[@class='recaptcha-checkbox-border']").click()

            # Main info
            h_team_name = bs_match.find("div", {"data-field": "home"}).find("a").text
            a_team_name = bs_match.find("div", {"data-field": "away"}).find("a").text
            venue = bs_match.find("span", {"class": "venue"}).get("title")
            att = bs_match.find("span", {"class": "attendance"}).get("title")
            ref = None
            if bs_match.find("span", {"class": "referee"}):
                ref = bs_match.find("span", {"class": "referee"}).get("title")
            kick_off = bs_match.find("dt", string="Kick off:").nextSibling.text.strip()
            day, month, year = bs_match.find("dt", string="Date:").nextSibling.text.split(",")[1].strip().split("-")
            date = f"20{year}/{month_to_number(month)}/{day}"

            # Goals
            ht = bs_match.find("dt", string="Half time:")
            h_ht_goals, a_ht_goals = None, None
            if ht:
                h_ht_goals, a_ht_goals = ht.nextSibling.text.split(" : ")
            ft = bs_match.find("dt", string="Full time:")
            h_ft_goals, a_ft_goals = None, None
            if ft:
                h_ft_goals, a_ft_goals = ft.nextSibling.text.split(" : ")

            # Match centre statistics
            bs_match_centre = bs_match.find("div", {"class": "match-centre-stats", "data-mode": "team"})
            stat_variables = ["ratings", "shotsTotal", "shotsOnPost", "shotsOnTarget", "shotsOffTarget", "shotsBlocked",
                              "possession", "touches", "passSuccess", "passesTotal", "passesAccurate", "passesKey",
                              "dribblesWon", "dribblesAttempted", "dribbledPast", "dribbleSuccess", "aerialsWon",
                              "aerialSuccess", "offensiveAerials", "defensiveAerials", "tackleSuccessful",
                              "tacklesTotal", "tackleUnsuccesful", "tackleSuccess", "clearances", "interceptions",
                              "cornersTotal", "cornerAccuracy", "dispossessed", "errors", "foulsCommited", "offsidesCaught"]
            match_centre = []
            for s_var in stat_variables:
                bs_var = bs_match_centre.find("li", {"data-for": s_var})
                h_var_value = bs_var.find("span", {"data-field": "home"}).text
                a_var_value = bs_var.find("span", {"data-field": "away"}).text
                match_centre.extend([h_var_value, a_var_value])

            # Home events
            bs_timeline_home = bs_match.find("div", {"class": "timeline-events", "data-field": "home"})
            home_events = [events_to_string(event) for event in bs_timeline_home.find_all("div", {"class": "timeline-event"})]
            home_events_joined = ";".join(list(filter(None, home_events)))

            # Away events
            bs_timeline_away = bs_match.find("div", {"class": "timeline-events", "data-field": "away"})
            away_events = [events_to_string(event) for event in bs_timeline_away.find_all("div", {"class": "timeline-event"})]
            away_events_joined = ";".join(list(filter(None, away_events)))

            # Create list of data for the match
            match = [season, part, date, kick_off, venue,
                     att, h_team_name, a_team_name, ref,
                     h_ht_goals, a_ht_goals, h_ft_goals, a_ft_goals,
                     *match_centre, home_events_joined, away_events_joined]
            print(match)
            matches.append(match)

        # Export to CSV
        df = pd.DataFrame(data=matches, columns=col_names)
        df.to_csv(f"../data/{league}/games/seasons/{league}_games_{season.replace('/', '_')}.csv", index=False)


def join_seasons_data(league):
    dir_path = f"../data/{league}/games/seasons"
    season_dfs = [pd.read_csv(f"{dir_path}/{file}") for file in os.listdir(dir_path)]
    df = pd.concat(season_dfs)
    df.to_csv(f"../data/{league}/games/games.csv")


if __name__ == "__main__":
    leagues = {"premier_league": "/Regions/252/Tournaments/2/England-Premier-League",
               "serie_a": "/Regions/108/Tournaments/5/Italy-Serie-A",
               "la_liga": "/Regions/206/Tournaments/4/Spain-LaLiga",
               "bundesliga": "/Regions/81/Tournaments/3/Germany-Bundesliga",
               "ligue_1": "/Regions/74/Tournaments/22/France-Ligue-1",
               "champions_league": "/Regions/250/Tournaments/12/Europe-Champions-League",
               "europa_league": "/Regions/250/Tournaments/30/Europe-Europa-League",
               "portugal_nos": "/Regions/177/Tournaments/21/Portugal-Liga-NOS",
               "eredivisie": "/Regions/155/Tournaments/13/Netherlands-Eredivisie",
               "brasil": "/Regions/31/Tournaments/95/Brazil-Brasileir%C3%A3o",
               "argentina": "/Regions/11/Tournaments/68/Argentina-Liga-Profesional",
               "mls": "/Regions/233/Tournaments/85/USA-Major-League-Soccer",
               "turkey": "/Regions/225/Tournaments/17/Turkey-Super-Lig",
               "russia": "/Regions/182/Tournaments/77/Russia-Premier-League"
               }

    BASE_URL = "https://www.whoscored.com"
    s = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

    d = selenium_driver(BASE_URL, "other/geckodriver")
    # _, arg_league, s_season, e_season = list(sys.argv)
    arg_league = "ligue_1"
    s_season = "2022/2023"
    e_season = "2022/2023"
    get_games_data(d, leagues, arg_league, s_season, e_season)
    join_seasons_data(arg_league)
    d.close()
