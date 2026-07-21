const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const componentVideos = document.querySelectorAll(".component-media__video");

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
