import json
import sys

sys.path.append(".")

from flask import (
    Flask,
    Response,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from tools.WorkoutData import WorkoutData

app = Flask(__name__)


def get_workout_data():
    """Get workout data from global object

    Returns
    -------
    data
        WorkoutData instance
    """
    data = getattr(g, "_WorkoutData", None)
    if data is None:
        data = g._WorkoutData = WorkoutData("gym-log.db")
    return data


@app.route("/")
def home():
    """Return homepage

    Returns
    -------
    str
        Rendered HTML template
    """
    W = get_workout_data()
    workouts = W.list_workouts()

    return render_template("homepage.html", workouts=workouts)


@app.route("/workout/<string:slug>")
def workout(slug: str):
    """Return page for workout given by slug

    Parameters
    ----------
    slug : str
        Slug for workout

    Returns
    -------
    str
        Rendered HTML template
    """
    w = get_workout_data()
    return render_template(
        "workout.html", exercises=w.list_exercises(slug), name=w.get_workout_name(slug)
    )


@app.route("/exercise/<int:exerciseID>")
def exercise(exerciseID: int):
    """Return page for exercise given by ID

    Parameters
    ----------
    exerciseID : int
        Exercise ID

    Returns
    -------
    str
        Rendered HTML template
    """
    w = get_workout_data()
    return render_template(
        "exercise.html",
        sets=w.list_sets(exerciseID),
        name=w.get_exercise_name(exerciseID),
        type=w.get_exercise_type(exerciseID),
        exerciseID=exerciseID,
    )


@app.route("/add-set", methods=["POST"])
def add_set():

    if request.method == "POST":
        post_data = request.form
        set_data = json.loads(post_data["set"])

        w = get_workout_data()
        w.save_set(set_data)
        exerciseID = set_data["exerciseID"]

        return redirect(url_for("exercise", exerciseID=exerciseID))
