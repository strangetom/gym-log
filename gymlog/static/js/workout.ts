document.addEventListener("DOMContentLoaded", () => {
  let exercises: NodeListOf<HTMLAnchorElement> =
    document.querySelectorAll("a.exercise-card");
  let offlineSets = JSON.parse(localStorage.getItem("offline-sets")) || [];
  exercises.forEach((el) => {
    let exerciseID = el.dataset.exerciseid;
    let count = offlineSets.filter((s) => {
      return s.exerciseID == exerciseID;
    }).length;
    if (count > 0) {
      el.querySelector("img.offline").classList.remove("hidden");
    }
  });
});
