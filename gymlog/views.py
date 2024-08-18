#!/usr/bin/env python3

import json

from flask import Response, render_template, request

from gymlog import app
from gymlog.interfaces import WorkoutInterface

W = WorkoutInterface()


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
    workouts = W.list_workouts()
    return render_template("homepage.html.jinja", workouts=workouts)


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
    all_exercises = W.list_all_exercises()
    workout_exercises = [ex["name"] for ex in W.list_workout_exercises(workoutID)]

    return render_template(
        "edit_workout.html.jinja",
        name=W.get_workout_name(workoutID),
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
    if request.method == "GET":
        return render_template(
            "workout.html.jinja",
            exercises=W.list_workout_exercises(workoutID),
            name=W.get_workout_name(workoutID),
            workoutID=workoutID,
            colour=W.get_workout_colour(workoutID),
        )

    elif request.method == "POST":
        post_data = request.form
        W.new_workout(post_data["name"], post_data["colour"])
        return Response(status=200)

    elif request.method == "PUT":
        post_data = request.form
        workout_data = json.loads(post_data["workout"])
        W.save_workout(workoutID, workout_data)
        return Response(status=200)

    elif request.method == "DELETE":
        W.delete_workout(workoutID)
        return Response(status=200)


@app.route("/exercise/", methods=["POST"], defaults={"exerciseID": None})
@app.route("/exercise/<int:exerciseID>", methods=["GET", "DELETE"])
@app.route("/exercise/<int:exerciseID>", methods=["PATCH"])
def exercise_endpoint(exerciseID: int):
    """Exercise endpoint.
    If the method is GET, return exercise page.
    If the method is POST, create new exercise.
    If the method is DELETE, delete indicated exercise.
    If the method is PATCH, update the exercise notes

    Returns
    -------
    Response
        Response object

    Parameters
    ----------
    exerciseID : int
        Exercise ID
    """
    if request.method == "GET":
        # Get workout ID for parent workout from query string
        # /exercise/1?workoutID=1
        workoutID = request.args.get("workoutID")

        graph_data = W.get_exercise_history(exerciseID)
        # Extract the lastest entry to display on y axis, if there is graph data
        if len(graph_data) == 0:
            graph_label = ""
        else:
            graph_label = list(graph_data.values())[0][0]

        return render_template(
            "exercise.html.jinja",
            sets=W.list_todays_exercise_sets(exerciseID),
            last_set=W.get_exercise_last_set(exerciseID),
            stats=W.get_exercise_stats(exerciseID),
            name=W.get_exercise_name(exerciseID),
            type=W.get_exercise_type(exerciseID),
            notes=W.get_exercise_notes(exerciseID),
            graph=graph_data,
            graph_label=graph_label,
            exerciseID=exerciseID,
            workoutID=workoutID,
            workoutColour=W.get_workout_colour(workoutID),
        )

    elif request.method == "POST":
        post_data = request.form
        W.new_exercise(post_data["name"], post_data["type"])
        return Response(status=200)

    elif request.method == "DELETE":
        W.delete_exercise(exerciseID)
        return Response(status=200)

    elif request.method == "PATCH":
        patch_data = request.form
        W.update_exercise_notes(exerciseID, patch_data["notes"])
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
    if request.method == "POST":
        post_data = request.form
        W.save_set(post_data)
        return Response(status=200)

    elif request.method == "DELETE":
        W.delete_set(setID)
        return Response(status=200)

    elif request.method == "PUT":
        post_data = request.form
        W.update_set(setID, post_data)
        return Response(status=200)


@app.route("/sync", methods=["POST"])
def sync_sets():
    """Sync sets cached when offline to database.

    Sets are only added to database there is no other set with the same UUID
    in the database.

    Returns
    -------
    Response
        Response object
    """
    if request.method == "POST":
        post_data = request.form
        offline_sets = json.loads(post_data["offline_sets"])
        W.sync_sets(offline_sets)
        return Response(status=200)
