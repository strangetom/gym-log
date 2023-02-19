const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
    duration: 100,
    easing: "ease-out",
};
document.addEventListener("DOMContentLoaded", () => {
    installServiceWorker();
    let fab = document.querySelector("#fab");
    let addWorkoutDialog = document.querySelector("#new-workout-dialog");
    fab.addEventListener("click", () => {
        addWorkoutDialog.showModal();
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
function installServiceWorker() {
    if ("serviceWorker" in navigator) {
        console.log("CLIENT: service worker registration in progress.");
        navigator.serviceWorker.register("/service-worker.min.js").then(function () {
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
