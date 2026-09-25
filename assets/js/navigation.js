// Native disclosures remain usable when JavaScript is unavailable.
document.querySelectorAll(".site-nav").forEach((nav) => {
  const disclosures = [...nav.querySelectorAll("details")];
  const hover = window.matchMedia(
    "(hover: hover) and (pointer: fine) and (min-width: 48.0625rem)",
  );
  const close = (except) =>
    disclosures.forEach((item) => {
      if (item !== except) item.open = false;
    });

  disclosures.forEach((details) => {
    const summary = details.querySelector("summary");
    const item = details.closest(".site-nav__item");
    let hoverOpened = false;
    let dismissed = false;
    details.addEventListener("toggle", () => {
      if (details.open) close(details);
    });
    summary.addEventListener("click", (event) => {
      // Clicking a disclosure just opened by hover pins it open.
      if (hoverOpened && details.open) {
        event.preventDefault();
        hoverOpened = false;
        return;
      }
      dismissed = details.open;
      hoverOpened = false;
      if (!details.open) close(details);
    });
    item.addEventListener("pointerenter", () => {
      if (hover.matches && !dismissed && !details.open) {
        close(details);
        details.open = true;
        hoverOpened = true;
      }
    });
    item.addEventListener("pointerleave", () => {
      dismissed = false;
      if (hoverOpened && !item.contains(document.activeElement))
        details.open = false;
      hoverOpened = false;
    });
    item.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && details.open) {
        event.preventDefault();
        details.open = false;
        dismissed = true;
        hoverOpened = false;
        summary.focus();
      }
    });
  });
  nav.addEventListener("focusout", (event) => {
    if (!nav.contains(event.relatedTarget)) close();
    else
      disclosures.forEach((details) => {
        if (!details.closest(".site-nav__item").contains(event.relatedTarget))
          details.open = false;
      });
  });
  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target)) close();
  });
  hover.addEventListener("change", () => close());
});
