import { saveError, saveSuccess } from "./saveFunctions.js";

const hideDialogAnimation = [{ transform: "translateY(-100%" }];
const hideDialogTiming = {
  duration: 100,
  easing: "ease-out",
};
let timer;
var wakelock = null;

enum WakelockStatus {
  Enable = 1,
  Disable,
}

/**
 * Timer class for time based exercises
 */
class Timer {
  // Store start time from Date.now(), milliseconds
  startTime: number = 0;
  // Store pause time, to continue from if paused, milliseconds
  pauseElapsed: number = 0;
  // Store interval id
  interval: number = null;
  // Timer element
  timerEl: HTMLDivElement;
  // Display element, where we'll show the output
  displayEl: HTMLSpanElement;
  millisEl: HTMLSpanElement;
  // Play pause button element
  playPauseEl: HTMLButtonElement;
  // Wakelock for timer is running;
  wakelock = null;

  /**
   * Initialise timer by getting internal elements and setting counter to 0
   * @param {HTMLDivElement} timerEl Timer element in DOM
   */
  constructor(timerEl: HTMLDivElement) {
    this.timerEl = timerEl;
    this.displayEl = timerEl.querySelector("#timer-display") as HTMLSpanElement;
    this.millisEl = timerEl.querySelector(
      "#timer-display-millis"
    ) as HTMLSpanElement;
    this.playPauseEl = timerEl.querySelector(
      "#timer-start-btn"
    ) as HTMLButtonElement;
  }

  /**
   * Toggle timer start / pause
   */
  toggle() {
    if (this.interval == null) {
      this.startTime = Date.now();
      this.interval = setInterval(this.display.bind(this), 100);
      this.togglePlayPause();
      this.display();
      toggleWakeLock(WakelockStatus.Enable);
    } else {
      this.pauseElapsed = Date.now() - this.startTime + this.pauseElapsed;
      clearInterval(this.interval);
      this.interval = null;
      this.togglePlayPause();
      toggleWakeLock(WakelockStatus.Disable);
    }
  }

  /**
   * Stop and reset timer
   */
  reset() {
    clearInterval(this.interval);
    this.interval = null;
    this.pauseElapsed = 0;

    // Force start icon to play
    let img = this.playPauseEl.querySelector("img");
    img.src = "/static/img/play.svg";
    this.displayEl.innerHTML = "&ndash;&ndash;:&ndash;&ndash;:&ndash;&ndash;";
    this.millisEl.innerHTML = "&ndash;&ndash;&ndash;";

    this.timerEl.classList.remove("paused");
    this.timerEl.classList.remove("running");

    toggleWakeLock(WakelockStatus.Disable);
  }

  /**
   * Convert counter in seconds to readble time and display in displayEl
   */
  display() {
    let elapsedMillis = Date.now() - this.startTime + this.pauseElapsed;
    let elapsedSecs = elapsedMillis / 1000;

    let hours = Math.floor(Math.floor(elapsedSecs) / 3600);
    let minutes = Math.floor((Math.floor(elapsedSecs) % 3600) / 60);
    let seconds = Math.floor(Math.floor(elapsedSecs) % 60);

    // Get milli seconds, but only to 10 ms accuracy, so last digit is always 0
    let millis = (elapsedSecs % 1) * 1000;
    let roundedMillis = Math.ceil(millis / 10) * 10;

    let displayHours = hours < 10 ? "0" + hours : hours.toString();
    let displayMinutes = minutes < 10 ? "0" + minutes : minutes.toString();
    let displaySeconds = seconds < 10 ? "0" + seconds : seconds.toString();

    this.displayEl.innerText =
      displayHours + ":" + displayMinutes + ":" + displaySeconds;
    this.millisEl.innerText = roundedMillis.toString().padStart(3, "0");
  }

