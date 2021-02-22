from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (f'Welcome to the SQLAlchemy Challenge! Presented by Tom Babjak<br/>'
            f'<br>'
            f'Available Routes:<br/>'
            f'/api/v1.0/precipitation<br/>'
            f'/api/v1.0/stations<br/>'
            f'/api/v1.0/tobs<br>'
            f'/api/v1.0/start<br/>'
            f'/api/v1.0/start/end<br>'
            f'<br>'
            f'HINT: Use YYYY-MM-DD format when entering dates in routes :D')

# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list
    all_dates = []
    for date, prcp in results:
        date_dict = {}
        date_dict[date] = prcp
        all_dates.append(date_dict)
        
    # Return the JSON representation of your dictionary.
    return jsonify(all_dates)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stns():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    TOBS = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').\
    filter(Measurement.station == 'USC00519281').all()
    session.close()
    
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    all_tobs = list(np.ravel(TOBS))
    return jsonify(all_tobs)
  
# Return a JSON list of the TMIN, TAVG, and TMAX for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)
    
    sel = [func.max(Measurement.tobs),
           func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           Station.station,
           Measurement.date]
    
    calcs = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= '2017-08-23').\
        filter(Station.station == 'USC00519281').all()
    
    session.close()
    
    all_calcs = []
        
    for record in calcs:
        (mmax, mmin, mavg, station, date) = record
        calc_dict = {}
        calc_dict["TMAX"] = f'{mmax}F'
        calc_dict["TMIN"] = f'{mmin}F'
        calc_dict["TAVG"] = f'{round(mavg,2)}F'
        calc_dict["Start Date"] = start
        calc_dict["End Date"] = '2017-08-23'
        all_calcs.append(calc_dict)
        
        return jsonify(all_calcs)
    
# Return a JSON list of the TMIN, TAVG, and TMAX for a given start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def enddate(start, end):
    session = Session(engine)
    
    sel = [func.max(Measurement.tobs),
           func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           Station.station,
           Measurement.date]
    
    calcs = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        filter(Station.station == 'USC00519281').all()
    
    session.close()
    
    all_calcs = []
        
    for record in calcs:
        (mmax, mmin, mavg, station, date) = record
        calc_dict = {}
        calc_dict["TMAX"] = f'{mmax}F'
        calc_dict["TMIN"] = f'{mmin}F'
        calc_dict["TAVG"] = f'{round(mavg,2)}F'
        calc_dict["Start Date"] = start
        calc_dict["End Date"] = end
        all_calcs.append(calc_dict)
        
        return jsonify(all_calcs)

if __name__ == "__main__":
    app.run(debug=True)
