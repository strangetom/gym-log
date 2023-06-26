#!/usr/bin/env python3

from flask import Flask, Response

app = Flask(__name__)

import gymlog.views  # noqa: E402, F401
from gymlog.models import (  # noqa: E402
    database,
    Exercise,
    Workout,
    Sets,
    WorkoutExercise,
)

# Initialise the databse, only if the tables don't already exist
database.create_tables([Exercise, Workout, Sets, WorkoutExercise], safe=True)
database.close()


@app.before_request
def before_request():
    """Connect to database before processing each request"""
    database.connect()


@app.after_request
def after_request(response: Response) -> Response:
    """Close database connection after processing each request

    Parameters
    ----------
    response : Response
        Request Response object

    Returns
    -------
    Response
        Request Response object
    """
    database.close()
    return response


__version__ = "0.1.0"
