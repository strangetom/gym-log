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
        name=w.get_workout_name_from_slug(slug),
        slug=slug,
        colour=w.get_workout_colour_from_slug(slug),
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
        name=w.get_exercise_name_from_id(exerciseID),
        type=w.get_exercise_type_from_id(exerciseID),
        exerciseID=exerciseID,
    )


@app.route("/edit-workout/<string:slug>")
def edit_workout(slug: str):
    """Page for editing workout name and exercise list.

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
    all_exercises = w.list_all_exercises()
    workout_exercises = [ex["name"] for ex in w.list_workout_exercises(slug)]

    return render_template(
        "edit_workout.html",
        name=w.get_workout_name_from_slug(slug),
        all_exercises=all_exercises,
        workout_exercises=workout_exercises,
        workoutID=w.get_workout_id_from_slug(slug),
    )


@app.route("/save-set", methods=["POST", "DELETE", "PUT"])
def save_set():
    """Save set.
    If the method is POST, create new set.
    If the method is DELETE, delete indicated set
    If the method is PUT, update indicated set.

    Returns
    -------
    Response
        Response object
    """
    w = get_workout_data()
    if request.method == "POST":
        post_data = request.form
        set_data = json.loads(post_data["set"])

        w.save_set(set_data)
        exerciseID = set_data["exerciseID"]

        return Response(status=200)

    elif request.method == "DELETE":
        post_data = request.form
        set_data = json.loads(post_data)
        w.delete_set(int(post_data["setID"]))
        return Response(status=200)

    elif request.method == "PUT":
        post_data = request.form
        print(post_data)
        w.update_set(int(post_data["setID"]), post_data)
        return Response(status=200)


@app.route("/save-workout", methods=["POST"])
def save_workout():
    """Save modifications to workout

    Returns
    -------
    Response
        Redirection to workout page for modified workout
    """
    if request.method == "POST":
        post_data = request.form
        workout_data = json.loads(post_data["workout"])
        workoutID = workout_data["workoutID"]

        w = get_workout_data()
        w.save_workout(workout_data)

        return redirect(url_for("workout", slug=w.get_workout_slug_from_id(workoutID)))


@app.route("/new-exercise", methods=["POST"])
def new_exercise():
    """Create new exercise

    Returns
    -------
    Response
        Response object
    """
    if request.method == "POST":
        post_data = request.form

        w = get_workout_data()
        w.new_exercise(post_data["name"], post_data["type"])

        return Response(status=200)
