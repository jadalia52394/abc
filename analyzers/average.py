import json
import urllib
import urllib.request
import urllib.error
import datetime
from flask import abort

ENDPOINT = "https://www.speedrun.com/api/v1/"
RUNS = ENDPOINT + "runs?game={}&direction=desc&orderby=date&max=200"


def get_average(id, date=None, ending_date=None):
    verified_endpoint = RUNS.format(id)
    reversed_order = False
    list_of_runs = []
    runs_analyzed_count = 0
    average_daily = []
    if date is not None:
        starting_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        starting_date = None

    if ending_date is not None:
        ending_date = datetime.datetime.strptime(ending_date, "%Y-%m-%d")

    while True:
        date_reached = False

        try:
            verified = json.loads(urllib.request.urlopen(verified_endpoint).read())
        except urllib.error.URLError:
            abort(503)
            return

        for x in verified["data"]:
            try:
                date_of_run = datetime.datetime.strptime(x["date"], "%Y-%m-%d")
            except TypeError:
                continue
            if reversed_order:
                if ending_date is not None and date_of_run > ending_date:
                    date_reached = True
                    break

                if date is not None and date_of_run < starting_date:
                    continue

                if x["id"] in list_of_runs:
                    date_reached = True
                    break
            else:
                if ending_date is not None and date_of_run > ending_date:
                    continue

                if date is not None and date_of_run < starting_date:
                    date_reached = True
                    break

            runs_analyzed_count += 1
            average_daily.append(x["date"])

        if date_reached or starting_date is None:
            break

        else:
            found_endpoint = False
            for x in verified["pagination"]["links"]:
                if x["rel"] == "next":
                    verified_endpoint = x["uri"]
                    if verified_endpoint[-5:] == "10000":
                        verified_endpoint = verified_endpoint.replace('direction=desc', 'direction=asc')
                        verified_endpoint = verified_endpoint[:-13]
                        reversed_order = True
                    found_endpoint = True
                    break
            if not found_endpoint:
                break

    # Average Runs
    dates = []
    for x in average_daily:
        dates.append(datetime.datetime.strptime(x, "%Y-%m-%d").timetuple().tm_yday)
    try:
        range = max(dates) - min(dates)
        return len(average_daily) / range
    except:
        return 0
