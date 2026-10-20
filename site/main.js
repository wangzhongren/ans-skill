/* Progressive enhancement only: all content and commands remain in HTML. */
"use strict";
document.querySelectorAll("[data-copy]").forEach(function (button) {
  button.hidden = false;
  button.addEventListener("click", async function () {
    const command = document.getElementById(button.dataset.copy);
    const status = document.getElementById(button.getAttribute("aria-describedby"));
    status.textContent = "";
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        throw new Error("Clipboard API unavailable");
      }
      await navigator.clipboard.writeText(command.textContent);
      status.textContent = button.dataset.success;
    } catch (error) {
      console.info("Copy unavailable; select the command to copy manually.", error.name);
      status.textContent = button.dataset.failure;
    }
  });
});
