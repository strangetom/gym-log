import { saveError, saveSuccess } from "./saveFunctions.js";

document.addEventListener("DOMContentLoaded", () => {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  fab.addEventListener("click", saveSet);

  let sets: NodeListOf<HTMLDivElement> = document.querySelectorAll(".set-card")
  sets.forEach( el => {
    el.addEventListener("click", showEditSetDialog)
  })
});

function saveSet(e: Event) {
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

  fetch("/save-set", {
    method: "POST",
    body: postData,
  }).then((res) => {
    if (res.ok) {
      if (res.redirected) {
        // Redirect if instructed
        window.location.href = res.url;
      } else {
        saveSuccess("#fab");
      }
    } else {
      saveError("#fab");
    }
  });
}

/**
 * Return ISO8601 datetime without milliseconds
 */
function isoDateTime() {
  return new Date().toISOString().split(".")[0] + "Z";
}

function showEditSetDialog(e: Event){
  let set: HTMLDivElement = (e.target as HTMLDivElement).closest(".set-card");
  let editDialog: HTMLDialogElement = document.querySelector("#edit-set-dialog");

  if (set.dataset.type == "weight-repetitions") {
    let repDialogInput: HTMLInputElement = editDialog.querySelector("#reps");
    repDialogInput.value = set.dataset.repetitions || "";
    let weightDialogInput: HTMLInputElement = editDialog.querySelector("#weight")
    weightDialogInput.value = set.dataset.weight || "";
  } else if (set.dataset.type == "distance-time") {
    let distanceDialogInput: HTMLInputElement = editDialog.querySelector("#distance")
    distanceDialogInput.value = set.dataset.distance || "";
    let hoursDialogInput: HTMLInputElement = editDialog.querySelector("#hours")
    hoursDialogInput.value = set.dataset.hours || "";
    let minsDialogInput: HTMLInputElement = editDialog.querySelector("#mins")
    minsDialogInput.value = set.dataset.mins || "";
    let secondsDialogInput: HTMLInputElement = editDialog.querySelector("#seconds")
    secondsDialogInput.value = set.dataset.seconds || "";
  } else if (set.dataset.type == "time") {
    let hoursDialogInput: HTMLInputElement = editDialog.querySelector("#hours")
    hoursDialogInput.value = set.dataset.hours || "";
    let minsDialogInput: HTMLInputElement = editDialog.querySelector("#mins")
    minsDialogInput.value = set.dataset.mins || "";
    let secondsDialogInput: HTMLInputElement = editDialog.querySelector("#seconds")
    secondsDialogInput.value = set.dataset.seconds || "";
  }

  
  editDialog.showModal()
}
