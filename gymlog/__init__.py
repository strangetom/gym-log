#!/usr/bin/env python3

import os

from flask import Flask, Response
from flask_oidc import OpenIDConnect

app = Flask(__name__)
app.secret_key = "BapYtZ55gdyUb7gyVwLkaMd7qzzaTCswTFDLFJrCU0I="
app.config["OIDC_CLIENT_SECRETS"] = {
    "web": {
        "client_id": os.getenv("OIDC_CLIENT_ID"),
        "client_secret": os.getenv("OIDC_CLIENT_SECRET"),
        "auth_uri": os.getenv("OIDC_AUTH_URI"),
        "userinfo_uri": f"{os.getenv('OIDC_AUTH_URI')}/api/oidc/userinfo",
        "issuer": os.getenv("OIDC_ISSUER"),
        "redirect_uris": [os.getenv("OIDC_REDIRECT_URI")],
    }
}
app.config["OIDC_OVERWRITE_REDIRECT_URI"] = os.getenv("OIDC_OVERWRITE_REDIRECT_URI")
app.config["OIDC_SCOPES"] = "openid email profile"
oidc = OpenIDConnect(app)

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


@app.template_filter("slugify")
def slugify(text: str) -> str:
    """Simple slugification of text e.g. "Upper Body" -> "upper-body"

    Parameters
    ----------
    text : str
        Text to slugify

    Returns
    -------
    str
        Slugified text
    """
    return "-".join([word.lower() for word in text.split()]).replace("&", "")


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
