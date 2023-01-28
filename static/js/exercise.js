import { saveError, saveSuccess } from "./saveFunctions.js";
document.addEventListener("DOMContentLoaded", () => {
    let fab = document.querySelector("#fab");
    fab.addEventListener("click", saveSet);
});
function saveSet(e) {
    let setData = {
        exerciseID: "",
        datetime: isoDateTime(),
        distance_m: "",
        weight_kg: "",
        time_s: "",
        repetitions: "",
    };
    let exerciseIDEl = document.querySelector("#exerciseID");
    if (exerciseIDEl == null) {
    }
    else {
        setData.exerciseID = exerciseIDEl.value;
    }
    let distance_m = document.querySelector("#distance");
    if (distance_m != null) {
        setData.distance_m = distance_m.value;
    }
    let weight_kg = document.querySelector("#weight");
    if (weight_kg != null) {
        setData.weight_kg = weight_kg.value;
    }
    let reps = document.querySelector("#reps");
    if (reps != null) {
        setData.repetitions = reps.value;
    }
    let hours = document.querySelector("#hours");
    let mins = document.querySelector("#mins");
    let secs = document.querySelector("#secs");
    if (hours != null && mins != null && secs != null) {
        let time_s = Number(secs.value) + Number(mins.value) * 60 + Number(hours.value) * 3600;
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
function isoDateTime() {
    return new Date().toISOString().split(".")[0] + "Z";
}
