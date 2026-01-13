// enhanced carousel: centered controls, dots, keyboard nav, auto-advance
document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".carousel");
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll(".carousel .slide"));
  const prevBtn = carousel.querySelector(".carousel-prev");
  const nextBtn = carousel.querySelector(".carousel-next");
  const dotsContainer = carousel.querySelector(".carousel-dots");

  let idx = 0;
  const show = (i) => {
    slides.forEach((s, j) => { s.style.display = j === i ? "block" : "none"; });
    const dots = Array.from(dotsContainer.children);
    dots.forEach((d, j) => d.classList.toggle("active", j === i));
  };

  // build dots
  slides.forEach((s, i) => {
    const btn = document.createElement("button");
    btn.className = "dot";
    btn.setAttribute("aria-label", "Slide " + (i + 1));
    btn.addEventListener("click", () => { idx = i; show(idx); });
    dotsContainer.appendChild(btn);
  });

  // initial state
  show(idx);

  // controls
  nextBtn?.addEventListener("click", () => { idx = (idx + 1) % slides.length; show(idx); });
  prevBtn?.addEventListener("click", () => { idx = (idx - 1 + slides.length) % slides.length; show(idx); });

  // keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") nextBtn?.click();
    if (e.key === "ArrowLeft") prevBtn?.click();
  });

  // auto advance
  let timer = setInterval(() => { idx = (idx + 1) % slides.length; show(idx); }, 6000);
  // pause on hover
  carousel.addEventListener("mouseenter", () => clearInterval(timer));
  carousel.addEventListener("mouseleave", () => { timer = setInterval(() => { idx = (idx + 1) % slides.length; show(idx); }, 6000); });
});