  /**
   * Toggle img on play / pause button
   */
  togglePlayPause() {
    let img = this.playPauseEl.querySelector("img");
    if (img.src.endsWith("play.svg")) {
      img.src = "/static/img/pause.svg";
      this.timerEl.classList.remove("paused");
      this.timerEl.classList.add("running");
    } else {
      img.src = "/static/img/play.svg";
      this.timerEl.classList.add("paused");
      this.timerEl.classList.remove("running");
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  let fab: HTMLButtonElement = document.querySelector(
    "#fab"
  ) as HTMLButtonElement;

  let graphBtn: HTMLDivElement = document.querySelector(
    "#graph-button"
  ) as HTMLDivElement;
  let graphSection: HTMLElement = document.querySelector(
    "#graph"
  ) as HTMLElement;
  graphBtn.addEventListener("click", () => {
    if (graphSection.classList.contains("hidden")) {
      graphSection.classList.remove("hidden");
    } else {
      graphSection.style.transform = "";
      graphSection.classList.add("hidden");
    }
  });
  // Add event listener for swiping up to close graph drop down
  graphSection.addEventListener("touchstart", swipeCloseGraph);

  // When selecting the new set input
  let newSetInputs: NodeListOf<HTMLInputElement> =
    document.querySelectorAll("#new-set input");
  newSetInputs.forEach((el) => {
    el.addEventListener("click", (e) => {
      (e.target as HTMLInputElement).select();
    });
  });

  let editSetInputs: NodeListOf<HTMLInputElement> = document.querySelectorAll(
    "#edit-set-dialog input"
  );
  editSetInputs.forEach((el) => {
    el.addEventListener("click", (e) => {
      (e.target as HTMLInputElement).select();
    });
  });

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

  // Timer element for time-based exercises
  // Only initialise and add event listeners if it's on the exercise page
  let timerEl: HTMLDivElement = document.querySelector(".timer");
  if (timerEl != null) {
    timer = new Timer(timerEl);
    let timerStartBtn: HTMLButtonElement =
      document.querySelector("#timer-start-btn");
    timerStartBtn.addEventListener("click", () => {
      timer.toggle();
    });
    let timerStopBtn: HTMLButtonElement =
      document.querySelector("#timer-stop-btn");
    timerStopBtn.addEventListener("click", () => {
      timer.reset();
    });
  }
});
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

/**
 * Event handler for touch events to swipe up to close graph
 * @param {TouchEvent} e Touchstart event
 */
function swipeCloseGraph(e: TouchEvent) {
  if (
    (e.changedTouches[0].target as HTMLElement).closest(".graph-wrapper") !=
    null
  ) {
    // If the closest table element is not null, then it means we've touched the graph.
    // Therefore, abort this event listener so we can scroll the graph horizontally without
    // this event listener capturing the touch events
    return;
  }

  e.preventDefault();

  // e.changedTouches should only have a single item
  // Get the y position on the page from that item
  let startY = e.changedTouches[0].pageY;
  let currentY = startY;

  // Add a touchmove and touchend events to the graph element
  let graph: HTMLElement = (e.changedTouches[0].target as HTMLElement).closest(
    "#graph"
  );
  // Remove animation on touchstart event so it doesn't make the touch iteraction laggy.
  // We'll restore it when closing the graph
  graph.classList.remove("animate");

  this.swipeMove = function (e: TouchEvent) {
    let endY = e.changedTouches[0].pageY;
    // Don't allow translate to move graph section down
    let translate = Math.min(0, -(startY - endY));
    let transform = "translateY(" + translate + "px)";
    graph.style.transform = transform;
  };

  this.swipeEnd = function (e: TouchEvent) {
    let endY = e.changedTouches[0].pageY;
    // Remove any element style transform so that if we don't move far enough to close
    // the graph, it returns to fully open
    graph.style.transform = "";
    // Restore animation
    graph.classList.add("animate");
    // If the delta between startY and endY is large enough, add the "hidden" class
    // to trigger the close animation
    if (startY - endY > 100) {
      graph.classList.add("hidden");
    }
    // Remove the touchend and touchmove event listeners to avoid adding a new one
    // everytime a touchstart event is fired.
    graph.removeEventListener("touchmove", this.swipeMove);
    graph.removeEventListener("touchend", this.swipeEnd);
  };

  graph.addEventListener("touchmove", this.swipeMove);
  graph.addEventListener("touchend", this.swipeEnd);
}

/**
 * Toggle wakelock when checkbox state changes
 */
async function toggleWakeLock(status: WakelockStatus) {
  if (status == WakelockStatus.Enable && wakelock == null) {
    try {
      wakelock = await navigator.wakeLock.request("screen");
    } catch (err) {
      console.log(`Wakelock failed: ${err.message}`);
    }
  } else if (status == WakelockStatus.Disable && wakelock != null) {
    // Release wakelock and set variable back to null
    wakelock.release().then(() => (wakelock = null));
  }
}
