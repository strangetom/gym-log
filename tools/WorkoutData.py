#!/usr/bin/env python3

import datetime
import sqlite3
from slugify import slugify

from typing import Any, Dict, List


class WorkoutData:
    def __init__(self, db):
        self.db = db

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

    def _get_exercise_last_update(self, exerciseID: int) -> str:
        """Return human readable string for when timestamp of last set
        for exercise.

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
                "SELECT MAX(datetime) FROM sets WHERE exerciseID = ?", (exerciseID,)
            )
            timestamp = cur.fetchone()

        conn.close()

        if timestamp[0] is None:
            return "Never"

        return self._readable_datetime(timestamp[0])

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

                exercise_data.append(
                    {
                        "name": name,
                        "last_update": self._get_exercise_last_update(exerciseID),
                        "last_set": "10 x 47 kg",
                    }
                )

        conn.close()

        return exercise_data
