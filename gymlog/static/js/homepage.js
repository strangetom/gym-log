const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
var OfflineStatus;
(function (OfflineStatus) {
    OfflineStatus[OfflineStatus["ONLINE"] = 0] = "ONLINE";
    OfflineStatus[OfflineStatus["OFFLINE"] = 1] = "OFFLINE";
})(OfflineStatus || (OfflineStatus = {}));
document.addEventListener("DOMContentLoaded", () => {
    installServiceWorker();
    let offlineBtn = document.querySelector("#offline");
    offlineBtn.addEventListener("click", toggleOfflineStatus);
    let offline = JSON.parse(localStorage.getItem("offline"));
    if (offline) {
        setOfflineStatus(OfflineStatus.OFFLINE);
    }
    let fab = document.querySelector("#fab");
    let addWorkoutDialog = document.querySelector("#new-workout-dialog");
    fab.addEventListener("click", () => {
        addWorkoutDialog.showModal();
    });
    let workouts = document.querySelectorAll("a.workout-card");
    let offlineSets = JSON.parse(localStorage.getItem("offline-sets")) || [];
    workouts.forEach((el) => {
        let workoutID = el.dataset.workoutid;
        let count = offlineSets.filter((s) => {
            return s.workoutID == workoutID;
        }).length;
        if (count > 0) {
            el.querySelector("img.offline").classList.remove("hidden");
        }
    });
    addWorkoutDialog.addEventListener("click", (event) => {
        if (event.target.nodeName === "DIALOG") {
            let animation = addWorkoutDialog.animate(hideDialogAnimation, hideDialogTiming);
            animation.addEventListener("finish", () => {
                addWorkoutDialog.close("cancel");
            });
        }
    });
    let cancelBtn = addWorkoutDialog.querySelector("button[value='cancel']");
    cancelBtn.addEventListener("click", (e) => {
        e.preventDefault();
        let animation = addWorkoutDialog.animate(hideDialogAnimation, hideDialogTiming);
        animation.addEventListener("finish", () => {
            addWorkoutDialog.close("cancel");
        });
    });
    let addBtn = addWorkoutDialog.querySelector("button[value='submit']");
    addBtn.addEventListener("click", (e) => {
        e.preventDefault();
        let animation = addWorkoutDialog.animate(hideDialogAnimation, hideDialogTiming);
        animation.addEventListener("finish", () => {
            addWorkoutDialog.close("submit");
            addWorkout();
        });
    });
});
function addWorkout() {
    let addWorkoutDialog = document.querySelector("#new-workout-dialog");
    let formEl = addWorkoutDialog.querySelector("form");
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
function toggleOfflineStatus() {
    let offline = JSON.parse(localStorage.getItem("offline"));
    if (offline) {
        setOfflineStatus(OfflineStatus.ONLINE);
        syncOfflineSets();
    }
    else {
        setOfflineStatus(OfflineStatus.OFFLINE);
    }
}
function setOfflineStatus(mode) {
    let btn = document.querySelector("#offline");
    let img = btn.querySelector("img");
    if (mode == OfflineStatus.ONLINE) {
        localStorage.setItem("offline", "false");
        img.src = "/static/img/online.svg";
    }
    else {
        localStorage.setItem("offline", "true");
        img.src = "/static/img/offline.svg";
    }
}
function syncOfflineSets() {
    let offlineSets = JSON.parse(localStorage.getItem("offline-sets"));
    if (offlineSets === null || offlineSets.length == 0) {
        return;
    }
    let form = new FormData();
    form.append("offline_sets", JSON.stringify(offlineSets));
    fetch("/sync", {
        method: "POST",
        body: form,
    }).then((res) => {
        if (res.ok) {
            localStorage.setItem("offline-sets", "[]");
        }
    });
}
function installServiceWorker() {
    if ("serviceWorker" in navigator) {
        console.log("CLIENT: service worker registration in progress.");
        navigator.serviceWorker.register("/service-worker.js").then(function () {
            console.log("CLIENT: service worker registration complete.");
        }, function () {
            console.log("CLIENT: service worker registration failure.");
        });
    }
    else {
        console.log("CLIENT: service worker is not supported.");
    }
}
export {};
