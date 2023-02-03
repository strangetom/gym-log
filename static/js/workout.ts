document.addEventListener("DOMContentLoaded", () => {
  let deleteBtn: HTMLButtonElement = document.querySelector(
    "#fab-delete"
  ) as HTMLButtonElement;
  deleteBtn.addEventListener("click", () => {
    let workoutID: string = (
      document.querySelector("#workoutID") as HTMLInputElement
    ).value;
    if (confirm("Are you sure you want to delete this workout?")) {
      let postData = new FormData();
      postData.append("workoutID", workoutID);
      fetch("/save-workout", {
        method: "DELETE",
        body: postData,
      }).then((res) => {
        if (res.ok) {
          window.location.href = "/";
        }
      });
    }
  });
});
