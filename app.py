import os
import json
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from ics import Calendar
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# --- TES FICHIERS ICS LOCAUX ---
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=6579&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=6581&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3911&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8

#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3930&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3957&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3941&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
#https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3962&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8
ICS_FILES = {
    "1-I3": "edt1.ics",
    "2-I3": "edt2.ics",
    "3-I3": "edt3.ics",
    "A43-P2-08": "ang.ics",
    "EIMI43_P2-2": "msh1.ics",
    "ECNV43-P2-02": "msh2.ics",
    "EISI43-P2-01": "eisi.ics",
}


flask_app = Flask(__name__)


# Fuseau horaire par défaut
TZ = pytz.timezone("Europe/Paris")

def load_events(filename):
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as f:
        cal = Calendar(f.read())

    events = []
    for e in cal.events:
        start = e.begin.datetime
        end = e.end.datetime

        # Normalisation timezone → Europe/Paris
        if start.tzinfo is None:
            start = TZ.localize(start)
        else:
            start = start.astimezone(TZ)

        if end.tzinfo is None:
            end = TZ.localize(end)
        else:
            end = end.astimezone(TZ)

        events.append({
            "title": e.name,
            "start": start,
            "end": end,
            "location": e.location if e.location else "",
        })
    return events

@flask_app.route("/", methods=["GET"])
def index():
    # default to the first available ICS key if edt not provided
    default_option = next(iter(ICS_FILES.keys()))
    option = request.args.get("edt", default_option)
    filename = ICS_FILES.get(option, list(ICS_FILES.values())[0])
    events = load_events(filename)
    # compute available weeks based on events in this file
    if events:
        first_event = min(events, key=lambda x: x["start"])["start"]
        last_event = max(events, key=lambda x: x["end"])["end"]
    else:
        # fallback to current date if no events
        now = datetime.now(TZ)
        first_event = now
        last_event = now

    # compute first monday and last monday (week starts)
    first_monday = (first_event - timedelta(days=first_event.weekday())).date()
    last_monday = (last_event - timedelta(days=last_event.weekday())).date()

    # build list of week start dates (ISO strings) and labels
    weeks = []
    week_labels = []
    cur = first_monday
    while cur <= last_monday:
        weeks.append(cur.isoformat())
        week_labels.append(cur.strftime("%A %d/%m/%Y"))
        cur = cur + timedelta(days=7)

    # selected week from query param (YYYY-MM-DD) or default to current week if in range
    week_param = request.args.get("week")
    selected_week_date = None
    if week_param:
        try:
            selected_week_date = datetime.strptime(week_param, "%Y-%m-%d").date()
        except Exception:
            selected_week_date = None

    today = datetime.now(TZ).date()
    if not selected_week_date:
        # prefer today's week if within range, else first available week
        if first_monday <= today <= last_monday + timedelta(days=6):
            selected_week_date = today - timedelta(days=today.weekday())
        else:
            selected_week_date = first_monday

    # clamp to available week starts
    if selected_week_date < first_monday:
        selected_week_date = first_monday
    if selected_week_date > last_monday:
        selected_week_date = last_monday

    # compute start and end datetimes for filtering (timezone-aware)
    start_week = TZ.localize(datetime.combine(selected_week_date, datetime.min.time()))
    end_week = start_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    week_events = [e for e in events if start_week <= e["start"] <= end_week]

    # Prepare events for template
    events_js = []
    for e in week_events:
        s = e["start"]
        en = e["end"]
        events_js.append({
            "title": e.get("title") or "(sans titre)",
            "location": e.get("location", ""),
            "day": int(s.weekday()),
            "start": s.strftime("%H:%M"),
            "end": en.strftime("%H:%M"),
            "start_minutes": s.hour * 60 + s.minute,
            "duration": max(1, int((en - s).total_seconds() // 60)),
        })

    # prepare display labels for header (Mon..Sun)
    week_dates = [(selected_week_date + timedelta(days=i)).strftime("%A %d/%m/%Y") for i in range(7)]

    return render_template(
        "calendar.html",
        events_js=events_js,
        week_dates=week_dates,
        weeks=zip(weeks, week_labels),
        selected_week=selected_week_date.isoformat(),
        option=option,
    options=list(ICS_FILES.keys()),
    )

# En mode production derrière Nginx
# Middleware pour le préfixe /ade
app = DispatcherMiddleware(Flask('dummy_app'), {
    '/ade': flask_app
})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    flask_app.run(debug=True, port=port)
