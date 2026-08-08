const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const componentVideos = document.querySelectorAll(".component-media__video");
const turntableVideos = document.querySelectorAll(
  ".component-media__video[data-turntable]",
);

function applyMotionPreference(event) {
  componentVideos.forEach((video) => {
    if (event.matches) {
      video.autoplay = false;
      video.pause();
      video.currentTime = 0;
      return;
    }

    video.autoplay = true;
    video.play().catch(() => {
      // The poster remains visible if a browser declines muted autoplay.
    });
  });
}

applyMotionPreference(reducedMotion);
reducedMotion.addEventListener("change", applyMotionPreference);

function wrapTime(time, duration) {
  return ((time % duration) + duration) % duration;
}

turntableVideos.forEach((video) => {
  let activePointer = null;
  let touchIdentifier = null;
  let touchStartX = 0;
  let touchStartY = 0;
  let touchDragging = false;
  let startX = 0;
  let startTime = 0;
  let pendingTime = 0;
  let seekFrame = null;
  let resumeTimer = null;

  function applyPendingSeek() {
    seekFrame = null;
    if (Number.isFinite(video.duration) && video.duration > 0) {
      video.currentTime = pendingTime;
    }
  }

  function startDrag(clientX) {
    clearTimeout(resumeTimer);
    startX = clientX;
    startTime = video.currentTime;
    pendingTime = startTime;
    video.pause();
    video.classList.add("is-dragging");
  }

  function updateDrag(clientX) {
    const width = Math.max(video.clientWidth, 1);
    const delta = ((clientX - startX) / width) * video.duration;
    pendingTime = wrapTime(startTime + delta, video.duration);
    if (seekFrame === null) {
      seekFrame = requestAnimationFrame(applyPendingSeek);
    }
  }

  function finishDrag() {
    video.classList.remove("is-dragging");
    if (!reducedMotion.matches) {
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(() => {
        video.play().catch(() => {
          // The current frame remains visible if playback is declined.
        });
      }, 400);
    }
  }

  video.addEventListener("pointerdown", (event) => {
    if (
      reducedMotion.matches ||
      !Number.isFinite(video.duration) ||
      video.duration <= 0 ||
      event.pointerType === "touch" ||
      (event.pointerType === "mouse" && event.button !== 0)
    ) {
      return;
    }
    activePointer = event.pointerId;
    startDrag(event.clientX);
    video.setPointerCapture(event.pointerId);
  });

  video.addEventListener(
    "pointermove",
    (event) => {
      if (event.pointerId !== activePointer) {
        return;
      }
      event.preventDefault();
      updateDrag(event.clientX);
    },
    { passive: false },
  );

  function finishPointerDrag(event) {
    if (event.pointerId !== activePointer) {
      return;
    }
    activePointer = null;
    if (video.hasPointerCapture(event.pointerId)) {
      video.releasePointerCapture(event.pointerId);
    }
    finishDrag();
  }

  video.addEventListener("pointerup", finishPointerDrag);
  video.addEventListener("pointercancel", finishPointerDrag);

  video.addEventListener(
    "touchstart",
    (event) => {
      if (
        reducedMotion.matches ||
        touchIdentifier !== null ||
        event.changedTouches.length !== 1 ||
        !Number.isFinite(video.duration) ||
        video.duration <= 0
      ) {
        return;
      }
      const touch = event.changedTouches[0];
      touchIdentifier = touch.identifier;
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      touchDragging = false;
    },
    { passive: true },
  );

  video.addEventListener(
    "touchmove",
    (event) => {
      const touch = Array.from(event.changedTouches).find(
        (item) => item.identifier === touchIdentifier,
      );
      if (!touch) {
        return;
      }

      const deltaX = touch.clientX - touchStartX;
      const deltaY = touch.clientY - touchStartY;
      if (!touchDragging) {
        if (Math.max(Math.abs(deltaX), Math.abs(deltaY)) < 8) {
          return;
        }
        if (Math.abs(deltaY) >= Math.abs(deltaX)) {
          touchIdentifier = null;
          return;
        }
        touchDragging = true;
        startDrag(touchStartX);
      }

      event.preventDefault();
      updateDrag(touch.clientX);
    },
    { passive: false },
  );

  function finishTouchDrag(event) {
    const ended = Array.from(event.changedTouches).some(
      (touch) => touch.identifier === touchIdentifier,
    );
    if (!ended) {
      return;
    }
    touchIdentifier = null;
    if (touchDragging) {
      touchDragging = false;
      finishDrag();
    }
  }

  video.addEventListener("touchend", finishTouchDrag);
  video.addEventListener("touchcancel", finishTouchDrag);
});
