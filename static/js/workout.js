document.addEventListener("DOMContentLoaded", () => {
    let deleteBtn = document.querySelector("#fab-delete");
    deleteBtn.addEventListener("click", () => {
        let workoutID = document.querySelector("#workoutID").value;
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
