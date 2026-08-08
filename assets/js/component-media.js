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

  function finishDrag(event) {
    if (event.pointerId !== activePointer) {
      return;
    }
    activePointer = null;
    video.classList.remove("is-dragging");
    if (video.hasPointerCapture(event.pointerId)) {
      video.releasePointerCapture(event.pointerId);
    }
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
      (event.pointerType === "mouse" && event.button !== 0)
    ) {
      return;
    }
    clearTimeout(resumeTimer);
    activePointer = event.pointerId;
    startX = event.clientX;
    startTime = video.currentTime;
    pendingTime = startTime;
    video.pause();
    video.setPointerCapture(event.pointerId);
    video.classList.add("is-dragging");
  });

  video.addEventListener(
    "pointermove",
    (event) => {
      if (event.pointerId !== activePointer) {
        return;
      }
      event.preventDefault();
      const width = Math.max(video.clientWidth, 1);
      const delta = ((event.clientX - startX) / width) * video.duration;
      pendingTime = wrapTime(startTime + delta, video.duration);
      if (seekFrame === null) {
        seekFrame = requestAnimationFrame(applyPendingSeek);
      }
    },
    { passive: false },
  );

  video.addEventListener("pointerup", finishDrag);
  video.addEventListener("pointercancel", finishDrag);
});
