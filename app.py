from os import stat
from flask import Flask
from flask import json
from flask.json import jsonify
import numpy as np
from numpy.core.defchararray import _startswith_dispatcher
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

database = ("Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{database}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


my_app =  Flask(__name__)


@my_app.route("/")
def home():
     return (
         f"Welome to Climate App API<br/>"
         f"For Percipitation Data use - /api/v1.0/precipitation<br/>"
         f"For list of Stations use - /api/v1.0/stations<br/>"
         f"To find most active station use - /api/v1.0/tobs<br/>"
         f"To find temperature data from a given start date use (use format YYYY-MM-DD) - /api/v1.0/<start><br/>"
         f"To find temperature data from a given range of date use (use format YYYY-MM-DD)- /api/v1.0/<start>/<end><br/>") 


prcp_dict = {}

@my_app.route("/api/v1.0/precipitation")
def percipitation():
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    last_date = last_date.date()
    start_date = last_date - dt.timedelta(days=365)
    selection = [Measurement.date, Measurement.prcp]
    data = session.query(*selection).filter(Measurement.date <= last_date).filter(Measurement.date >= start_date).all()
    
    for row in data:
        prcp_dict[row[0]] = row[1]

    session.close()

    return jsonify (prcp_dict)

@my_app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    names = session.query(Station.station, Station.name).all()
    names_dict = {}
    for row in names:
        names_dict[row[0]] = row[1]
    session.close()

    return jsonify (names_dict)

@my_app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    top_station_id = session.query(Station.name, Measurement.station, func.count(Measurement.prcp))\
                    .group_by(Measurement.station)\
                    .order_by(func.count(Measurement.prcp).desc())\
                    .filter(Measurement.station == Station.station).first()[1]
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).filter(Measurement.station == top_station_id).first()[0]
    final_date = dt.datetime.strptime(final_date, "%Y-%m-%d")
    final_date = final_date.date()
    first_date = final_date - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date <= final_date).filter(Measurement.date >= first_date).all()
    tobs_dict = {}
    for row in data:
        tobs_dict[row[0]] = row[1]

    session.close()

    return jsonify (tobs_dict)  


@my_app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start_date = session.query(func.min(Measurement.date)).first()[0]
    end_date = session.query(func.max(Measurement.date)).first()[0]

    if start >= start_date and start <= end_date:
        min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
        max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
        avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
    
        return (f"Minimum Temperature = {min_temp}</br>"
                f"Maximun Temperature = {max_temp}</br>"
                f"Average Temperature = {avg_temp}</br>") 
    else:
        return jsonify({"error" : f"The date {start} was not found. Please select between {start_date} and {end_date}"})

@my_app.route("/api/v1.0/<start>/<end>")
def startend(start, end):

    session = Session(engine)

    start_date = session.query(func.min(Measurement.date)).first()[0]
    end_date = session.query(func.max(Measurement.date)).first()[0]

    if start >= start_date and end <= end_date:
        min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
        max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
        avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >=start).filter(Measurement.date <=end_date).all()[0]
    
        return (f"Minimum Temperature = {min_temp}</br>"
                f"Maximun Temperature = {max_temp}</br>"
                f"Average Temperature = {avg_temp}</br>") 
    else:
        return jsonify({"error" : f"The date {start} or {end} was not found. Please select between {start_date} and {end_date}"})


if __name__ == "__main__":
    my_app.run(debug=True)
