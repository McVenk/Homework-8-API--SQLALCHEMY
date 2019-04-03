import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new modelS
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
# Flask Routes- Welcome Page
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    print("Server received request for 'Welcome' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#################################################
# Flask Routes- Precipitation
#################################################


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data"""
    print("Server received request for 'precipitation data' page...")
    
    # Compute the latest date in our dataset
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Generate dates in YYYY-MM-DD format
    latest_date=datetime.strptime(latest_date[0],'%Y-%m-%d').date()
    
    # Calculate the date 1 year ago from the last data point in the database
    year_ago_date=latest_date.replace(year=latest_date.year-1)
    # Defining latest & year ago dates
    #latest_date= '2017-08-23'
    #year_ago_date= '2016-08-23'
    # Perform a query to retrieve the data and precipitation scores
    prcp_data_results= session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=year_ago_date).filter(Measurement.date<=latest_date).all()

    # Create a dictionary from the row data and append to a list of prcp_data
    prcp_data = []
    for date,prcp in prcp_data_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)
    
    # Formating prcp_data into a json file
    return jsonify(prcp_data)


#################################################
# Flask Routes- Stations
#################################################


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of station data"""
    print("Server received request for 'Stations data' page...")
    
    # Perform a query to retrieve station
    station_results= session.query(Station.name).all()

    #Convert list of tuples into normal list
    stations=list(np.ravel(station_results))

    # Formating stations data into a json file
    return jsonify(stations)



#################################################
# Flask Routes- Temperature
#################################################


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature data"""
    print("Server received request for 'temperature data' page...")
    
    # Compute the latest date in our dataset
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Generate dates in YYYY-MM-DD format
    latest_date=datetime.strptime(latest_date[0],'%Y-%m-%d').date()
    
    # Calculate the date 1 year ago from the last data point in the database
    year_ago_date=latest_date.replace(year=latest_date.year-1)
    
    # Perform a query to retrieve the date and temperature
    temp_data_results= session.query(Measurement.date,func.count(Measurement.tobs)).filter(Measurement.date>=year_ago_date).filter(Measurement.date<=latest_date).group_by(Measurement.date).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of temp_data
    temp_data = []
    for date,tobs in temp_data_results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature observations"] = tobs
        temp_data.append(temp_dict)
    
    # Formating prcp_data into a json file
    return jsonify(temp_data)


#################################################
# Flask Routes- <start>
#################################################


@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    """TMIN, TAVG, and TMAX for a given start date.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    # Converting start date variable in YYYY-MM-DD format 
    start_date= datetime.strptime(start,'%Y-%m-%d').date()
        
    # Determining the earliest and latest dates of the dataset and convert them in YYYY-MM-DD format 
    earliest_date_ds=session.query(Measurement.date).order_by(Measurement.date.asc()).first()
    latest_date_ds=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    earliest_date_ds= datetime.strptime(earliest_date_ds[0],'%Y-%m-%d').date()
    latest_date_ds= datetime.strptime(latest_date_ds[0],'%Y-%m-%d').date()
    # Checking if its a valid start date between earliest and latest dates of dataset
    if earliest_date_ds<=start_date<=latest_date_ds:
        # Quering all the temp data for given start date and end date
        temp_start_results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

        # Create a dictionary from the row data and append to a list of temp_data_start_date
        temp_data_start_date = []
        for TMIN, TAVG, TMAX in temp_start_results:
            temp_start_date_dict = {}
            temp_start_date_dict["TMIN"] = TMIN
            temp_start_date_dict["TAVG"] = TAVG
            temp_start_date_dict["TMAX"] = TMAX
            temp_data_start_date.append(temp_start_date_dict)
     
        # Formating temp_data_start_date into a json file
        return jsonify(temp_data_start_date)
    else:
        return (f"Please enter a start date between {earliest_date_ds} and {latest_date_ds}")

#################################################
# Flask Routes- <start><end>
#################################################


@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start,end):
    """TMIN, TAVG, and TMAX for a given start date.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    # Converting start date and end date variables in YYYY-MM-DD format 
    start_date_variable= datetime.strptime(start,'%Y-%m-%d').date()
    end_date_variable= datetime.strptime(end,'%Y-%m-%d').date()

    # Determining the earliest and latest dates of the dataset and convert them in YYYY-MM-DD format 
    earliest_date_dataset=session.query(Measurement.date).order_by(Measurement.date.asc()).first()
    latest_date_dataset=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    earliest_date_dataset= datetime.strptime(earliest_date_dataset[0],'%Y-%m-%d').date()
    latest_date_dataset= datetime.strptime(latest_date_dataset[0],'%Y-%m-%d').date()

    # Checking for valid start date and end date are within the earliest and latest dates of dataset
    if (earliest_date_dataset <= start_date_variable <= latest_date_dataset) and ((earliest_date_dataset <= end_date_variable <= latest_date_dataset)):
        if start_date_variable <= end_date_variable:
            # Quering all the temp data for given start date and end date
            temp_start_end_results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date_variable).filter(Measurement.date <=end_date_variable).all()

            # Create a dictionary from the row data and append to a list of temp_data_start_date
            temp_data_start_end_date = []
            for TMIN, TAVG, TMAX in temp_start_end_results:
                temp_start_end_date_dict = {}
                temp_start_end_date_dict["TMIN"] = TMIN
                temp_start_end_date_dict["TAVG"] = TAVG
                temp_start_end_date_dict["TMAX"] = TMAX
                temp_data_start_end_date.append(temp_start_end_date_dict)
            
            # Formating temp_data_start_date into a json file
            return jsonify(temp_data_start_end_date)
        else:
            return (f"The start date {start_date_variable} is after end date {end_date_variable}. Please revise the start and end dates. Your dates must be between {earliest_date_dataset} and {latest_date_dataset} in YYYY-MM-DD Format")
    else:
        return (f"No temperature observations available for requested dates. Please enter dates between {earliest_date_dataset} and {latest_date_dataset} in YYYY-MM-DD Format")

if __name__ == '__main__':
    app.run(debug=True)