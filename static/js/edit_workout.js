import { saveError, saveSuccess } from "./saveFunctions.js";
const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
document.addEventListener("DOMContentLoaded", () => {
    let fab_edit = document.querySelector("#fab-edit");
    fab_edit.addEventListener("click", saveWorkout);
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
});
function saveWorkout(e) {
    let workoutID;
    let workoutIDEl = document.querySelector("#workoutID");
    if (workoutIDEl == null) {
    }
    else {
        workoutID = Number(workoutIDEl.value);
    }
    let selectedExerciseIDs = [];
    let exerciseOptions = document.querySelectorAll("input[type='checkbox']");
    exerciseOptions.forEach((opt) => {
        if (opt.checked) {
            selectedExerciseIDs.push(Number(opt.dataset.exerciseid));
        }
    });
    let workoutData = { workoutID: workoutID, exerciseIDs: selectedExerciseIDs };
    let postData = new FormData();
    postData.append("workout", JSON.stringify(workoutData));
    fetch("/save-workout", {
        method: "POST",
        body: postData,
    }).then((res) => {
        if (res.ok) {
            saveSuccess("#fab-edit");
            window.history.back();
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
        fetch("/new-exercise", {
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
