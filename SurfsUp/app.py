from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Set up the database and create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Create a Flask app
app = Flask(__name__)

# Define routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    query_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for precipitation data
    prcp_results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= query_date)\
        .all()
    
    # Create a dictionary of date and prcp values
    prcp_data = {date: prcp for date, prcp in prcp_results}
    
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station, Station.name).all()
    stations_data = [{"Station": station, "Name": name} for station, name in station_results]
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    query_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    tobs_results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date >= query_date)\
        .filter(Measurement.station == 'USC00519281')\
        .all()
    
    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in tobs_results]
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    if end is None:
        end = session.query(func.max(Measurement.date)).scalar()

    temperature_results = session.query(func.min(Measurement.tobs),
                                        func.max(Measurement.tobs),
                                        func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    stats_data = {"Start Date": start,
                  "End Date": end,
                  "Min Temperature": temperature_results[0][0],
                  "Max Temperature": temperature_results[0][1],
                  "Avg Temperature": temperature_results[0][2]}

    return jsonify(stats_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)






    