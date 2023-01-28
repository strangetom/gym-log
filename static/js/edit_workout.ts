import { saveError, saveSuccess } from "./saveFunctions.js";

document.addEventListener("DOMContentLoaded", () => {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  fab.addEventListener("click", saveWorkout);
});

function saveWorkout(e: Event) {
  let workoutID: number;
  let workoutIDEl: HTMLInputElement = document.querySelector(
    "#workoutID"
  ) as HTMLInputElement;
  if (workoutIDEl == null) {
    //error
  } else {
    workoutID = Number(workoutIDEl.value);
  }

  let selectedExerciseIDs: number[] = [];
  let exerciseOptions: NodeListOf<HTMLInputElement> = document.querySelectorAll(
    "input[type='checkbox']"
  );
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
        // Redirect if instructed
        window.location.href = res.url;
      } else {
        saveSuccess();
      }
    } else {
      saveError();
    }
  });
}
