export function saveError() {
    let fab = document.querySelector("#fab");
    fab.classList.add("save-error");
    setTimeout(() => {
        fab.classList.remove("save-error");
    }, 2500);
}
export function saveSuccess() {
    let fab = document.querySelector("#fab");
    fab.classList.add("save-success");
    setTimeout(() => {
        fab.classList.remove("save-success");
    }, 2500);
}
