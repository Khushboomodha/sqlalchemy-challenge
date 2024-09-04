# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station=Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # a query to retrieve the last 12 months of precipitation data

    one_year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation_scores= session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>=one_year_ago_date).all()

    precipitation_df=pd.DataFrame(precipitation_scores, columns=['Date', 'Prcp'])

    precipitation_df = precipitation_df.sort_values('Date')

    precipitation_df.set_index('Date', inplace=True)

    precipitation_dict =precipitation_df.to_dict()

    session.close()


    return jsonify(precipitation_dict)

    


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_list = session.query(Station.station,Station.name).all()

    session.close()

    # Convert list of tuples into a dictionary
    results = {station: name for station, name in station_list}
    return jsonify(stations = results)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

# Query to find the temp of most active stations
    temp_data = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()

    session.close()


    tobs_info = []
    for date,tobs in temp_data:
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_info.append(tobs_dic)

    return jsonify(tobs_info)


@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find the min, avg, and max temperature for the specified start date
    start_date_temp = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    session.close()

    # Extract the result and create a dictionary
    min_temp, avg_temp, max_temp = start_date_temp[0]
    start_date_tobs_dict = {
        "min_temp": min_temp,
        "avg_temp": avg_temp,
        "max_temp": max_temp
    }

    return jsonify(start_date_tobs_dict)



@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find the min, avg, and max temperature between the start and end dates
    start_end_date_temp = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Extract the result and create a dictionary
    min_temp, avg_temp, max_temp = start_end_date_temp[0]
    start_end_date_tobs_dict = {
        "min_temp": min_temp,
        "avg_temp": avg_temp,
        "max_temp": max_temp
    }

    return jsonify(start_end_date_tobs_dict)




if __name__ == "__main__":
    app.run(debug=True)
