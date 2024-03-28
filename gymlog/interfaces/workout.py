#!/usr/bin/env python3

import datetime
import math
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from peewee import fn, IntegrityError

from gymlog.models import Workout, Exercise, Sets, WorkoutExercise


@dataclass
class ExerciseSet:
    uid: int
    datetime: str
    distance_m: Optional[float]
    weight_kg: Optional[float]
    time_s: Optional[int]
    repetitions: Optional[int]

    def __post_init__(self):
        if self.time_s is not None:
            self.hours = math.floor(float(self.time_s) / 3600) or None
            self.mins = math.floor((float(self.time_s) % 3600) / 60) or None
            self.seconds = math.floor(float(self.time_s) % 60) or None
        else:
            self.hours = None
            self.mins = None
            self.seconds = None


@dataclass
class ExerciseStats:
    specific_stat: str
    specific_stat_heading: str
    last_workout: str
    last_set: str
    aggregate: str


class WorkoutInterface:
    def __init__(self):
        pass

    def get_workout_name(self, workoutID: int) -> str:
        """Return workout name from workoutID

        Parameters
        ----------
        workoutID : int
            Workout ID

        Returns
        -------
        str
            Workout name
        """
        query = Workout.get(Workout.workout_id == workoutID)
        return query.name

    def get_workout_colour(self, workoutID: int) -> str:
        """Return hex colour for workout from workoutID

        Parameters
        ----------
        workoutID : int
            Workout ID

        Returns
        -------
        str
            Colour associated with workout
        """
        query = Workout.get(Workout.workout_id == workoutID)
        return query.colour

    def get_exercise_name(self, exerciseID: int) -> str:
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
        query = Exercise.get(Exercise.exercise_id == exerciseID)
        return query.name

    def get_exercise_type(self, exerciseID: int) -> str:
        """Return exercise type from exercise ID

        Parameters
        ----------
        exerciseID : int
            Exercise ID

        Returns
        -------
        str
            Exercise name
        """
        query = Exercise.get(Exercise.exercise_id == exerciseID)
        return query.type_

    def list_workouts(self) -> List[Dict[str, Any]]:
        """List all workouts in log

        Returns
        -------
        List[Dict[str, Any]]
            List of dictionaries with the following keys
                name
                exercise_count
                workoutID
                colour
                last_update
                last_exercise
        """
        workout_data = []
        # Get list of workouts
        workouts = Workout.select()
        for w in workouts:
            # For each workout, count number of exercises
            count = (
                WorkoutExercise.select()
                .where(WorkoutExercise.workout == w.workout_id)
                .count()
            )

            exercise, update = self._get_workout_last_update(w.workout_id)
            workout_data.append(
                {
                    "name": w.name,
                    "exercise_count": count,
                    "workoutID": w.workout_id,
                    "colour": w.colour,
                    "last_update": update,
                    "last_exercise": exercise,
                }
            )

        return workout_data

    def list_all_exercises(self) -> List[Dict[str, str]]:
        """Return all exercises in database

        Returns
        -------
        List[Dict[str, str]]
            List of dicts containing name and exercise ID for all exercises
        """
        all_exercises = []
        exercises = Exercise.select()
        all_exercises = [
            {"name": e.name, "exerciseID": e.exercise_id} for e in exercises
        ]
        return sorted(all_exercises, key=lambda x: x["name"])

    def list_workout_exercises(self, workoutID: int) -> List[Dict[str, str]]:
        """Return exercises for workout given by workoutID

        Parameters
        ----------
        workoutID : int
            Workout ID

        Returns
        -------
        List[Dict[str, str]]
            List of dicts containing name, exerciseID, last update
            and last set details
        """
        exercise_data = []
        exercises = WorkoutExercise.select().where(WorkoutExercise.workout == workoutID)
        for e in exercises:

            query = Exercise.get(Exercise.exercise_id == e.exercise)
            set_ = self.get_exercise_last_set(e.exercise)

            if set_.repetitions is not None and set_.weight_kg is not None:
                set_string = f"{set_.repetitions} x {set_.weight_kg} kg"
            elif set_.distance_m is not None and set_.time_s is not None:
                time_string = str(datetime.timedelta(seconds=int(set_.time_s)))[2:]
                set_string = f"{set_.distance_m / 1000:.2f} km / {time_string}"
            elif set_.time_s is not None:
                set_string = f"{set_.time_s} s"
            else:
                set_string = ""

            exercise_data.append(
                {
                    "name": query.name,
                    "exerciseID": query.exercise_id,
                    "last_update": self._readable_datetime(set_.datetime),
                    "is_today": self._timestamp_is_today(set_.datetime),
                    "last_set": set_string,
                }
            )

        # Sort alpabetically by name and return
        return sorted(exercise_data, key=lambda x: x["name"])

    def list_todays_exercise_sets(self, exerciseID: int) -> List[Dict[str, Any]]:
        """Get list of most recent sets limited by <number> for exercise.
        Sets are grouped by date.

        Parameters
        ----------
        exerciseID : int
            Exercise ID

        Returns
        -------
        List[Dict[str, Any]]
            List of dicts containing set timestamp and detail.
        """
        set_data = []
        sets = (
            Sets.select()
            .where(Sets.exercise == exerciseID)
            .order_by(Sets.uid.desc())
            .limit(15)  # Assume no more than 15 sets per day ever
        )
        for s in sets:
            if not self._timestamp_is_today(s.datetime):
                continue

            current_set = ExerciseSet(
                s.uid, s.datetime, s.distance_m, s.weight_kg, s.time_s, s.repetitions
            )
            set_string = self._create_set_summary(current_set)

            previous_set = self._get_previous_set(exerciseID, s.uid)
            if previous_set is not None:
                delta = self._calculate_set_delta(current_set, previous_set)
            else:
                delta = None

            # Convert time (seconds) to hours, minutes and seconds
            if s.time_s is not None:
                hours = math.floor(float(s.time_s) / 3600) or None
                mins = math.floor((float(s.time_s) % 3600) / 60) or None
                seconds = math.floor(float(s.time_s) % 60) or None
            else:
                hours = None
                mins = None
                seconds = None

            set_data.append(
                {
                    "uid": s.uid,
                    "timestamp": s.datetime,
                    "readable_time": self._readable_datetime(s.datetime),
                    "set_detail": set_string,
                    "distance": s.distance_m,
                    "weight": s.weight_kg,
                    "hours": hours,
                    "mins": mins,
                    "seconds": seconds,
                    "repetitions": s.repetitions,
                    "delta": delta,
                    "difficult": s.difficult,
                }
            )

        return set_data

    def get_exercise_history(
        self, exerciseID: int, num_sets: int = 25
    ) -> Dict[int, List[Tuple[str, str]]]:
        """Get historical sets for this exercise going back `period_days`.

        Parameters
        ----------
        exerciseID : int
            Exercise ID
        num_sets : int, optional
            Number of sets to include

        Returns
        -------
        Dict[int, List[Tuple[str, str]]]
            Dict.
            The key is the number of days ago the set was logged.
            The value is a list of tuple of (scaled value, value)
                For weight-repetition exercises, the value is weight*repetition
                For distance-time exercises, the value is distance/time
                For time exercises, the value is time
        """
        exercise_type = self.get_exercise_type(exerciseID)

        data = {}
        max_value = 0
        min_value = 1e6

        sets = (
            Sets.select()
            .where(Sets.exercise == exerciseID)
            .order_by(Sets.datetime.desc())
        )
        if exercise_type == "weight-repetitions":
            for s in sets:
                time_delta = self._parse_timestamp(s.datetime) - datetime.datetime.now(
                    datetime.timezone.utc
                )

                if time_delta.days in data.keys():
                    data[time_delta.days].append(
                        {
                            "value": s.weight_kg * s.repetitions,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    )
                else:
                    data[time_delta.days] = [
                        {
                            "value": s.weight_kg * s.repetitions,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    ]

                max_value = max(max_value, s.weight_kg * s.repetitions)
                min_value = min(min_value, s.weight_kg * s.repetitions)

                if len(data.keys()) == num_sets:
                    break

        elif exercise_type == "distance-time":
            for s in sets:
                time_delta = self._parse_timestamp(s.datetime) - datetime.datetime.now(
                    datetime.timezone.utc
                )

                if time_delta.days in data.keys():
                    data[time_delta.days].append(
                        {
                            "value": s.distance_m / s.time_s,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    )
                else:
                    data[time_delta.days] = [
                        {
                            "value": s.distance_m / s.time_s,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    ]

                max_value = max(max_value, s.distance_m / s.time_s)
                min_value = min(min_value, s.distance_m / s.time_s)

                if len(data.keys()) == num_sets:
                    break

        elif exercise_type == "time":
            for s in sets:
                time_delta = self._parse_timestamp(s.datetime) - datetime.datetime.now(
                    datetime.timezone.utc
                )

                if time_delta.days in data.keys():
                    data[time_delta.days].append(
                        {
                            "value": s.time_s,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    )
                else:
                    data[time_delta.days] = [
                        {
                            "value": s.time_s,
                            "today": self._timestamp_is_today(s.datetime),
                            "difficult": s.difficult,
                        }
                    ]

                max_value = max(max_value, s.time_s)
                min_value = min(min_value, s.time_s)

                if len(data.keys()) == num_sets:
                    break

        # Calculate a scaled value, offset so zero is at the 0.9*min_value,
        # then normalise. This is to better show the delta between sets
        # Format the value to 3 significant figures for diplay purposes tooltips
        max_value = max_value * 1.06
        min_value = min_value * 0.9
        for k, values in data.items():
            data[k] = [
                {
                    "scaled": f"{(v['value'] - min_value) / (max_value - min_value):.2g}",
                    "value": f"{v['value']:.3g}",
                    "today": v["today"],
                    "difficult": v["difficult"],
                }
                for v in values
            ]

        return data

    def get_exercise_stats(self, exerciseID: int) -> ExerciseStats:
        """Summary

        Parameters
        ----------
        exerciseID : int
            Exercise ID

        Returns
        -------
        ExerciseStats
            ExerciseStats object for exercise
        """
        exercise_type = self.get_exercise_type(exerciseID)

        sets = (
            Sets.select()
            .where(Sets.exercise == exerciseID)
            .order_by(Sets.datetime.desc())
        )
        # Exercise has not sets yet
        if not sets:
            return ExerciseStats("", "", "", "", "")

        latest_set = ExerciseSet(
            sets[0].uid,
            sets[0].datetime,
            sets[0].distance_m,
            sets[0].weight_kg,
            sets[0].time_s,
            sets[0].repetitions,
        )
        latest = self._create_set_summary(latest_set)
        recent = self._parse_timestamp(latest_set.datetime).strftime("%d %b")

        if exercise_type == "weight-repetitions":
            rep_max = self._calculate_one_rep_max(
                latest_set.weight_kg, latest_set.repetitions
            )
            total = sum(
                s.weight_kg * s.repetitions
                for s in sets
                if self._timestamp_is_within_year(s.datetime)
            )

            return ExerciseStats(
                f"{rep_max:.1f} kg", "1 rep max", recent, latest, f"{total:,g} kg"
            )

        elif exercise_type == "distance-time":

            total = (
                sum(
                    s.distance_m
                    for s in sets
                    if self._timestamp_is_within_year(s.datetime)
                )
                / 1000
            )
            speed = latest_set.distance_m / latest_set.time_s

            return ExerciseStats(
                f"{speed:.1f} m/s", "Speed", recent, latest, f"{total:,.2f} km"
            )
        elif exercise_type == "time":
            total_seconds = sum(
                s.time_s for s in sets if self._timestamp_is_within_year(s.datetime)
            )
            total_seconds_str = str(datetime.timedelta(seconds=int(total_seconds)))

            rep_max = max(s.time_s for s in sets)

            return ExerciseStats(
                f"{rep_max:.1f} s", "Longest", recent, latest, total_seconds_str
            )

    def save_set(self, post_data: Dict[str, str]) -> None:
        """Save new set to database

        Parameters
        ----------
        post_data : Dict[str, str]
            Data sent by client
        """
        # Create fallback timestamp in iso format, without milliseconds
        fallback_timestamp = (
            datetime.datetime.now(datetime.timezone.utc).isoformat().split(".")[0] + "Z"
        )

        # Convert time from hours, minutes, seconds into total seconds
        time = None
        hours = post_data.get("hours", None)
        mins = post_data.get("mins", None)
        secs = post_data.get("secs", None)
        if hours is not None and mins is not None and secs is not None:
            time = int(secs or 0) + 60 * int(mins or 0) + 3600 * int(hours or 0)

        new = Sets.create(
            datetime=post_data.get("timestamp", fallback_timestamp),
            distance_m=post_data.get("distance", None),
            exercise=post_data.get("exerciseID", None),
            repetitions=post_data.get("reps", None),
            time_s=time,
            weight_kg=post_data.get("weight", None),
            uuid=post_data.get("uuid", uuid.uuid4()),
        )
        new.save()

    def delete_set(self, uid: int) -> None:
        """Delete set given by set uid

        Parameters
        ----------
        uid : int
            Set unique ID
        """
        set_ = Sets.get(Sets.uid == uid)
        set_.delete_instance()

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
        set_ = Sets.get(Sets.uid == uid)
        set_.distance_m = data.get("distance_m", None)
        set_.weight_kg = data.get("weight_kg", None)
        set_.repetitions = data.get("repetitions", None)
        set_.difficult = True if data.get("difficult", False) else False

        if (
            "hours" in data.keys()
            and "mins" in data.keys()
            and "seconds" in data.keys()
        ):
            # Calculate time in seconds
            seconds = (
                int(data["hours"] or 0) * 3600
                + int(data["mins"] or 0) * 60
                + int(data["seconds"] or 0)
            )

            set_.time_s = seconds

        set_.save()

    def sync_sets(self, offline_sets: list[dict[str, str]]) -> None:
        """Sync sets saved offline to database.

        New sets are added to sets table. Any new sets with duplicate UUID are ignored.

        Parameters
        ----------
        offline_sets : list[dict[str, str]]
            List of sets saved offline
        """
        for set_ in offline_sets:
            try:
                self.save_set(set_)
            except IntegrityError:
                # Database constraint violated, probably due to duplicate UUID
                pass

    def save_workout(self, workoutID: int, workout_data: Dict[str, Any]) -> None:
        """Save changes to workout

        Parameters
        ----------
        workoutID : int
            Workout ID
        workout_data : Dict[str, Any]
            Dict containing latest workout name and exercise list
        """
        workout = Workout.get(Workout.workout_id == workoutID)
        workout.name = workout_data["name"]
        workout.save()

        # Get set of current exercise IDs
        current_exercises = self.list_workout_exercises(workoutID)
        current_exercise_IDs = {ex["exerciseID"] for ex in current_exercises}

        new_exercises = set(workout_data["exerciseIDs"]) - current_exercise_IDs
        deleted_exercises = current_exercise_IDs - set(workout_data["exerciseIDs"])

        for exerciseID in new_exercises:
            new = WorkoutExercise.create(workout=workoutID, exercise=exerciseID)
            new.save()

        for exerciseID in deleted_exercises:
            delete = WorkoutExercise.get(
                WorkoutExercise.workout == workoutID,
                WorkoutExercise.exercise == exerciseID,
            )
            delete.delete_instance()

    def new_exercise(self, name: str, exercise_type: str) -> None:
        """Add new exercise to database

        Parameters
        ----------
        name : str
            Name of exercise
        exercise_type : str
            Type of exercise
        """
        new = Exercise.create(name=name, type_=exercise_type)
        new.save()

    def delete_exercise(self, exerciseID: int) -> None:
        """Delete exercise given by set exerciseID.
        Delete association between exercise and any workouts.
        Delete any sets associated with exercise.

        Parameters
        ----------
        exerciseID : int
            Exercise ID
        """
        exercise = Exercise.get(Exercise.exercise_id == exerciseID)
        exercise.delete_instance(recursive=True)

    def new_workout(self, name: str, colour: str) -> None:
        """Add new workout to database

        Parameters
        ----------
        name : str
            Name of workout
        colour : str
            Workout colour
        """
        new = Workout.create(name=name, colour=colour)
        new.save()

    def delete_workout(self, workoutID: int) -> None:
        """Delete workout given by set workoutID.
        Delete association between workout and exercises.

        Parameters
        ----------
        workoutID : int
            Workout ID
        """
        workout = Workout.get(Workout.workout_id == workoutID)
        # Recursive deletes related model i.e. any WorkoutExercise
        # instance with same workoutID
        workout.delete_instance(recursive=True)

    def _get_workout_last_update(self, workoutID: int) -> Tuple[str, str]:
        """Return human readable string for when timestamp of last set
        for exercise in workout.

        Parameters
        ----------
        workoutID : int
            workoutID

        Returns
        -------
        Tuple[str, str, bool]
            Last exercise
            Human readable relative datetime string
        """
        exercises = WorkoutExercise.select(WorkoutExercise.exercise).where(
            WorkoutExercise.workout == workoutID
        )
        query = Sets.select(fn.MAX(Sets.datetime), Sets.exercise).where(
            Sets.exercise.in_(exercises)
        )
        latest = query[0]

        if latest.datetime is None:
            return "", "Never"
        else:
            return self.get_exercise_name(latest.exercise), self._readable_datetime(
                latest.datetime
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
        prev_set_id = Sets.select(fn.MAX(Sets.uid)).where(
            (Sets.exercise == exerciseID) & (Sets.uid < uid)
        )
        set_ = Sets.get_or_none(Sets.uid == prev_set_id)
        if set_ is None:
            return set_

        return ExerciseSet(
            set_.uid,
            set_.datetime,
            set_.distance_m,
            set_.weight_kg,
            set_.time_s,
            set_.repetitions,
        )

    def get_exercise_last_set(self, exerciseID: int) -> ExerciseSet:
        """Return ExerciseSet object for most recent set for exercise

        Parameters
        ----------
        exerciseID : int
            exerciseID

        Returns
        -------
        ExerciseSet
            Object containing set information
        """
        query = Sets.select(
            fn.MAX(Sets.datetime),
            Sets.uid,
            Sets.distance_m,
            Sets.weight_kg,
            Sets.time_s,
            Sets.repetitions,
        ).where(Sets.exercise == exerciseID)
        set_ = query[0]

        # Exercise has no sets yet
        if set_.uid is None:
            return ExerciseSet(0, "", None, None, None, None)

        return ExerciseSet(
            set_.uid,
            set_.datetime,
            set_.distance_m,
            set_.weight_kg,
            set_.time_s,
            set_.repetitions,
        )

    def _readable_datetime(self, timestamp: str | None) -> str:
        """Convert an ISO8601 timestamp into a human readable relative string

        Parameters
        ----------
        timestamp : str | None
            ISO8601 timestamp

        Returns
        -------
        str
            Human readable relative string
        """
        if timestamp is None or timestamp == "":
            return "Never"

        # Python <3.11 doesn't parse the Z in the timestamp, so the dt object is not
        # timezone aware. Replace Z with +00:00 to make it timezone aware
        dt = self._parse_timestamp(timestamp)

        delta = datetime.datetime.now(datetime.timezone.utc) - dt
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

    def _timestamp_is_today(self, timestamp: str | None) -> bool:
        """Return True is timestamp is same day as today

        Parameters
        ----------
        timestamp : str | None
            ISO8601 timestamp or None

        Returns
        -------
        bool
            True is timestamp day is today
        """
        if timestamp is None or timestamp == "":
            return False

        dt = self._parse_timestamp(timestamp)
        return dt.date() == datetime.date.today()

    def _timestamp_is_within_year(self, timestamp: str | None) -> bool:
        """Return True is timestamp is within a year of the current date.

        Parameters
        ----------
        timestamp : str | None
            ISO8601 timestamp or None

        Returns
        -------
        bool
            True if time since timestamp is less than or equal to a year
        """
        if timestamp is None or timestamp == "":
            return False

        dt = self._parse_timestamp(timestamp)
        delta = datetime.date.today() - dt.date()
        return delta.days <= 365

    def _create_set_summary(self, details: ExerciseSet) -> str:
        """Generate string that summarises a set
        For example:
        10× 39.0 kg for weight-repetitions exercises
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
            set_string = f"{details.distance_m / 1000:.2f} km / {time_string}"

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

        # Convert change from previous set to sensible string
        if change_from_previous == 0:
            delta = None
        else:
            delta = change_from_previous

        return delta

    def _parse_timestamp(self, timestamp: str) -> datetime.datetime:
        """Parse timestemp string into datetime.datetime object,
        being timezone aware

        Parameters
        ----------
        timestamp : str
            ISO8601 formatted timestamp

        Returns
        -------
        datetime.datetime
            Timestamp convert to datetime.datetime object
        """
        return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def _calculate_one_rep_max(self, weight: float, reps: int) -> float:
        """Calculate one rep max using Brzycki formula

        Parameters
        ----------
        weight : float
            Weight used for set
        reps : int
            Number of reps in set

        Returns
        -------
        float
            One rep max value
        """
        return weight / (1.0278 - 0.0278 * reps)
