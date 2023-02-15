export function saveError(id) {
  let fab: HTMLButtonElement = document.querySelector(id) as HTMLButtonElement;
  fab.classList.add("save-error");
  setTimeout(() => {
    fab.classList.remove("save-error");
  }, 2500);
}

export function saveSuccess(id) {
  let fab: HTMLButtonElement = document.querySelector(id) as HTMLButtonElement;
  fab.classList.add("save-success");
  setTimeout(() => {
    fab.classList.remove("save-success");
  }, 2500);
}
