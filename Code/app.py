# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
e = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=e)


# Save references to each table

M = Base.classes.measurement

S = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(e)

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
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/<s>/end/<e>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value."""

    end_date = dt.date(2017, 8, 23)
    start_date = end_date - dt.timedelta(days=365)

    prcp_one_yr = session.query(M.date, M.prcp).\
    filter(M.date >= start_date).\
    filter(M.date <= end_date).all()

    prcp_dict = dict(prcp_one_yr)
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    stations_list = []

    stations = session.query(S.station).all()

    for value in stations:
        stations_list.append(value[0])
        
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    """Return a JSON list of temperature observations for the previous year."""

    tobs_list = []
    
    end_date = dt.date(2017, 8, 23)
    start_date = end_date - dt.timedelta(days=365)
    
    tobs_station = session.query(M.date, M.tobs).\
    filter(M.station == 'USC00519281').\
    filter(M.date >= start_date).\
    filter(M.date <= end_date).all()

    for value in tobs_station:
        tobs_data = {"date": value[0], "temperature": value[1]}
        tobs_list.append(tobs_data)
    
    return jsonify(tobs_list)
from datetime import datetime 

@app.route("/api/v1.0/start/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start. """
    """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})
    
    start_q = session.query(
        func.min(M.tobs),
        func.max(M.tobs),
        func.avg(M.tobs)).\
        filter(M.date >= start).all()
    
    start_data = {'Min': start_q[0][0], 'Max': start_q[0][1], 'Average': start_q[0][2]}
    
    return jsonify(start_data)



from datetime import datetime 
        
@app.route("/api/v1.0/start/<s>/end/<e>")
def start_end(s,e):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range. """
    """For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive. """

    try:
        s_date = datetime.strptime(s, "%Y-%m-%d").date()
        e_date = datetime.strptime(e, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

    range_q = session.query(
        func.min(M.tobs),
        func.max(M.tobs),
        func.avg(M.tobs)).\
        filter(M.date >= s_date).\
        filter(M.date <= e_date).all()

    range_data = {'Min': range_q[0][0], 'Max': range_q[0][1], 'Average': range_q[0][2]}
    
    return jsonify(range_data)

session.close()
    
if __name__ == '__main__':
    app.run(debug=True)