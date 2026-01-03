document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const btn = document.querySelector("button[type='submit']");

  if (form) {
    form.addEventListener("submit", () => {
      btn.innerHTML = `<span class="spinner"></span> Processing Data...`;
      btn.style.opacity = "0.7";
      btn.style.pointerEvents = "none";
    });
  }
});