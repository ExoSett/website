// Section links remain in the HTML; JavaScript supplies the optional submenus.
const navigationMenus = {
  Components: [
    ["Accommodation module", "/components/accommodation-module/"],
    ["Accommodation frame", "/components/accommodation-frame/"],
    ["Service frame", "/components/service-frame/"],
    ["Cell", "/components/cell/"],
    ["Frame node", "/components/frame-node/"],
    ["All components", "/components/"],
  ],
  Design: [
    ["Sketch", "/design/sketch/"],
    ["Project roles", "/design/#roles-heading"],
    ["Accommodation design", "/design/accommodation-design/"],
    ["Location", "/design/location/"],
    ["Fire safety", "/design/fire-safety/"],
    ["Design overview", "/design/"],
  ],
  Stories: [
    ["Retirement living", "/stories/retirement-living/"],
    ["The First-Time Buyer", "/stories/the-first-time-buyer/"],
    ["Almost Home", "/stories/almost-home/"],
    ["Event accommodation", "/stories/event-accommodation/"],
    ["The old prison", "/stories/the-old-prison/"],
    ["The evolving hotel", "/stories/evolving-hotel/"],
    ["All stories", "/stories/"],
  ],
  About: [
    ["Why are we here?", "/about/"],
    ["Research and Reading", "/about/research-and-reading/"],
    [
      "ExoSett and conventional modular construction",
      "/about/exosett-and-conventional-modular-construction/",
    ],
    ["Discuss ExoSett", "/about/#contact-heading"],
  ],
};

document.querySelectorAll(".site-nav").forEach((nav) => {
  nav.querySelectorAll(".site-nav__section-link").forEach((sectionLink) => {
    const entries = navigationMenus[sectionLink.textContent.trim()];
    if (!entries) return;
    const item = sectionLink.closest(".site-nav__item");
    if (item.querySelector("details")) return;
    const details = document.createElement("details");
    details.className = "site-nav__disclosure";
    const summary = document.createElement("summary");
    const label = document.createElement("span");
    label.className = "visually-hidden";
    label.textContent = `${sectionLink.textContent.trim()} submenu`;
    const chevron = document.createElement("span");
    chevron.className = "site-nav__chevron";
    chevron.setAttribute("aria-hidden", "true");
    summary.append(label, chevron);
    const list = document.createElement("ul");
    list.className = "site-nav__submenu";
    list.id = `nav-${sectionLink.textContent.trim().toLowerCase()}`;
    summary.setAttribute("aria-controls", list.id);
    const currentPath = window.location.pathname.replace(/index\.html$/, "");
    entries.forEach(([title, href]) => {
      const entry = document.createElement("li");
      const link = document.createElement("a");
      link.href = href;
      link.textContent = title;
      if (href === currentPath) link.setAttribute("aria-current", "page");
      entry.append(link);
      list.append(entry);
    });
    details.append(summary, list);
    item.append(details);
  });
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
