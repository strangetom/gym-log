export class Offline {
  constructor() {
    let offlineCache = localStorage.getItem("offline");
    if (offlineCache == null) {
      localStorage.setItem("offline", JSON.stringify([]));
    }
  }

  addSetToCache(setData) {
    let offlineCache = JSON.parse(localStorage.getItem("offline"));
    offlineCache.push(setData);
    localStorage.setItem("offline", JSON.stringify(offlineCache));
  }

  getOfflineSets(exerciseID: number) {
    let offlineCache = JSON.parse(localStorage.getItem("offline"));
    return offlineCache.filter((set) => set.exerciseID == exerciseID);
  }

  getAllOfflineSets() {
    let offlineCache = JSON.parse(localStorage.getItem("offline"));
    return offlineCache;
  }
}
