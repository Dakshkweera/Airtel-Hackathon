"""Order tracker: 5 stages, expected date = today + the largest install time in the plan."""
import random
from datetime import date, datetime, timedelta

from .i18n import STAGES, pick


def create(S, quote):
    days = quote["totals"]["expected_days"]
    o = dict(id="UD-" + str(random.randint(100000, 999999)), stage=0,
             expected_date=(date.today() + timedelta(days=days)).isoformat(), expected_days=days,
             monthly=quote["totals"]["monthly"], setup=quote["totals"]["setup"], plan=quote["plan_name"],
             history=[dict(stage=0, at=datetime.now().strftime("%d %b, %I:%M %p"))])
    return o


def advance(o):
    if o["stage"] < len(STAGES) - 1:
        o["stage"] += 1
        o["history"].append(dict(stage=o["stage"], at=datetime.now().strftime("%d %b, %I:%M %p")))
    return o


def view(o, lang):
    return dict(o, stages=[pick(s, lang) for s in STAGES], done=o["stage"] == len(STAGES) - 1)
