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
  fab.addEventListener("click", saveSet);

  let sets: NodeListOf<HTMLDivElement> = document.querySelectorAll(".set-card");
  sets.forEach((el) => {
    el.addEventListener("click", showEditSetDialog);
  });

  let editDialog: HTMLDialogElement =
    document.querySelector("#edit-set-dialog");
  editDialog.addEventListener("click", (event) => {
    if ((event.target as HTMLElement).nodeName === "DIALOG") {
      let animation = editDialog.animate(hideDialogAnimation, hideDialogTiming);
      animation.addEventListener("finish", () => {
        editDialog.close("cancel");
      });
    }
  });

  let editBtn = editDialog.querySelector("button[value='edit']");
  editBtn.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = editDialog.animate(hideDialogAnimation, hideDialogTiming);
    animation.addEventListener("finish", () => {
      editDialog.close("edit");
      modifySet();
    });
  });

  let deleteBtn = editDialog.querySelector("button[value='delete']");
  deleteBtn.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = editDialog.animate(hideDialogAnimation, hideDialogTiming);
    animation.addEventListener("finish", () => {
      editDialog.close("delete");
      modifySet();
    });
  });

  let cancelBtn = editDialog.querySelector("button[value='cancel']");
  cancelBtn.addEventListener("click", (e) => {
    e.preventDefault();
    let animation = editDialog.animate(hideDialogAnimation, hideDialogTiming);
    animation.addEventListener("finish", () => {
      editDialog.close("cancel");
    });
  });
});
/**
 * Save new set to database
 */
function saveSet() {
  let setData = {
    exerciseID: "",
    datetime: isoDateTime(),
    distance_m: "",
    weight_kg: "",
    time_s: "",
    repetitions: "",
  };

  let exerciseIDEl: HTMLInputElement = document.querySelector(
    "#exerciseID"
  ) as HTMLInputElement;
  if (exerciseIDEl == null) {
    //error
  } else {
    setData.exerciseID = exerciseIDEl.value;
  }

  let distance_m: HTMLInputElement = document.querySelector(
    "#distance"
  ) as HTMLInputElement;
  if (distance_m != null) {
    setData.distance_m = distance_m.value;
  }

  let weight_kg: HTMLInputElement = document.querySelector(
    "#weight"
  ) as HTMLInputElement;
  if (weight_kg != null) {
    setData.weight_kg = weight_kg.value;
  }

  let reps: HTMLInputElement = document.querySelector(
    "#reps"
  ) as HTMLInputElement;
  if (reps != null) {
    setData.repetitions = reps.value;
  }

  let hours: HTMLInputElement = document.querySelector(
    "#hours"
  ) as HTMLInputElement;
  let mins: HTMLInputElement = document.querySelector(
    "#mins"
  ) as HTMLInputElement;
  let secs: HTMLInputElement = document.querySelector(
    "#secs"
  ) as HTMLInputElement;
  if (hours != null && mins != null && secs != null) {
    let time_s =
      Number(secs.value) + Number(mins.value) * 60 + Number(hours.value) * 3600;
    setData.time_s = time_s.toString();
  }

  let postData = new FormData();
  postData.append("set", JSON.stringify(setData));

  fetch("/set/", {
    method: "POST",
    body: postData,
  }).then((res) => {
    if (res.ok) {
      window.location.reload();
    } else {
      saveError("#fab");
    }
  });
}

/**
 * Return current ISO8601 datetime without milliseconds.
 */
function isoDateTime() {
  return new Date().toISOString().split(".")[0] + "Z";
}

/**
 * Show dialog for editing a set
 * @param {Event} e Click event for set to be edited.
 */
function showEditSetDialog(e: Event) {
  let set: HTMLDivElement = (e.target as HTMLDivElement).closest(".set-card");
  let editDialog: HTMLDialogElement =
    document.querySelector("#edit-set-dialog");

  (editDialog.querySelector("#setID") as HTMLInputElement).value =
    set.dataset.uid;

  if (set.dataset.type == "weight-repetitions") {
    let repDialogInput: HTMLInputElement =
      editDialog.querySelector("#repetitions");
    repDialogInput.value = set.dataset.repetitions || "";
    let weightDialogInput: HTMLInputElement =
      editDialog.querySelector("#weight_kg");
    weightDialogInput.value = set.dataset.weight || "";
  } else if (set.dataset.type == "distance-time") {
    let distanceDialogInput: HTMLInputElement =
      editDialog.querySelector("#distance_m");
    distanceDialogInput.value = set.dataset.distance || "";
    let hoursDialogInput: HTMLInputElement = editDialog.querySelector("#hours");
    hoursDialogInput.value = set.dataset.hours || "";
    let minsDialogInput: HTMLInputElement = editDialog.querySelector("#mins");
    minsDialogInput.value = set.dataset.mins || "";
    let secondsDialogInput: HTMLInputElement =
      editDialog.querySelector("#seconds");
    secondsDialogInput.value = set.dataset.seconds || "";
  } else if (set.dataset.type == "time") {
    let hoursDialogInput: HTMLInputElement = editDialog.querySelector("#hours");
    hoursDialogInput.value = set.dataset.hours || "";
    let minsDialogInput: HTMLInputElement = editDialog.querySelector("#mins");
    minsDialogInput.value = set.dataset.mins || "";
    let secondsDialogInput: HTMLInputElement =
      editDialog.querySelector("#seconds");
    secondsDialogInput.value = set.dataset.seconds || "";
  }

  editDialog.showModal();
}
/**
 * Modify set from dialog box.
 * Modification includes changing values or deleting the set.
 */
function modifySet() {
  let editDialog: HTMLDialogElement =
    document.querySelector("#edit-set-dialog");
  let formEl: HTMLFormElement = editDialog.querySelector("form");
  let post_data = new FormData(formEl);
  let setID = post_data.get("setID");
  let url = `/set/${setID}`;

  if (editDialog.returnValue == "edit") {
    fetch(url, {
      method: "PUT",
      body: post_data,
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  } else if (editDialog.returnValue == "delete") {
    fetch(url, {
      method: "DELETE",
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  }
}
