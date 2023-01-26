"use strict";

document.addEventListener("DOMContentLoaded", () => {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  fab.addEventListener("click", saveSet);
});

function saveSet(e: Event) {
  let set_data = {
    exerciseID: "",
    datetime: isoDateTime(),
    distance_m: "",
    weight_kg: "",
    time_s: "",
    repetitions: "",
  };

  let exerciseID: HTMLInputElement = document.querySelector(
    "#exerciseID"
  ) as HTMLInputElement;
  if (exerciseID == null) {
    //error
  } else {
    set_data.exerciseID = exerciseID.value;
  }

  let distance_m: HTMLInputElement = document.querySelector(
    "#distance"
  ) as HTMLInputElement;
  if (distance_m != null) {
    set_data.distance_m = distance_m.value;
  }

  let weight_kg: HTMLInputElement = document.querySelector(
    "#weight"
  ) as HTMLInputElement;
  if (weight_kg != null) {
    set_data.weight_kg = weight_kg.value;
  }

  let reps: HTMLInputElement = document.querySelector(
    "#reps"
  ) as HTMLInputElement;
  if (reps != null) {
    set_data.repetitions = reps.value;
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
    set_data.time_s = time_s.toString();
  }

  let postData = new FormData();
  postData.append("set", JSON.stringify(set_data));

  fetch("/add-set", {
    method: "POST",
    body: postData,
  }).then((res) => {
    if (res.ok) {
      saveSuccess();
    } else {
      saveError();
    }
  });
}

/**
 * Return ISO8601 datetime without milliseconds
 */
function isoDateTime() {
  return new Date().toISOString().split(".")[0] + "Z";
}

function saveSuccess() {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  fab.classList.add("save-success");
  setTimeout(() => {
    fab.classList.remove("save-success");
  }, 2500);
}

function saveError() {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;
  fab.classList.add("save-error");
  setTimeout(() => {
    fab.classList.remove("save-error");
  }, 2500);
}
