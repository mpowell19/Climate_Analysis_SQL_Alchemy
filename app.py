import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import pandas as pd

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#################################################
#Create a query for percipitation from the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    trailing_year= session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()
#Convert the query results to a Dictionary using date as the key and prcp as the value.
    Total_rain=[]
    for results in trailing_year:
        row ={}
        row["date"]=trailing_year[0]
        row["prcp"]=trailing_year[1]
        Total_rain.append(row)
    
    return jsonify(Total_rain)
#################################################
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    active_stations = session.query(Station.name, Station.station)
    stations = pd.read_sql(active_stations.statement, active_stations.session.bind)
    return jsonify(stations.to_dict())



#################################################
#Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    Temps= session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > last_year).\
    order_by(Measurement.date).all()
# Return a JSON list of Temperature Observations (tobs) for the previous year.
    totals_temp = []
    for result in Temps:
        row = {}
        row["date"] = Temps[0]
        row["tobs"] = Temps[1]
        totals_temp.append(row)

    return jsonify(totals_temp)

#################################################
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
#calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def trip_start_date(start):

 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.date(2017,7,8)
    calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    trip = list(np.ravel(calc))
    return jsonify(trip)
#################################################
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
#calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/<start>/<end>")
def all_dates(start, end):

 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start= dt.date(2017, 7, 8)
    end =  dt.date(2017, 7, 16)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)
           
          
if __name__ == "__main__":
    app.run(debug=True)