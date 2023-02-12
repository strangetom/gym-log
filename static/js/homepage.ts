import { saveError, saveSuccess } from "./saveFunctions.js";

const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
  duration: 100,
  easing: "ease-out",
};

document.addEventListener("DOMContentLoaded", () => {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  let addWorkoutDialog: HTMLDialogElement = document.querySelector(
    "#new-workout-dialog"
  );
  fab.addEventListener("click", () => {
    addWorkoutDialog.showModal();
  });

  addWorkoutDialog.addEventListener("click", (event) => {
    if ((event.target as HTMLElement).nodeName === "DIALOG") {
      let animation = addWorkoutDialog.animate(
        hideDialogAnimation,
        hideDialogTiming
      );
      animation.addEventListener("finish", () => {
        addWorkoutDialog.close("cancel");
      });
    }
  });

  let cancelBtn = addWorkoutDialog.querySelector("button[value='cancel']");
  cancelBtn.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = addWorkoutDialog.animate(
      hideDialogAnimation,
      hideDialogTiming
    );
    animation.addEventListener("finish", () => {
      addWorkoutDialog.close("cancel");
    });
  });

  let addBtn = addWorkoutDialog.querySelector("button[value='submit']");
  addBtn.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = addWorkoutDialog.animate(
      hideDialogAnimation,
      hideDialogTiming
    );
    animation.addEventListener("finish", () => {
      addWorkoutDialog.close("submit");
      addWorkout();
    });
  });
});

function addWorkout() {
  let addWorkoutDialog: HTMLDialogElement = document.querySelector(
    "#new-workout-dialog"
  );
  let formEl: HTMLFormElement = addWorkoutDialog.querySelector("form");
  let post_data = new FormData(formEl);

  if (addWorkoutDialog.returnValue == "submit") {
    fetch("/workout/", {
      method: "POST",
      body: post_data,
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  }
}
