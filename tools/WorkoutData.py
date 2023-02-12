#!/usr/bin/env python3

import datetime
import math
import sqlite3
from dataclasses import dataclass
from itertools import groupby
from typing import Any, Dict, List, Optional, Tuple

from slugify import slugify


@dataclass
class ExerciseSet:
    uid: int
    datetime: str
    distance_m: Optional[float]
    weight_kg: Optional[float]
    time_s: Optional[int]
    repetitions: Optional[int]


class WorkoutData:
    def __init__(self, db):
        self.db = db

    def get_workout_name_from_slug(self, slug: str) -> str:
        """Return workout name from slug

        Parameters
        ----------
        slug : str
            Workout slug

        Returns
        -------
        str
            Workout name
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM workout WHERE slug = ?", (slug,))
            name = cur.fetchone()

        conn.close()
        return name[0]

    def get_workout_id_from_slug(self, slug: str) -> int:
        """Return workout ID from slug

        Parameters
        ----------
        slug : str
            Workout slug

        Returns
        -------
        int
            Workout ID
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT workoutID FROM workout WHERE slug = ?", (slug,))
            workoutID = cur.fetchone()

        conn.close()
        return workoutID[0]

    def get_workout_slug_from_id(self, workoutID: int) -> str:
        """Return workout slug from ID

        Parameters
        ----------
        workoutID : int
            Workout ID

        Returns
        -------
        str
            Workout slug
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT slug FROM workout WHERE workoutID = ?", (workoutID,))
            slug = cur.fetchone()

        conn.close()
        return slug[0]

    def get_workout_colour_from_slug(self, slug: str) -> str:
        """Return hex colour for workout from slug

        Parameters
        ----------
        slug : str
            Workout slug

        Returns
        -------
        str
            Workout colour
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT colour FROM workout WHERE slug = ?", (slug,))
            colour = cur.fetchone()

        conn.close()
        return colour[0]

    def get_exercise_name_from_id(self, exerciseID: int) -> str:
        """Return exercise name from exercise ID

        Parameters
        ----------
        exerciseID : int
            Exercise ID

        Returns
        -------
        str
            Exercise name
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM exercise WHERE exerciseID = ?", (exerciseID,))
            name = cur.fetchone()

        conn.close()
        return name[0]

    def get_exercise_type_from_id(self, exerciseID: int) -> str:
        """Return work name from slug

        Parameters
        ----------
        exerciseID : int
            Exercise ID

        Returns
        -------
        str
            Exercise name
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT type FROM exercise WHERE exerciseID = ?", (exerciseID,))
            type_ = cur.fetchone()

        conn.close()
        return type_[0]

    def list_workouts(self) -> List[Dict[str, Any]]:
        """List all workouts in log

        Returns
        -------
        List[Dict[str, Any]]
            List of dictionaries with the following keys
                name
                exercise_count
                slug
                last_update
                last_exercise
        """
        workout_data = []
        # Get list of workouts
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT workoutID, name, slug, colour FROM workout")
            workout_names = cur.fetchall()

            # For each workout, count number of exercises
            for workoutID, name, slug, colour in workout_names:
                cur.execute(
                    "SELECT COUNT(*) FROM workout_exercise WHERE workoutID = ?",
                    (workoutID,),
                )
                count = cur.fetchone()

                exercise, update = self._get_workout_last_update(workoutID)
                workout_data.append(
                    {
                        "name": name,
                        "exercise_count": count[0],
                        "slug": slug,
                        "colour": colour,
                        "last_update": update,
                        "last_exercise": exercise,
                    }
                )

        conn.close()

        return workout_data

    def list_all_exercises(self) -> List[Dict[str, str]]:
        """Return all exercises in database

        Returns
        -------
        List[Dict[str, str]]
            List of dicts containing name and exercise ID for all exercises
        """
        all_exercises = []
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, exerciseID FROM exercise")
            exercises = cur.fetchall()

            for name, exerciseID in exercises:
                all_exercises.append({"name": name, "exerciseID": exerciseID})

        return sorted(all_exercises, key=lambda x: x["name"])

    def list_workout_exercises_by_id(self, workoutID: int) -> List[Dict[str, str]]:
        """Return exercises for workout given by workoutID

        Parameters
        ----------
        workoutID : int
            workoutID

        Returns
        -------
        List[Dict[str, str]]
            ist of dicts containing name, exerciseID, last update
            and last set details
        """
        slug = self.get_workout_slug_from_id(workoutID)
        return self.list_workout_exercises(slug)

    def list_workout_exercises(self, slug: str) -> List[Dict[str, str]]:
        """Return exercises for workout given by slug

        Parameters
        ----------
        slug : str
            Workout slug

        Returns
        -------
        List[Dict[str, str]]
            List of dicts containing name, exerciseID, last update
            and last set details
        """
        exercise_data = []
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT workoutID from workout WHERE slug = ?", (slug,))
            workoutID = cur.fetchone()[0]

            cur.execute(
                "SELECT exerciseID FROM workout_exercise WHERE workoutID = ?",
                (workoutID,),
            )
            exerciseIDs = cur.fetchall()

            for (exerciseID,) in exerciseIDs:
                cur.execute(
                    "SELECT name, type FROM exercise WHERE exerciseID = ?",
                    (exerciseID,),
                )
                name, exercise_type = cur.fetchone()
                last_update, last_set = self._get_exercise_last_set(exerciseID)

                exercise_data.append(
                    {
                        "name": name,
                        "exerciseID": exerciseID,
                        "last_update": last_update,
                        "last_set": last_set,
                    }
                )

        conn.close()

        # Sort alpabetically by name and return
        return sorted(exercise_data, key=lambda x: x["name"])

    def list_exercise_sets(
        self, exerciseID: int, number: int = 36
    ) -> List[List[Dict[str, Any]]]:
        """Get list of most recent sets limited by <number> for exercise.
        Sets are grouped by date.

        Parameters
        ----------
        exerciseID : int
            Exercise ID
        number : int, optional
            Number of sets to return. Default is 12.

        Returns
        -------
        List[List[Dict[str, Any]]]
            List of dicts containing set timestamp and detail, grouped by date.
        """
        set_data = []
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM sets WHERE exerciseID = ? ORDER BY uid DESC LIMIT ?",
                (exerciseID, number),
            )
            sets = cur.fetchall()

            for info in sets:
                uid, _, timestamp, distance, weight, time, repetitions = info
                current_set = ExerciseSet(
                    uid, timestamp, distance, weight, time, repetitions
                )
                previous_set = self._get_previous_set(exerciseID, uid)

                set_string = self._create_set_summary(current_set)
                delta = self._calculate_set_delta(current_set, previous_set)

                # Convert time (seconds) to hours, minutes and seconds
                if time is not None:
                    hours = math.floor(float(time) / 3600) or None
                    mins = math.floor((float(time) % 3600) / 60) or None
                    seconds = math.floor(float(time) % 60) or None
                else:
                    hours = None
                    mins = None
                    seconds = None

                set_data.append(
                    {
                        "uid": uid,
                        "timestamp": timestamp,
                        "readable_time": self._readable_datetime(timestamp),
                        "set_detail": set_string,
                        "distance": distance,
                        "weight": weight,
                        "hours": hours,
                        "mins": mins,
                        "seconds": seconds,
                        "repetitions": repetitions,
                        "delta": delta,
                    }
                )

        # Group sets by date (i.e. the bit before 'T' in the timestamp)
        grouped_sets = [
            list(group)
            for _, group in groupby(
                set_data, key=lambda x: x["timestamp"].split("T")[0]
            )
        ]

        return grouped_sets

    def save_set(self, set_data: Dict[str, str]) -> None:

        # Replace empty strings in keys with None
        data = {key: None if value == "" else value for key, value in set_data.items()}

        # Insert into database
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO sets (exerciseID, datetime, distance_m, weight_kg, time_s, repetitions) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    data["exerciseID"],
                    data["datetime"],
                    data["distance_m"],
                    data["weight_kg"],
                    data["time_s"],
                    data["repetitions"],
                ),
            )
        conn.close()

    def delete_set(self, uid: int) -> None:
        """Delete set given by set uid

        Parameters
        ----------
        uid : int
            Set unique ID
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM sets WHERE uid = ?", (uid,))
        conn.close()

    def update_set(self, uid: int, data: Dict[str, str]) -> None:
        """Update set with new data.
        The timestamp and uid remain unchanged.

        Parameters
        ----------
        uid : int
            Set unique ID
        data : Dict[str, str]
            Dict containing updated values. Only the values relevant to the
            exercise type are in the dict.
        """
        time_updated = False
        # Iterate through items in dict and update field in table
        for key, value in data.items():
            if key == "setID":
                # Skip set ID
                continue
            elif key in ["hours", "mins", "seconds"]:
                if not time_updated:
                    # Calculate time in seconds
                    seconds = (
                        int(data["hours"] or 0) * 3600
                        + int(data["mins"] or 0) * 60
                        + int(data["seconds"] or 0)
                    )
                    with sqlite3.connect(self.db) as conn:
                        cur = conn.cursor()
                        cur.execute(
                            f"UPDATE sets SET time_s = ?  WHERE uid = ?", (seconds, uid)
                        )
                    conn.close()
                    # Mark time update as done so we don't do it 3 times
                    time_updated = True
            else:
                with sqlite3.connect(self.db) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        f"UPDATE sets SET {key} = ?  WHERE uid = ?", (value, uid)
                    )
                conn.close()

    def save_workout(self, workout_data: Dict[str, Any]) -> None:
        """Save changes to workout

        Parameters
        ----------
        workout_data : Dict[str, Any]
            Dict containing latest workout name and exercise list
        """
        workoutID = workout_data["workoutID"]

        # Update name and slug
        workout_name = workout_data["name"]
        workout_slug = slugify(workout_name)

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE workout SET name = ?, slug = ? WHERE workoutID = ?",
                (workout_name, workout_slug, workoutID),
            )
        conn.close()

        # Get set of current exercise IDs
        current_exercises = self.list_workout_exercises_by_id(workoutID)
        current_exercise_IDs = {ex["exerciseID"] for ex in current_exercises}

        new_exercises = set(workout_data["exerciseIDs"]) - current_exercise_IDs
        deleted_exercises = current_exercise_IDs - set(workout_data["exerciseIDs"])

        for exerciseID in new_exercises:
            with sqlite3.connect(self.db) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO workout_exercise (workoutID, exerciseID) VALUES (?, ?)",
                    (workoutID, exerciseID),
                )
            conn.close()

        for exerciseID in deleted_exercises:
            with sqlite3.connect(self.db) as conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM workout_exercise WHERE (workoutID = ? AND exerciseID = ?)",
                    (workoutID, exerciseID),
                )
            conn.close()

    def new_exercise(self, name: str, exercise_type: str) -> None:
        """Add new exercise to database

        Parameters
        ----------
        name : str
            Name of exercise
        exercise_type : str
            Type of exercise
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO exercise (name, type) VALUES (?, ?)", (name, exercise_type)
            )
        conn.close()

    def delete_exercise(self, exerciseID: int) -> None:
        """Delete exercise given by set exerciseID.
        Delete association between exercise and any workouts.
        Delete any sets associated with exercise.

        Parameters
        ----------
        exerciseID : int
            Exercise ID
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM exercise WHERE exerciseID = ?", (exerciseID,))
            cur.execute(
                "DELETE FROM workout_exercise WHERE exerciseID = ?", (exerciseID,)
            )
            cur.execute("DELETE FROM sets WHERE exerciseID = ?", (exerciseID,))

        conn.close()

    def new_workout(self, name: str, colour: str) -> None:
        """Add new workout to database

        Parameters
        ----------
        name : str
            Name of workout
        colour : str
            Workout colour
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO workout (name, slug, colour) VALUES (?, ?, ?)",
                (name, slugify(name), colour),
            )
        conn.close()

    def delete_workout(self, workoutID: int) -> None:
        """Delete workout given by set workoutID.
        Delete association between workout and exercises.

        Parameters
        ----------
        workoutID : int
            Workout ID
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM workout WHERE workoutID = ?", (workoutID,))
            cur.execute(
                "DELETE FROM workout_exercise WHERE workoutID = ?", (workoutID,)
            )

        conn.close()

    def _get_workout_last_update(self, workoutID: int) -> Tuple[str, str]:
        """Return human readable string for when timestamp of last set
        for exercise in workout.

        Parameters
        ----------
        workoutID : int
            workoutID

        Returns
        -------
        Tuple[str, str]
            Last exercise
            Human readable relative datetime string
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(datetime), exerciseID FROM sets WHERE exerciseID in (SELECT exerciseID FROM workout_exercise WHERE workoutID = ?)",
                (workoutID,),
            )
            timestamp, exerciseID = cur.fetchone()

        conn.close()

        if timestamp is None:
            return "", "Never"
        else:
            return self.get_exercise_name_from_id(exerciseID), self._readable_datetime(
                timestamp
            )

    def _get_previous_set(self, exerciseID: int, uid: int):
        """Return last set for exercise given by exerciseID prior to set given by uid

        Parameters
        ----------
        exerciseID : int
            exerciseID
        uid : int
            uid of set to find previous set for
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(uid), * FROM sets WHERE exerciseID = ? and uid < ?",
                (exerciseID, uid),
            )
            (
                prev_uid,
                _,
                _,
                timestamp,
                distance,
                weight,
                time,
                repetitions,
            ) = cur.fetchone()

        conn.close()

        return ExerciseSet(prev_uid, timestamp, distance, weight, time, repetitions)

    def _get_exercise_last_set(self, exerciseID: int) -> Tuple[str, str]:
        """Return human readable string for when timestamp of last set
        for exercise.

        Parameters
        ----------
        exerciseID : int
            exerciseID

        Returns
        -------
        Tuple[str, str]
            Human readable relative timestamp
            Last set string
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(datetime), * FROM sets WHERE exerciseID = ?",
                (exerciseID,),
            )
            timestamp, _, _, _, distance, weight, time, repetitions = cur.fetchone()

            if repetitions is not None and weight is not None:
                set_string = f"{repetitions} x {weight} kg"
            elif distance is not None and time is not None:
                time_string = str(datetime.timedelta(seconds=int(time)))[2:]
                set_string = f"{int(distance)} m - {time_string}"
            elif time is not None:
                set_string = f"{time} s"
            else:
                set_string = ""

        conn.close()

        if timestamp is None:
            return "Never", set_string
        else:
            return self._readable_datetime(timestamp), set_string

    def _readable_datetime(self, timestamp: str) -> str:
        """Convert an ISO8601 timestamp into a human readable relative string

        Parameters
        ----------
        timestamp : str
            ISO8601 timestamp

        Returns
        -------
        str
            Human readable relative string
        """
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

        delta = datetime.datetime.now() - dt
        delta_seconds = int(delta.total_seconds())

        if dt.date() == datetime.date.today():
            if delta_seconds < 60:
                return "Just now"
            elif delta_seconds < 3600:
                mins = int(delta_seconds / 60)
                unit = "mins" if mins > 1 else "min"
                return f"{mins} {unit} ago"
            elif delta_seconds < 3600 * 12:
                hours = int(delta_seconds / 60 / 60)
                unit = "hours" if hours > 1 else "hour"
                return f"{hours} {unit} ago"
            else:
                return "Earlier today"
        else:
            if delta_seconds < 3600 * 24 * 2:
                return "Yesterday"
            elif delta_seconds < 3600 * 24 * 7:
                days = int(delta_seconds / (3600 * 24))
                return f"{days} days ago"
            else:
                return dt.strftime("%b %d %Y")

    def _create_set_summary(self, details: ExerciseSet) -> str:
        """Generate string that summarises a set
        For example:
        10 x 39.0 kg for weight-repetition exercises
        2000 m - 17:00 for distance-time exercises
        45 s for time exercises

        Parameters
        ----------
        details : ExerciseSet
            ExerciseSet dataclass containing details of set.

        Returns
        -------
        str
            String summarising set
        """
        if details.repetitions is not None and details.weight_kg is not None:
            set_string = f"{details.repetitions} x {details.weight_kg} kg"

        elif details.distance_m is not None and details.time_s is not None:
            time_string = str(datetime.timedelta(seconds=int(details.time_s)))[2:]
            set_string = f"{int(details.distance_m)} m - {time_string}"

        elif details.time_s is not None:
            set_string = f"{details.time_s} s"
        else:
            set_string = ""

        return set_string

    def _calculate_set_delta(
        self, current_set: ExerciseSet, previous_set: ExerciseSet
    ) -> Optional[float]:
        """Calculate the percentage change from previous set.
        If the exercise type is weight-repetitions, the delta is calculated
        from the weight (repetitions ignored)
        If the exercise type is distance-time, the delta is calculated from
        the change in rate (i.e. distance/time)
        If the exercise type is time, the delta is calculated from the change
        is time.

        Parameters
        ----------
        current_set : ExerciseSet
            Current set details
        previous_set : ExerciseSet
            Previous set details

        Returns
        -------
        Optional[float]
            Percentage change is non-zero, else None
        """
        change_from_previous = 0

        if current_set.weight_kg is not None and previous_set.weight_kg is not None:
            if previous_set.weight_kg != 0:
                change_from_previous = (
                    (current_set.weight_kg - previous_set.weight_kg)
                    / previous_set.weight_kg
                    * 100
                )

        elif (
            current_set.distance_m is not None
            and current_set.time_s is not None
            and previous_set.distance_m is not None
            and previous_set.time_s is not None
        ):
            rate = current_set.distance_m / current_set.time_s
            previous_rate = previous_set.distance_m / previous_set.time_s
            if previous_rate != 0:
                change_from_previous = (rate - previous_rate) / previous_rate * 100

        elif current_set.time_s is not None and previous_set.time_s is not None:
            if previous_set.time_s != 0:
                change_from_previous = (
                    (current_set.time_s - previous_set.time_s)
                    / previous_set.time_s
                    * 100
                )
        else:
            set_string = ""

        # Convert change from previous set to sensible string
        if change_from_previous == 0:
            delta = None
        else:
            delta = change_from_previous

        return delta
