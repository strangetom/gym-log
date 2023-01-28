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


@app.route("/service-worker.js", methods=["GET"])
def serviceworker():
    """Make servicer work available at /service-worker.js path instead of from
    within /static path

    Returns
    -------
    Response
        Response object pointing to service-worker.js
    """
    return app.send_static_file("service-worker.js")


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
        "workout.html",
        exercises=w.list_workout_exercises(slug),
        name=w.get_workout_name(slug),
        slug=slug,
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
        sets=w.list_exercise_sets(exerciseID),
        name=w.get_exercise_name(exerciseID),
        type=w.get_exercise_type(exerciseID),
        exerciseID=exerciseID,
    )


@app.route("/edit-workout/<string:slug>")
def edit_workout(slug: str):
    w = get_workout_data()
    all_exercises = w.list_all_exercises()
    workout_exercises = [ex["name"] for ex in w.list_workout_exercises(slug)]

    return render_template(
        "edit_workout.html",
        name=w.get_workout_name(slug),
        all_exercises=all_exercises,
        workout_exercises=workout_exercises,
        workoutID=w.get_workout_id(slug),
    )


@app.route("/save-set", methods=["POST"])
def save_set():

    if request.method == "POST":
        post_data = request.form
        set_data = json.loads(post_data["set"])

        w = get_workout_data()
        w.save_set(set_data)
        exerciseID = set_data["exerciseID"]

        return redirect(url_for("exercise", exerciseID=exerciseID))


@app.route("/save-workout", methods=["POST"])
def save_workout():

    if request.method == "POST":
        post_data = request.form
        workout_data = json.loads(post_data["workout"])

        w = get_workout_data()
        w.save_workout(workout_data)

        slug = w.get_workout_slug(workout_data["workoutID"])
        return redirect(url_for("workout", slug=slug))
