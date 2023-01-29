BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "exercise" (
	"exerciseID"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("exerciseID")
);
CREATE TABLE IF NOT EXISTS "workout_exercise" (
	"uid"	INTEGER NOT NULL,
	"workoutID"	INTEGER NOT NULL,
	"exerciseID"	INTEGER NOT NULL,
	FOREIGN KEY("exerciseID") REFERENCES "exercise"("exerciseID"),
	FOREIGN KEY("workoutID") REFERENCES "workout"("workoutID"),
	PRIMARY KEY("uid")
);
CREATE TABLE IF NOT EXISTS "sets" (
	"uid"	INTEGER NOT NULL,
	"exerciseID"	INTEGER NOT NULL,
	"datetime"	TEXT NOT NULL,
	"distance_m"	REAL,
	"weight_kg"	REAL,
	"time_s"	TEXT,
	"repetitions"	INTEGER,
	FOREIGN KEY("exerciseID") REFERENCES "exercise"("exerciseID"),
	PRIMARY KEY("uid")
);
CREATE TABLE IF NOT EXISTS "workout" (
	"workoutID"	INT NOT NULL,
	"name"	TEXT NOT NULL,
	"slug"	TEXT NOT NULL,
	"colour"	TEXT NOT NULL DEFAULT #32302f,
	PRIMARY KEY("workoutID")
);
COMMIT;
