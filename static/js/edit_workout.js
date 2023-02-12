import { saveError, saveSuccess } from "./saveFunctions.js";
const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
document.addEventListener("DOMContentLoaded", () => {
    let fab_save = document.querySelector("#fab-save");
    fab_save.addEventListener("click", saveWorkout);
    let fab_new_exercise = document.querySelector("#fab-new-exercise");
    let new_exercise_dialog = document.querySelector("#new-exercise-dialog");
    fab_new_exercise.addEventListener("click", () => {
        new_exercise_dialog.showModal();
    });
    new_exercise_dialog.addEventListener("click", (event) => {
        if (event.target.nodeName === "DIALOG") {
            let animation = new_exercise_dialog.animate(hideDialogAnimation, hideDialogTiming);
            animation.addEventListener("finish", () => {
                new_exercise_dialog.close("cancel");
            });
        }
    });
    let cancel_new_exercise = new_exercise_dialog.querySelector("button[value='cancel']");
    cancel_new_exercise.addEventListener("click", (e) => {
        e.preventDefault();
        let animation = new_exercise_dialog.animate(hideDialogAnimation, hideDialogTiming);
        animation.addEventListener("finish", () => {
            new_exercise_dialog.close("cancel");
        });
    });
    let add_new_exercise = new_exercise_dialog.querySelector("button[value='submit']");
    add_new_exercise.addEventListener("click", (e) => {
        e.preventDefault();
        let animation = new_exercise_dialog.animate(hideDialogAnimation, hideDialogTiming);
        animation.addEventListener("finish", () => {
            new_exercise_dialog.close("submit");
            saveExercise();
        });
    });
    let fab_delete_workout = document.querySelector("#fab-delete");
    fab_delete_workout.addEventListener("click", deleteWorkout);
    let delete_exercise_btns = document.querySelectorAll(".delete-exercise");
    delete_exercise_btns.forEach((el) => {
        el.addEventListener("click", deleteExercise);
    });
});
function saveWorkout(e) {
    let workoutID;
    let workoutIDEl = document.querySelector("#workoutID");
    if (workoutIDEl == null) {
    }
    else {
        workoutID = Number(workoutIDEl.value);
    }
    let workoutName = document.querySelector("#workout-name").value;
    let selectedExerciseIDs = [];
    let exerciseOptions = document.querySelectorAll("input[type='checkbox']");
    exerciseOptions.forEach((opt) => {
        if (opt.checked) {
            selectedExerciseIDs.push(Number(opt.dataset.exerciseid));
        }
    });
    let workoutData = {
        workoutID: workoutID,
        exerciseIDs: selectedExerciseIDs,
        name: workoutName,
    };
    let postData = new FormData();
    postData.append("workout", JSON.stringify(workoutData));
    fetch("/save-workout", {
        method: "POST",
        body: postData,
    }).then((res) => {
        if (res.ok) {
            if (res.redirected) {
                window.location.href = res.url;
            }
            else {
                saveSuccess("#fab-edit");
            }
        }
        else {
            saveError("#fab-edit");
        }
    });
}
function saveExercise() {
    let new_exercise_dialog = document.querySelector("#new-exercise-dialog");
    if (new_exercise_dialog.returnValue == "submit") {
        let formEl = new_exercise_dialog.querySelector("form");
        let post_data = new FormData(formEl);
        fetch("/save-exercise", {
            method: "POST",
            body: post_data,
        }).then((res) => {
            if (res.ok) {
                window.location.reload();
            }
            else {
                saveError("#fab-new-exercise");
            }
        });
    }
}
function deleteWorkout() {
    let workoutID = document.querySelector("#workoutID").value;
    if (confirm("Are you sure you want to delete this workout?")) {
        let postData = new FormData();
        postData.append("workoutID", workoutID);
        fetch("/save-workout", {
            method: "DELETE",
            body: postData,
        }).then((res) => {
            if (res.ok) {
                window.location.href = "/";
            }
        });
    }
}
function deleteExercise(e) {
    let exerciseID = e.target.dataset.exerciseid;
    if (confirm("Are you sure you want to delete this exercise?")) {
        let postData = new FormData();
        postData.append("exerciseID", exerciseID);
        fetch("/save-exercise", {
            method: "DELETE",
            body: postData,
        }).then((res) => {
            if (res.ok) {
                window.location.reload();
            }
        });
    }
}
