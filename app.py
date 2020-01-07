from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
from flask import Flask, jsonify
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')

# Python SQL toolkit and Object Relational Mapper
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(bind=engine)

# SETUP FLASK AND ROUTES

app = Flask(__name__)


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"<header><h1>Welcome to my Climate API!<h1/></header><br/>"
        f"<ul><h1>Available Routes:</h1><br/>"
        f"<br/>"
        f"<font size=3><li>/api/v1.0/precipitation</li></font><br/>"
        f"<font size=2>Returns a list of dictionaries by dates and precipitation values for 08/2016 to 08/2017</font><br/>"
        f"<br/>"
        f"<font size=3><li>/api/v1.0/stations</li></font><br/>"
        f"<font size=2>Returns a list of weather stations in Hawaii.</font><br/>"
        f"<br/>"
        f"<font size=3><li>/api/v1.0/tobs</li></font><br/>"
        f"<font size=2>Returns a list of dictionaries by date and temperature readings for 08/2016 to 08/2017.</font><br/>"
        f"<br/>"
        f"<font size=3><li>/api/v1.0/<date></li></font><br/>"
        f"<font size=2>Input date (/YYYY-MM-DD) to return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.</font><br/>"
        f"<br/>"
        f"<font size=3><li>/api/v1.0/<start>/<end> </li></font><br/>"
        f"<font size=2>Input start date and end date (in /YYYY-MM-DD/YYYY-MM-DD format) to return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given  date range.</font></ul>"
    )

# Create FLASK route for precipitation analysis


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
# query for the dates and precipitation for the last year(2017)
    prcp2017 = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date.between("2016-08-23", "2017-08-23")).\
        group_by(Measurement.date).all()


# Create a dictionary from the row data and append to a list of prcp_2017
    prcp_2017 = []
    
    for date, prcp in prcp2017:
        HI_prcp = {}
        HI_prcp[date] = prcp
        #HI_prcp["precipitation"] = prcp
        prcp_2017.append(HI_prcp)

    return jsonify(prcp_2017)


@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    stations = session.query(Station.name).all()
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")
    tobs2017 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

# Create a dictionary from the row data and append to a list of prcp_2017
    tobs_2017 = []
    
    for date, tobs in tobs2017:
        HI_tobs = {}
        HI_tobs[date] = tobs
        #HI_prcp["precipitation"] = prcp
        tobs_2017.append(HI_tobs)

    return jsonify(tobs_2017)

@app.route("/api/v1.0/<date>/")
def given_date(date):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date == date).all()

# creates JSONified list of dictionaries
    date_list = []
    for result in results:
        temp = {}
        temp['Date'] = date
        temp['Lowest Temperature'] = result[0]
        temp['Average Temperature'] = result[1]
        temp['Highest Temperature'] = result[2]
        date_list.append(temp)

    return jsonify(date_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def start_end(start_date, end_date):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # creates JSONified list of dictionaries
    dates_list = []
    for result in results:
        range = {}
        range["Start Date"] = start_date
        range["End Date"] = end_date
        range["Lowest Temperature"] = result[0]
        range["Average Temperature"] = result[1]
        range["Highest Temperature"] = result[2]
        dates_list.append(range)
    return jsonify(dates_list)


if __name__ == "__main__":
    app.run(debug=True)
