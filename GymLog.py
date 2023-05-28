#!/usr/bin/env python3

import json

from flask import Flask, Response, g, render_template, request, redirect, url_for

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


@app.route("/edit-workout/<int:workoutID>")
def edit_workout(workoutID: int):
    """Page for editing workout name and exercise list.

    Parameters
    ----------
    workoutID : int
        Workout ID

    Returns
    -------
    str
        Rendered HTML template
    """
    w = get_workout_data()
    all_exercises = w.list_all_exercises()
    workout_exercises = [ex["name"] for ex in w.list_workout_exercises(workoutID)]

    return render_template(
        "edit_workout.html",
        name=w.get_workout_name(workoutID),
        all_exercises=all_exercises,
        workout_exercises=workout_exercises,
        workoutID=workoutID,
    )


@app.route("/workout/", methods=["POST"], defaults={"workoutID": None})
@app.route("/workout/<int:workoutID>", methods=["GET", "DELETE", "PUT"])
def workout_endpoint(workoutID: int):
    """Workout endpoint
    If the method is GET, return workout page.
    If the method is POST, create new workout.
    If the method is PUT, update indicated workout.
    If the method is DELETE, delete indicated workout.

    Returns
    -------
    Response
        Redirection to workout page for modified workout

    Parameters
    ----------
    workoutID : int
        Workout ID
    """
    w = get_workout_data()
    if request.method == "GET":
        return render_template(
            "workout.html",
            exercises=w.list_workout_exercises(workoutID),
            name=w.get_workout_name(workoutID),
            workoutID=workoutID,
            colour=w.get_workout_colour(workoutID),
        )

    elif request.method == "POST":
        post_data = request.form
        w.new_workout(post_data["name"], post_data["colour"])
        return Response(status=200)

    elif request.method == "PUT":
        post_data = request.form
        workout_data = json.loads(post_data["workout"])
        w.save_workout(workoutID, workout_data)
        return Response(status=200)

    elif request.method == "DELETE":
        w.delete_workout(workoutID)
        return Response(status=200)


@app.route("/exercise/", methods=["POST"], defaults={"exerciseID": None})
@app.route("/exercise/<int:exerciseID>", methods=["GET", "DELETE"])
def exercise_endpoint(exerciseID: int):
    """Exercise endpoint.
    If the method is GET, return exercise page.
    If the method is POST, create new exercise.
    If the method is DELETE, delete indicated exercise.

    Returns
    -------
    Response
        Response object

    Parameters
    ----------
    exerciseID : int
        Exercise ID
    """
    w = get_workout_data()
    if request.method == "GET":
        # Get workout ID for parent workout from query string
        # /exercise/1?workoutID=1
        workoutID = request.args.get("workoutID")

        return render_template(
            "exercise.html",
            sets=w.list_exercise_sets(exerciseID),
            name=w.get_exercise_name(exerciseID),
            type=w.get_exercise_type(exerciseID),
            graph=w.get_exercise_history(exerciseID),
            exerciseID=exerciseID,
            workoutID=workoutID,
            workoutColour=w.get_workout_colour(workoutID),
        )

    elif request.method == "POST":
        post_data = request.form
        w.new_exercise(post_data["name"], post_data["type"])
        return Response(status=200)

    elif request.method == "DELETE":
        w.delete_exercise(exerciseID)
        return Response(status=200)


@app.route("/set/", methods=["POST"], defaults={"setID": None})
@app.route("/set/<int:setID>", methods=["DELETE", "PUT"])
def set_endpoint(setID: int):
    """Exercise set endpoint.
    If the method is POST, create new set.
    If the method is PUT, update indicated set.
    If the method is DELETE, delete indicated set.

    Returns
    -------
    Response
        Response object

    Parameters
    ----------
    setID : int
        Set ID
    """
    w = get_workout_data()
    if request.method == "POST":
        post_data = request.form
        w.save_set(post_data)
        return redirect(
            url_for(
                "exercise_endpoint",
                exerciseID=post_data["exerciseID"],
                workoutID=post_data["workoutID"],
            )
        )

    elif request.method == "DELETE":
        w.delete_set(setID)
        return Response(status=200)

    elif request.method == "PUT":
        post_data = request.form
        w.update_set(setID, post_data)
        return Response(status=200)
