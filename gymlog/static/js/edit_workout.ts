import { saveError, saveSuccess } from "./saveFunctions.js";

const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
  duration: 100,
  easing: "ease-out",
};

document.addEventListener("DOMContentLoaded", () => {
  let fab_save: HTMLButtonElement = document.querySelector(
    "#fab-save",
  ) as HTMLButtonElement;
  fab_save.addEventListener("click", saveWorkout);

  let fab_new_exercise: HTMLButtonElement = document.querySelector(
    "#fab-new-exercise",
  ) as HTMLButtonElement;
  let new_exercise_dialog: HTMLDialogElement = document.querySelector(
    "#new-exercise-dialog",
  ) as HTMLDialogElement;
  // Open new exercise when clicking new exercise FAB
  fab_new_exercise.addEventListener("click", () => {
    new_exercise_dialog.showModal();
  });

  // Close new exercise dialog when clicking backdrop
  new_exercise_dialog.addEventListener("click", (event) => {
    if ((event.target as HTMLElement).nodeName === "DIALOG") {
      let animation = new_exercise_dialog.animate(
        hideDialogAnimation,
        hideDialogTiming,
      );
      animation.addEventListener("finish", () => {
        new_exercise_dialog.close("cancel");
      });
    }
  });

  // Close new exercise dialog when clicking cancel
  let cancel_new_exercise: HTMLButtonElement =
    new_exercise_dialog.querySelector(
      "button[value='cancel']",
    ) as HTMLButtonElement;
  cancel_new_exercise.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = new_exercise_dialog.animate(
      hideDialogAnimation,
      hideDialogTiming,
    );
    animation.addEventListener("finish", () => {
      new_exercise_dialog.close("cancel");
    });
  });

  // Submit new exercise when clicking add
  let add_new_exercise: HTMLButtonElement = new_exercise_dialog.querySelector(
    "button[value='submit']",
  ) as HTMLButtonElement;
  add_new_exercise.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = new_exercise_dialog.animate(
      hideDialogAnimation,
      hideDialogTiming,
    );
    animation.addEventListener("finish", () => {
      new_exercise_dialog.close("submit");
      saveExercise();
    });
  });

  let fab_delete_workout: HTMLButtonElement = document.querySelector(
    "#fab-delete",
  ) as HTMLButtonElement;
  fab_delete_workout.addEventListener("click", deleteWorkout);

  let delete_exercise_btns: NodeListOf<HTMLImageElement> =
    document.querySelectorAll(".delete-exercise");
  delete_exercise_btns.forEach((el) => {
    el.addEventListener("click", deleteExercise);
  });
});

function saveWorkout(e: Event) {
  let workoutID: number;
  let workoutIDEl: HTMLInputElement = document.querySelector(
    "#workoutID",
  ) as HTMLInputElement;
  if (workoutIDEl == null) {
    //error
  } else {
    workoutID = Number(workoutIDEl.value);
  }

  let workoutName: string = (
    document.querySelector("#workout-name") as HTMLInputElement
  ).value;

  let selectedExerciseIDs: number[] = [];
  let exerciseOptions: NodeListOf<HTMLInputElement> = document.querySelectorAll(
    "input[type='checkbox']",
  );
  exerciseOptions.forEach((opt) => {
    if (opt.checked) {
      selectedExerciseIDs.push(Number(opt.dataset.exerciseid));
    }
  });
  let workoutData = {
    exerciseIDs: selectedExerciseIDs,
    name: workoutName,
  };

  let postData = new FormData();
  postData.append("workout", JSON.stringify(workoutData));

  let url = `/workout/${workoutID}`;
  fetch(url, {
    method: "PUT",
    body: postData,
  }).then((res) => {
    if (res.ok) {
      window.location.href = `/workout/${workoutID}`;
    } else {
      saveError("#fab-edit");
    }
  });
}

function deleteWorkout() {
  let workoutID: string = (
    document.querySelector("#workoutID") as HTMLInputElement
  ).value;
  if (confirm("Are you sure you want to delete this workout?")) {
    let url = `/workout/${workoutID}`;
    fetch(url, {
      method: "DELETE",
    }).then((res) => {
      if (res.ok) {
        window.location.href = "/";
      }
    });
  }
}

function saveExercise() {
  let new_exercise_dialog: HTMLDialogElement = document.querySelector(
    "#new-exercise-dialog",
  ) as HTMLDialogElement;
  if (new_exercise_dialog.returnValue == "submit") {
    let formEl: HTMLFormElement = new_exercise_dialog.querySelector("form");
    let post_data = new FormData(formEl);

    fetch("/exercise/", {
      method: "POST",
      body: post_data,
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      } else {
        saveError("#fab-new-exercise");
      }
    });
  }
}

function deleteExercise(e: Event) {
  let exerciseID: string = (e.target as HTMLImageElement).dataset.exerciseid;
  if (confirm("Are you sure you want to delete this exercise?")) {
    let url = `/exercise/${exerciseID}`;
    fetch(url, {
      method: "DELETE",
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  }
}
