import peewee as pw

database = pw.SqliteDatabase("data/gym-log.db")


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(pw.Model):
    class Meta:
        database = database


class Exercise(BaseModel):
    exercise_id = pw.AutoField(column_name="exerciseID")
    name = pw.TextField()
    type_ = pw.TextField(column_name="type")

    class Meta:
        table_name = "exercise"


class Sets(BaseModel):
    datetime = pw.TextField()
    distance_m = pw.FloatField(null=True)
    exercise = pw.ForeignKeyField(
        column_name="exerciseID", field="exercise_id", model=Exercise
    )
    repetitions = pw.IntegerField(null=True)
    time_s = pw.IntegerField(null=True)
    uid = pw.AutoField()
    weight_kg = pw.FloatField(null=True)

    class Meta:
        table_name = "sets"


class Workout(BaseModel):
    colour = pw.TextField(constraints=[pw.SQL("DEFAULT '#000'")])
    name = pw.TextField()
    workout_id = pw.AutoField(column_name="workoutID")

    class Meta:
        table_name = "workout"


class WorkoutExercise(BaseModel):
    exercise = pw.ForeignKeyField(
        column_name="exerciseID", field="exercise_id", model=Exercise
    )
    uid = pw.AutoField()
    workout = pw.ForeignKeyField(
        column_name="workoutID", field="workout_id", model=Workout
    )

    class Meta:
        table_name = "workout_exercise"
