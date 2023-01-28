import { saveError, saveSuccess } from "./saveFunctions.js";
document.addEventListener("DOMContentLoaded", () => {
    let fab = document.querySelector("#fab");
    fab.addEventListener("click", saveWorkout);
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
            if (res.redirected) {
                window.location.href = res.url;
            }
            else {
                saveSuccess();
            }
        }
        else {
            saveError();
        }
    });
}
