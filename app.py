from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "taxi_app_secret_2025"

# YOUR WEBHOOK URL FROM STEP 2 (paste here)
GOOGLE_WEBHOOK = "https://script.google.com/macros/s/AKfycbwD_1XiPRVNuRtBFprVPWbbGkhcfFYc-BjFn6DsUoghKzBUE6gqT2Yqo7cAbGRheF0j/exec"

VALID_USERS = {"siva": "5218"}

CHENNAI_LOCATIONS = [
    "Adambakkam", "Adyar", "Alandur", "Ambattur", "Anna Nagar", "Ashok Nagar",
    "Besant Nagar", "Chrompet", "Egmore", "Guindy", "Kilpauk", "Kodambakkam",
    "Mylapore", "Nanganallur", "Nungambakkam", "Perambur", "Poonamallee",
    "Porur", "Saidapet", "Sholinganallur", "T. Nagar", "Tambaram",
    "Thiruvanmiyur", "Thuraipakkam", "Velachery", "Villivakkam", "Virugambakkam","West Mambalam",
    "Tiruporur",
    "Anagaputhur",
    "Kundruthur",
    "Mambakkam",
    "Thalambur",
    "Madambakkam",
    "Guduvancherry",
    "Karapakkam",
    "Sholinganallur",
    "Perumbakkam",
    "Asthanapuram",
    "Kanthanchavady",
    "Navallur",
    "Vavin",
    "Pamal",
    "Chemencherry"
]

TRIP_TYPES = ["DROP", "PICK-UP"]
PASSENGER_COUNTS = [str(i) for i in range(1, 7)]
ESCORT_OPTIONS = ["YES", "NO"]
TIME_OPTIONS = [
    "12:00 AM", "12:30 AM", "1:00 AM", "1:30 AM", "2:00 AM", "2:30 AM", "3:00 AM", "3:30 AM",
    "4:00 AM", "4:30 AM", "5:00 AM", "5:30 AM", "6:00 AM", "6:30 AM", "7:00 AM", "7:30 AM",
    "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
    "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM",
    "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM",
    "8:00 PM", "8:30 PM", "9:00 PM", "9:30 PM", "10:00 PM", "10:30 PM", "11:00 PM", "11:30 PM"
]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in VALID_USERS and VALID_USERS[username] == password:
            session["username"] = username
            return redirect(url_for("trip_form"))
        return render_template("login.html", error="Invalid login")
    return render_template("login.html")

@app.route("/trip", methods=["GET", "POST"])
def trip_form():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "username": session["username"],
            "date": request.form.get("trip_date"),
            "time": request.form.get("trip_time"),
            "location": request.form.get("location"),
            "tripType": request.form.get("trip_type"),
            "passengers": request.form.get("passengers"),
            "escort": request.form.get("escort")
        }

        # Send to Google Sheets LIVE
        try:
            response = requests.post(GOOGLE_WEBHOOK, json=data)
            if response.status_code == 200:
                return redirect(url_for("success"))
            else:
                return render_template("trip_form.html", error="Save failed", 
                                     locations=CHENNAI_LOCATIONS, trip_types=TRIP_TYPES,
                                     passenger_counts=PASSENGER_COUNTS, escort_options=ESCORT_OPTIONS,
                                     time_options=TIME_OPTIONS)
        except:
            return render_template("trip_form.html", error="Network error", 
                                 locations=CHENNAI_LOCATIONS, trip_types=TRIP_TYPES,
                                 passenger_counts=PASSENGER_COUNTS, escort_options=ESCORT_OPTIONS,
                                 time_options=TIME_OPTIONS)

    return render_template("trip_form.html", locations=CHENNAI_LOCATIONS, 
                         trip_types=TRIP_TYPES, passenger_counts=PASSENGER_COUNTS,
                         escort_options=ESCORT_OPTIONS, time_options=TIME_OPTIONS)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
