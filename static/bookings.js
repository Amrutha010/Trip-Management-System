// lightweight modal handling for booking modal
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("booking-modal");
  const modalClose = document.getElementById("booking-modal-close");
  const openButtons = document.querySelectorAll(".open-book-modal");
  const modalTitle = document.getElementById("modal-trip-title");
  const modalMeta = document.getElementById("modal-trip-meta");
  const modalTripId = document.getElementById("modal-trip-id");
  const form = document.getElementById("booking-modal-form");

  function openModalForTrip(el) {
    // find parent card to pull trip data attributes
    const card = el.closest(".card");
    const tripId = el.getAttribute("data-trip-id") || card.getAttribute("data-trip-id");
    const title = card.getAttribute("data-trip-title") || card.querySelector(".title").textContent.trim();
    const destination = card.getAttribute("data-trip-destination") || "";
    const date = card.getAttribute("data-trip-date") || "";
    modalTitle.textContent = "Book: " + title;
    modalMeta.textContent = (destination ? destination + " • " : "") + (date || "");
    modalTripId.value = tripId;
    modal.style.display = "block";
    modal.setAttribute("aria-hidden", "false");
    // prefill name if logged-in info available via data-current-user in DOM? (not implemented)
  }

  openButtons.forEach(btn => {
    btn.addEventListener("click", function (e) {
      openModalForTrip(btn);
    });
  });

  modalClose && modalClose.addEventListener("click", function () {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
  });

  // close by clicking outside content
  window.addEventListener("click", function (e) {
    if (!modal) return;
    if (e.target === modal) {
      modal.style.display = "none";
      modal.setAttribute("aria-hidden", "true");
    }
  });
});