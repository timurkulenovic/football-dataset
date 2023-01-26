def month_to_number(mth):
    month_dict = {
        "Jan": "1",
        "Feb": "2",
        "Mar": "3",
        "Apr": "4",
        "May": "5",
        "Jun": "6",
        "Jul": "7",
        "Aug": "8",
        "Sep": "9",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    return month_dict[mth]


def events_to_string(html):
    event = None
    if html.get("data-event-satisfier-goalnormal") is not None:
        event = "goal"
    elif html.get("data-event-satisfier-penaltyscored") is not None:
        event = "penalty_scored"
    elif html.get("data-event-satisfier-goalown") is not None:
        event = "own-goal"
    elif html.get("data-event-satisfier-keeperpenaltysaved") is not None:
        event = "penalty_saved"
    elif html.get("data-event-satisfier-penaltymissed") is not None:
        event = "penalty-missed"
    elif html.get("data-event-satisfier-yellowcard") is not None:
        event = "yellow-card"
    elif html.get("data-event-satisfier-secondyellow") is not None:
        event = "second-yellow"
    elif html.get("data-event-satisfier-redcard") is not None:
        event = "red-card"
    elif html.get("data-event-satisfier-errorleadstogoal") is not None:
        event = "error-to-goal"
    elif html.get("data-event-satisfier-shotonpost") is not None:
        event = "shot-on-post"
    elif html.get("data-event-satisfier-clearanceofftheline") is not None:
        event = "clearance-off-the-line"
    else:
        return None
    minute = int(html.get("data-minute")) + 1
    return f"{event}({minute})"


col_names = [
                "Season", "Part", "Date", "Time", "Venue",
                "Attendance", "H_Team", "A_Team", "Referee",
                "H_HT_Goals", "A_HT_Goals", "H_FT_Goals", "A_FT_Goals",
                'H_Ratings', 'A_Ratings', 'H_ShotsTotal', 'A_ShotsTotal', 'H_ShotsOnPost', 'A_ShotsOnPost', 'H_ShotsOnTarget',
                'A_ShotsOnTarget', 'H_ShotsOffTarget', 'A_ShotsOffTarget', 'H_ShotsBlocked', 'A_ShotsBlocked', 'H_Possession',
                'A_Possession', 'H_Touches', 'A_Touches', 'H_PassSuccess', 'A_PassSuccess', 'H_PassesTotal', 'A_PassesTotal',
                'H_PassesAccurate', 'A_PassesAccurate', 'H_PassesKey', 'A_PassesKey', 'H_DribblesWon', 'A_DribblesWon',
                'H_DribblesAttempted', 'A_DribblesAttempted', 'H_DribbledPast', 'A_DribbledPast', 'H_DribbleSuccess',
                'A_DribbleSuccess', 'H_AerialsWon', 'A_AerialsWon', 'H_AerialSuccess', 'A_AerialSuccess', 'H_OffensiveAerials',
                'A_OffensiveAerials', 'H_DefensiveAerials', 'A_DefensiveAerials', 'H_TackleSuccessful', 'A_TackleSuccessful',
                'H_TacklesTotal', 'A_TacklesTotal', 'H_TackleUnsuccesful', 'A_TackleUnsuccesful', 'H_TackleSuccess',
                'A_TackleSuccess', 'H_Clearances', 'A_Clearances', 'H_Interceptions', 'A_Interceptions', 'H_CornersTotal',
                'A_CornersTotal', 'H_CornerAccuracy', 'A_CornerAccuracy', 'H_Dispossessed', 'A_Dispossessed', 'H_Errors',
                'A_Errors', 'H_FoulsCommited', 'A_FoulsCommited', 'H_OffsidesCaught', 'A_OffsidesCaught', 'H_Events', 'A_Events'
            ]
