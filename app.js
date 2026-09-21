if ("serviceWorker" in navigator) {
  window.addEventListener("load", async () => {
    try {
      await navigator.serviceWorker.register("./sw.js");

      const sendStatusRequest = () => {
        if (navigator.serviceWorker.controller) {
          navigator.serviceWorker.controller.postMessage({
            type: "GET_OFFLINE_STATUS"
          });
        }
      };

      navigator.serviceWorker.addEventListener("message", event => {
        if (event.data && event.data.type === "OFFLINE_READY") {
          const status = document.getElementById("offline-status");

          if (status) {
            status.textContent = "✓ Offline Ready";
            status.classList.add("ready");
            status.setAttribute(
              "aria-label",
              "Complete tour cached for offline use"
            );
          }
        }
      });

      await navigator.serviceWorker.ready;
      sendStatusRequest();

    } catch (error) {
      console.warn(
        "Elephanta Guide service worker registration failed:",
        error
      );
    }
  });
}
