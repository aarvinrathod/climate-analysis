from flask import Flask

my_app =  Flask(__name__)


@my_app.route("/")
def home():
     return (
         f"Welome to Climate App API<br/>"
         f"For Percipitation Data use - /api/v1.0/precipitation<br/>"
         f"For list of Stations use - /api/v1.0/stations<br/>"
         f"To find most active station use - /api/v1.0/tobs<br/>"
         f"To find temperature data from a given start date use - /api/v1.0/<start><br/>"
         f"To find temperature data from a given range of date use - /api/v1.0/<start>/<end><br/>"
     )



if __name__ == "__main__":
    my_app.run(debug=True)
