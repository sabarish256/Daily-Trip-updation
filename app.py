from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "taxi_app_secret_2026"

GOOGLE_WEBHOOK = "https://script.google.com/macros/s/YOUR_WEBHOOK_URL/exec"  # Your webhook

VALID_USERS = {"siva": "5218"}
CHENNAI_LOCATIONS = [
    "Adambakkam", "Adyar", "Alandur", "Ambattur", "Anagaputhur", "Anna Nagar", 
    "Ashok Nagar", "Asthanapuram", "Besant Nagar", "Chemencherry", "Chrompet", 
    "Egmore", "Guduvancherry", "Guindy", "Kanthanchavady", "Karapakkam", 
    "Kilpauk", "Kodambakkam", "Kundruthur", "Madambakkam", "Mambakkam", 
    "Mylapore", "Nanganallur", "Navallur", "Nungambakkam", "Pamal", 
    "Perambur", "Perumbakkam", "Poonamallee", "Porur", "Saidapet", 
    "Sholinganallur", "T. Nagar", "Tambaram", "Thalambur", "Thiruvanmiyur", 
    "Thuraipakkam", "Tiruporur", "Vavin", "Velachery", "Villivakkam", 
    "Virugambakkam"
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

    # Initialize or load trips for the date
    if "trips" not in session:
        session["trips"] = []
        session["trip_date"] = ""
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_trip":
            # Add single trip to session
            new_trip = {
                "time": request.form.get("trip_time"),
                "location": request.form.get("location"),
                "trip_type": request.form.get("trip_type"),
                "passengers": request.form.get("passengers"),
                "escort": request.form.get("escort")
            }
            session["trips"].append(new_trip)
            session["trip_date"] = request.form.get("trip_date")
            session.modified = True
            return render_template("trip_form.html", 
                                 trips=session["trips"],
                                 trip_date=session["trip_date"],
                                 locations=CHENNAI_LOCATIONS, 
                                 trip_types=TRIP_TYPES,
                                 passenger_counts=PASSENGER_COUNTS, 
                                 escort_options=ESCORT_OPTIONS, 
                                 time_options=TIME_OPTIONS,
                                 username=session["username"])
        
        elif action == "submit_all":
            # Submit all trips for the date to Google Sheets
            trip_date = session["trip_date"]
            success_count = 0
            
            for trip in session["trips"]:
                data = {
                    "username": session["username"],
                    "date": trip_date,
                    "time": trip.trip["time"],
                    "location": trip["location"],
                    "tripType": trip["trip_type"],
                    "passengers": trip["passengers"],
                    "escort": trip["escort"]
                }
                
                try:
                    response = requests.post(GOOGLE_WEBHOOK, json=data, timeout=10)
                    if response.status_code == 200:
                        success_count += 1
                except:
                    pass
            
            # Clear session
            session["trips"] = []
            session["trip_date"] = ""
            session.modified = True
            
            return render_template("success.html", 
                                 submitted_count=len(session["trips"]),
                                 success_count=success_count,
                                 trip_date=trip_date)
    
    return render_template("trip_form.html", 
                         trips=session["trips"],
                         trip_date=session["trip_date"],
                         locations=CHENNAI_LOCATIONS, 
                         trip_types=TRIP_TYPES,
                         passenger_counts=PASSENGER_COUNTS, 
                         escort_options=ESCORT_OPTIONS, 
                         time_options=TIME_OPTIONS,
                         username=session["username"])

@app.route("/clear_trips")
def clear_trips():
    session["trips"] = []
    session["trip_date"] = ""
    session.modified = True
    return redirect(url_for("trip_form"))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
