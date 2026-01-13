// very small carousel behavior
document.addEventListener("DOMContentLoaded", function () {
  const slides = document.querySelectorAll(".carousel .slide");
  if (!slides.length) return;
  let idx = 0;
  slides.forEach((s, i) => s.style.display = i === 0 ? "block" : "none");
  function show(i) {
    slides.forEach((s, j) => s.style.display = j === i ? "block" : "none");
  }
  document.querySelector(".carousel-next")?.addEventListener("click", () => { idx = (idx + 1) % slides.length; show(idx); });
  document.querySelector(".carousel-prev")?.addEventListener("click", () => { idx = (idx - 1 + slides.length) % slides.length; show(idx); });
  // auto-advance
  setInterval(() => { idx = (idx + 1) % slides.length; show(idx); }, 6000);
});