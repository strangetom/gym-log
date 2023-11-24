import { saveError, saveSuccess } from "./saveFunctions.js";

const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
  duration: 100,
  easing: "ease-out",
};

enum OfflineStatus {
  ONLINE,
  OFFLINE,
}

document.addEventListener("DOMContentLoaded", () => {
  installServiceWorker();

  let offlineBtn: HTMLButtonElement = document.querySelector(
    "#offline",
  ) as HTMLButtonElement;
  offlineBtn.addEventListener("click", toggleOfflineStatus);
  // Check is already in offline mode and set icon
  let offline = JSON.parse(localStorage.getItem("offline"));
  if (offline) {
    setOfflineStatus(OfflineStatus.OFFLINE);
  }

  let fab: HTMLButtonElement = document.querySelector(
    "#fab",
  ) as HTMLButtonElement;
  let addWorkoutDialog: HTMLDialogElement = document.querySelector(
    "#new-workout-dialog",
  );
  fab.addEventListener("click", () => {
    addWorkoutDialog.showModal();
  });

  addWorkoutDialog.addEventListener("click", (event) => {
    if ((event.target as HTMLElement).nodeName === "DIALOG") {
      let animation = addWorkoutDialog.animate(
        hideDialogAnimation,
        hideDialogTiming,
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
      hideDialogTiming,
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
      hideDialogTiming,
    );
    animation.addEventListener("finish", () => {
      addWorkoutDialog.close("submit");
      addWorkout();
    });
  });
});

function addWorkout() {
  let addWorkoutDialog: HTMLDialogElement = document.querySelector(
    "#new-workout-dialog",
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

/**
 * Toggle offline status to opposite of current value
 */
function toggleOfflineStatus() {
  let offline = JSON.parse(localStorage.getItem("offline"));
  if (offline) {
    setOfflineStatus(OfflineStatus.ONLINE);
    syncOfflineSets();
  } else {
    setOfflineStatus(OfflineStatus.OFFLINE);
  }
}

/**
 * Set offline status in localStorage to specifiy value
 * Update icon on homepage to match
 * @param {OfflineStatus} mode Selected mode
 */
function setOfflineStatus(mode: OfflineStatus) {
  let btn = document.querySelector("#offline");
  let img = btn.querySelector("img");

  if (mode == OfflineStatus.ONLINE) {
    localStorage.setItem("offline", "false");
    img.src = "/static/img/online.svg";
  } else {
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

/**
 * Convenience function to install service worker
 */
function installServiceWorker() {
  if ("serviceWorker" in navigator) {
    console.log("CLIENT: service worker registration in progress.");
    navigator.serviceWorker.register("/service-worker.js").then(
      function () {
        console.log("CLIENT: service worker registration complete.");
      },
      function () {
        console.log("CLIENT: service worker registration failure.");
      },
    );
  } else {
    console.log("CLIENT: service worker is not supported.");
  }
}
