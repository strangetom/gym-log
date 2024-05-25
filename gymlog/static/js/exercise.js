const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
let timer;
var wakelock = null;
var WakelockStatus;
(function (WakelockStatus) {
    WakelockStatus[WakelockStatus["Enable"] = 1] = "Enable";
    WakelockStatus[WakelockStatus["Disable"] = 2] = "Disable";
})(WakelockStatus || (WakelockStatus = {}));
class Timer {
    constructor(timerEl) {
        this.startTime = 0;
        this.pauseElapsed = 0;
        this.interval = null;
        this.wakelock = null;
        this.timerEl = timerEl;
        this.displayEl = timerEl.querySelector("#timer-display");
        this.millisEl = timerEl.querySelector("#timer-display-millis");
        this.playPauseEl = timerEl.querySelector("#timer-start-btn");
    }
    toggle() {
        if (this.interval == null) {
            this.startTime = Date.now();
            this.interval = setInterval(this.display.bind(this), 100);
            this.togglePlayPause();
            this.display();
            toggleWakeLock(WakelockStatus.Enable);
        }
        else {
            this.pauseElapsed = Date.now() - this.startTime + this.pauseElapsed;
            clearInterval(this.interval);
            this.interval = null;
            this.togglePlayPause();
            toggleWakeLock(WakelockStatus.Disable);
        }
    }
    reset() {
        clearInterval(this.interval);
        this.interval = null;
        this.pauseElapsed = 0;
        let img = this.playPauseEl.querySelector("img");
        img.src = "/static/img/play.svg";
        this.displayEl.innerHTML = "&ndash;&ndash;:&ndash;&ndash;:&ndash;&ndash;";
        this.millisEl.innerHTML = "&ndash;&ndash;&ndash;";
        this.timerEl.classList.remove("paused");
        this.timerEl.classList.remove("running");
        toggleWakeLock(WakelockStatus.Disable);
    }
    display() {
        let elapsedMillis = Date.now() - this.startTime + this.pauseElapsed;
        let elapsedSecs = elapsedMillis / 1000;
        let hours = Math.floor(Math.floor(elapsedSecs) / 3600);
        let minutes = Math.floor((Math.floor(elapsedSecs) % 3600) / 60);
        let seconds = Math.floor(Math.floor(elapsedSecs) % 60);
        let millis = (elapsedSecs % 1) * 1000;
        let roundedMillis = Math.ceil(millis / 10) * 10;
        let displayHours = hours < 10 ? "0" + hours : hours.toString();
        let displayMinutes = minutes < 10 ? "0" + minutes : minutes.toString();
        let displaySeconds = seconds < 10 ? "0" + seconds : seconds.toString();
        this.displayEl.innerText =
            displayHours + ":" + displayMinutes + ":" + displaySeconds;
        this.millisEl.innerText = roundedMillis.toString().padStart(3, "0");
    }
    togglePlayPause() {
        let img = this.playPauseEl.querySelector("img");
        if (img.src.endsWith("play.svg")) {
            img.src = "/static/img/pause.svg";
            this.timerEl.classList.remove("paused");
            this.timerEl.classList.add("running");
        }
        else {
            img.src = "/static/img/play.svg";
            this.timerEl.classList.add("paused");
            this.timerEl.classList.remove("running");
        }
    }
}
document.addEventListener("DOMContentLoaded", () => {
    let form = document.querySelector("#todays-sets > form");
    form.addEventListener("formdata", insertUUIDTimestamp);
    let offline = JSON.parse(localStorage.getItem("offline"));
    if (offline) {
        document.querySelector("#offline").classList.remove("hidden");
        form.addEventListener("submit", saveLocally);
    }
    else {
        form.addEventListener("submit", saveToServer);
    }
    let newSetInputs = document.querySelectorAll("#todays-sets input");
    newSetInputs.forEach((el) => {
        el.addEventListener("click", (e) => {
            e.target.select();
        });
    });
    let editSetInputs = document.querySelectorAll("#edit-set-dialog input");
    editSetInputs.forEach((el) => {
        el.addEventListener("click", (e) => {
            e.target.select();
        });
    });
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
    let timerEl = document.querySelector(".timer");
    if (timerEl != null) {
        timer = new Timer(timerEl);
        let timerStartBtn = document.querySelector("#timer-start-btn");
        timerStartBtn.addEventListener("click", () => {
            timer.toggle();
        });
        let timerStopBtn = document.querySelector("#timer-stop-btn");
        timerStopBtn.addEventListener("click", () => {
            timer.reset();
        });
    }
    var inputTimer;
    let notes = document.querySelector("#notes textarea");
    notes.addEventListener("input", (e) => {
        clearTimeout(inputTimer);
        inputTimer = setTimeout(patchNotes, 500);
    });
    showOfflineSets();
});
function isoDateTime() {
    return new Date().toISOString().split(".")[0] + "Z";
}
function patchNotes(e) {
    let exerciseID = document.querySelector("#exerciseID")
        .value;
    let notes = document.querySelector("#notes textarea");
    let patch_data = new FormData();
    patch_data.append("notes", notes.value);
    let url = `/exercise/${exerciseID}`;
    fetch(url, {
        method: "PATCH",
        body: patch_data,
    });
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
    let difficultInput = editDialog.querySelector("#difficult");
    if (set.dataset.difficult == "True") {
        difficultInput.checked = true;
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
async function toggleWakeLock(status) {
    if (status == WakelockStatus.Enable && wakelock == null) {
        try {
            wakelock = await navigator.wakeLock.request("screen");
        }
        catch (err) {
            console.log(`Wakelock failed: ${err.message}`);
        }
    }
    else if (status == WakelockStatus.Disable && wakelock != null) {
        wakelock.release().then(() => (wakelock = null));
    }
}
function insertUUIDTimestamp(e) {
    let uuid = crypto.randomUUID();
    let timestamp = new Date().toISOString().split(".")[0] + "Z";
    e.formData.append("timestamp", timestamp);
    e.formData.append("uuid", uuid);
}
function saveToServer(e) {
    e.preventDefault();
    let form = document.querySelector("#todays-sets > form");
    let formdata = new FormData(form);
    fetch("/set/", {
        method: "POST",
        body: formdata,
    }).then((res) => {
        if (res.ok) {
            window.location.reload();
        }
        else {
            let btn = form.querySelector("button");
            btn.classList.add("save-error");
            setTimeout(() => {
                btn.classList.remove("save-error");
            }, 2500);
        }
    });
}
function saveLocally(e) {
    e.preventDefault();
    let form = document.querySelector("#todays-sets > form");
    let formdata = new FormData(form);
    let data = Object.fromEntries(formdata);
    let offlineData = JSON.parse(localStorage.getItem("offline-sets")) || [];
    offlineData.push(data);
    localStorage.setItem("offline-sets", JSON.stringify(offlineData));
    showOfflineSets();
}
function removeLocalSet(e) {
    let set = e.target.closest("div");
    let uuid = set.dataset.uuid;
    let offlineData = JSON.parse(localStorage.getItem("offline-sets")) || [];
    let setRemovedData = offlineData.filter((s) => {
        return s.uuid != uuid;
    });
    localStorage.setItem("offline-sets", JSON.stringify(setRemovedData));
    showOfflineSets();
}
function showOfflineSets() {
    let exerciseID = document.querySelector("#exerciseID")
        .value;
    let offlineSets = JSON.parse(localStorage.getItem("offline-sets"));
    if (offlineSets == null) {
        return;
    }
    let offlineSetContainer = document.querySelector("#todays-sets .offline");
    offlineSetContainer.innerHTML = "";
    let relevantOfflineSets = offlineSets.filter((s) => {
        return s.exerciseID == exerciseID;
    });
    if (relevantOfflineSets.length == 0) {
        return;
    }
    relevantOfflineSets.forEach((data) => {
        let card = document.createElement("div");
        card.classList.add("offline-card");
        card.dataset.uuid = data.uuid;
        let value = document.createElement("h3");
        value.innerText = formatSetValue(data);
        let date = document.createElement("span");
        date.innerText = formatSetTimestamp(data.timestamp);
        let icon = document.createElement("img");
        icon.src = "/static/img/delete.svg";
        icon.addEventListener("click", removeLocalSet);
        date.appendChild(icon);
        card.appendChild(value);
        card.appendChild(date);
        offlineSetContainer.appendChild(card);
    });
    offlineSetContainer.parentElement.scrollTop = 0;
}
function formatSetValue(data) {
    let keys = Object.keys(data);
    if (keys.includes("weight") && keys.includes("reps")) {
        return `${data.reps} x ${data.weight}`;
    }
    if (keys.includes("secs") && keys.includes("distance")) {
        return `${Math.floor(data.distance)} m - ${data.mins}:${data.secs}`;
    }
    if (keys.includes("secs")) {
        return `${data.secs} s`;
    }
    return "";
}
function formatSetTimestamp(timestamp) {
    let date = new Date(timestamp);
    return date.toDateString().slice(4);
}
export {};
