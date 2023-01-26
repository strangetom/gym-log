"use strict";
document.addEventListener("DOMContentLoaded", () => {
    let fab = document.querySelector("#fab");
    fab.addEventListener("click", saveSet);
});
function saveSet(e) {
    let set_data = {
        exerciseID: "",
        datetime: isoDateTime(),
        distance_m: "",
        weight_kg: "",
        time_s: "",
        repetitions: "",
    };
    let exerciseID = document.querySelector("#exerciseID");
    if (exerciseID == null) {
    }
    else {
        set_data.exerciseID = exerciseID.value;
    }
    let distance_m = document.querySelector("#distance");
    if (distance_m != null) {
        set_data.distance_m = distance_m.value;
    }
    let weight_kg = document.querySelector("#weight");
    if (weight_kg != null) {
        set_data.weight_kg = weight_kg.value;
    }
    let reps = document.querySelector("#reps");
    if (reps != null) {
        set_data.repetitions = reps.value;
    }
    let hours = document.querySelector("#hours");
    let mins = document.querySelector("#mins");
    let secs = document.querySelector("#secs");
    if (hours != null && mins != null && secs != null) {
        let time_s = Number(secs.value) + Number(mins.value) * 60 + Number(hours.value) * 3600;
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
        }
        else {
            saveError();
        }
    });
}
function isoDateTime() {
    return new Date().toISOString().split(".")[0] + "Z";
}
function saveSuccess() {
    let fab = document.querySelector("#fab");
    fab.classList.add("save-success");
    setTimeout(() => {
        fab.classList.remove("save-success");
    }, 2500);
}
function saveError() {
    let fab = document.querySelector("#fab");
    fab.classList.add("save-error");
    setTimeout(() => {
        fab.classList.remove("save-error");
    }, 2500);
}
