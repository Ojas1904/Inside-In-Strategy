from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import json
import calendar
from scanner import run_scan

app = Flask(__name__)

# ===================== LOAD NSE HOLIDAYS ===================== #

with open("holidays.json", "r") as f:
    NSE_HOLIDAYS = set(json.load(f))

# ===================== CONSTANTS ===================== #

MIN_DATE = date(2020, 1, 1)
TODAY = date.today()

# ===================== HELPERS ===================== #

def is_weekend(trade_date):
    # Saturday = 5, Sunday = 6
    return trade_date.weekday() >= 5


def is_holiday(trade_date):
    return trade_date.strftime("%Y-%m-%d") in NSE_HOLIDAYS

# ===================== ROUTES ===================== #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    date_str = request.json.get("date")

    # ---- Basic validation ----
    if not date_str:
        return jsonify({
            "status": "invalid_date",
            "logs": ["❌ No date received from frontend."]
        })

    trade_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # ---- DATE RANGE CHECK (2020 → TODAY) ----
    if trade_date < MIN_DATE or trade_date > TODAY:
        return jsonify({
            "status": "invalid_date",
            "logs": [
                f"❌ Invalid date selected: {trade_date}",
                "📅 Please select a date between 2020 and today."
            ]
        })

    # ---- WEEKEND CHECK ----
    if is_weekend(trade_date):
        day_name = "Saturday" if trade_date.weekday() == 5 else "Sunday"
        return jsonify({
            "status": "closed",
            "reason": day_name,
            "logs": [
                f"📅 {trade_date} is a {day_name}.",
                "🏦 Indian stock markets are closed."
            ]
        })

    # ---- NSE HOLIDAY CHECK ----
    if is_holiday(trade_date):
        return jsonify({
            "status": "closed",
            "reason": "Holiday",
            "logs": [
                f"🏦 {trade_date} is an NSE trading holiday.",
                "📉 No market data available."
            ]
        })

    # ---- VALID TRADING DAY → RUN SCANNER ----
    result = run_scan(date_str)

    # ---- SAFETY CHECK ----
    if not result or not result.get("logs"):
        return jsonify({
            "status": "no_data",
            "logs": [
                "⚠️ No data was fetched.",
                "This may be due to an unexpected market closure or API issue."
            ]
        })

    return jsonify({
        "status": "ok",
        **result
    })

# ===================== ENTRY ===================== #

if __name__ == "__main__":
    app.run(debug=True)
