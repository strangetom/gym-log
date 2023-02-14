import { saveError } from "./saveFunctions.js";
const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
document.addEventListener("DOMContentLoaded", () => {
    let fab = document.querySelector("#fab");
    fab.addEventListener("click", saveSet);
    let graphBtn = document.querySelector("#graph-button");
    let graphSection = document.querySelector("#graph");
    graphBtn.addEventListener("click", () => {
        graphSection.classList.toggle("hidden");
    });
    graphSection.addEventListener("touchstart", swipeCloseGraph);
    let sets = document.querySelectorAll(".set-card");
    sets.forEach((el) => {
        el.addEventListener("click", showEditSetDialog);
    });
    let editDialog = document.querySelector("#edit-set-dialog");
    editDialog.addEventListener("click", (event) => {
        if (event.target.nodeName === "DIALOG") {
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
function saveSet() {
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
    fetch("/set/", {
        method: "POST",
        body: postData,
    }).then((res) => {
        if (res.ok) {
            window.location.reload();
        }
        else {
            saveError("#fab");
        }
    });
}
function isoDateTime() {
    return new Date().toISOString().split(".")[0] + "Z";
}
function showEditSetDialog(e) {
    let set = e.target.closest(".set-card");
    let editDialog = document.querySelector("#edit-set-dialog");
    editDialog.querySelector("#setID").value =
        set.dataset.uid;
    if (set.dataset.type == "weight-repetitions") {
        let repDialogInput = editDialog.querySelector("#repetitions");
        repDialogInput.value = set.dataset.repetitions || "";
        let weightDialogInput = editDialog.querySelector("#weight_kg");
        weightDialogInput.value = set.dataset.weight || "";
    }
    else if (set.dataset.type == "distance-time") {
        let distanceDialogInput = editDialog.querySelector("#distance_m");
        distanceDialogInput.value = set.dataset.distance || "";
        let hoursDialogInput = editDialog.querySelector("#hours");
        hoursDialogInput.value = set.dataset.hours || "";
        let minsDialogInput = editDialog.querySelector("#mins");
        minsDialogInput.value = set.dataset.mins || "";
        let secondsDialogInput = editDialog.querySelector("#seconds");
        secondsDialogInput.value = set.dataset.seconds || "";
    }
    else if (set.dataset.type == "time") {
        let hoursDialogInput = editDialog.querySelector("#hours");
        hoursDialogInput.value = set.dataset.hours || "";
        let minsDialogInput = editDialog.querySelector("#mins");
        minsDialogInput.value = set.dataset.mins || "";
        let secondsDialogInput = editDialog.querySelector("#seconds");
        secondsDialogInput.value = set.dataset.seconds || "";
    }
    editDialog.showModal();
}
function modifySet() {
    let editDialog = document.querySelector("#edit-set-dialog");
    let formEl = editDialog.querySelector("form");
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
    }
    else if (editDialog.returnValue == "delete") {
        fetch(url, {
            method: "DELETE",
        }).then((res) => {
            if (res.ok) {
                window.location.reload();
            }
        });
    }
}
function swipeCloseGraph(e) {
    if (e.changedTouches[0].target.closest("table") != null) {
        return;
    }
    e.preventDefault();
    let startY = e.changedTouches[0].pageY;
    let graph = e.changedTouches[0].target.closest("#graph");
    graph.addEventListener("touchend", function swipeEnd(e) {
        let endY = e.changedTouches[0].pageY;
        if (startY - endY > 30) {
            graph.classList.add("hidden");
        }
        graph.removeEventListener("touchend", swipeEnd);
    });
}
