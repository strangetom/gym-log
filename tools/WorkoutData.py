#!/usr/bin/env python3

import datetime
import sqlite3
from itertools import groupby
from typing import Any, Dict, List, Tuple

from slugify import slugify


class WorkoutData:
    def __init__(self, db):
        self.db = db

    def get_workout_name(self, slug: str) -> str:
        """Return work name from slug

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

    def get_exercise_name(self, exerciseID: int) -> str:
        """Return work name from slug

        Parameters
        ----------
        exerciseID : ing
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
        """
        workout_data = []
        # Get list of workouts
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT workoutID, name, slug FROM workout")
            workout_names = cur.fetchall()

            # For each workout, count number of exercises
            for workoutID, name, slug in workout_names:
                cur.execute(
                    "SELECT COUNT(*) FROM workout_exercise WHERE workoutID = ?",
                    (workoutID,),
                )
                count = cur.fetchone()

                workout_data.append(
                    {
                        "name": name,
                        "exercise_count": count[0],
                        "slug": slug,
                        "last_update": self._get_workout_last_update(workoutID),
                    }
                )

        conn.close()

        return workout_data

    def list_exercises(self, slug: str) -> List[Dict[str, Any]]:

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

    def list_sets(
        self, exerciseID: int, number: int = 12
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
                "SELECT * FROM sets WHERE exerciseID = ? ORDER BY datetime DESC LIMIT ?",
                (exerciseID, number),
            )
            sets = cur.fetchall()

            for info in sets:
                _, _, timestamp, distance, weight, time, repetitions = info

                if repetitions is not None and weight is not None:
                    set_string = f"{repetitions} x {weight} kg"
                elif distance is not None and time is not None:
                    time_string = str(datetime.timedelta(seconds=int(time)))[2:]
                    set_string = f"{int(distance)} m - {time_string}"
                elif time is not None:
                    set_string = f"{time} s"
                else:
                    set_string = ""

                set_data.append(
                    {
                        "timestamp": self._readable_datetime(timestamp),
                        "set_detail": set_string,
                    }
                )

        # Group sets by timestamp
        grouped_sets = [
            list(group) for _, group in groupby(set_data, key=lambda x: x["timestamp"])
        ]

        return grouped_sets

    def _get_workout_last_update(self, workoutID: int) -> str:
        """Return human readable string for when timestamp of last set
        for exercise in workout.

        Parameters
        ----------
        workoutID : int
            workoutID

        Returns
        -------
        str
            Human readable relative string
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(datetime) FROM sets WHERE exerciseID in (SELECT exerciseID FROM workout_exercise WHERE workoutID = ?)",
                (workoutID,),
            )
            timestamp = cur.fetchone()

        conn.close()

        if timestamp[0] is None:
            return "Never"

        return self._readable_datetime(timestamp[0])

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
        elif delta_seconds < 3600 * 24:
            return "Earlier today"
        elif delta_seconds < 3600 * 24 * 2:
            return "Yesterday"
        elif delta_seconds < 3600 * 24 * 7:
            days = int(delta_seconds / (3600 * 24))
            return f"{days} days ago"
        else:
            return dt.strftime("%b %d %Y")
