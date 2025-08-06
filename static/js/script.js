const container = document.querySelector(".container"),
  mainVideo = container.querySelector("video"),
  videoTimeline = container.querySelector(".video-timeline"),
  progressBar = container.querySelector(".progress-bar"),
  volumeBtn = container.querySelector(".volume i"),
  volumeSlider = container.querySelector(".left input[type='range']");
  currentVidTime = container.querySelector(".current-time"),
  videoDuration = container.querySelector(".video-duration"),
  skipBackward = container.querySelector(".skip-backward i"),
  skipForward = container.querySelector(".skip-forward i"),
  playPauseBtn = container.querySelector(".play-pause i"),
  speedBtn = container.querySelector(".playback-speed span"),
  speedOptions = container.querySelector(".speed-options"),
  pipBtn = container.querySelector(".pic-in-pic span"),
  fullScreenBtn = container.querySelector(".fullscreen i");
let timer;

// --- Playlist variables ---
let videoPlaylist = [];
let currentVideoIndex = 0;
let currentVideoUrl = ''; // Keep track of the current video's URL for capturing

// --- Loading Overlay Elements ---
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// --- Helper function to show/hide the loading overlay ---
function showLoading(message) {
  loadingText.textContent = message;
  loadingOverlay.classList.add('show');
}

function hideLoading() {
  loadingOverlay.classList.remove('show');
}

const hideControls = () => {
    if(mainVideo.paused) return;
    timer = setTimeout(() => {
        container.classList.remove("show-controls");
    }, 3000);
}
hideControls();

container.addEventListener("mousemove", () => {
    container.classList.add("show-controls");
    clearTimeout(timer);
    hideControls();   
});

const formatTime = time => {
    let seconds = Math.floor(time % 60),
    minutes = Math.floor(time / 60) % 60,
    hours = Math.floor(time / 3600);

    seconds = seconds < 10 ? `0${seconds}` : seconds;
    minutes = minutes < 10 ? `0${minutes}` : minutes;
    hours = hours < 10 ? `0${hours}` : hours;

    if(hours == 0) {
        return `${minutes}:${seconds}`
    }
    return `${hours}:${minutes}:${seconds}`;
}

videoTimeline.addEventListener("mousemove", e => {
    let timelineWidth = videoTimeline.clientWidth;
    let offsetX = e.offsetX;
    let percent = Math.floor((offsetX / timelineWidth) * mainVideo.duration);
    const progressTime = videoTimeline.querySelector("span");
    offsetX = offsetX < 20 ? 20 : (offsetX > timelineWidth - 20) ? timelineWidth - 20 : offsetX;
    progressTime.style.left = `${offsetX}px`;
    progressTime.innerText = formatTime(percent);
});

videoTimeline.addEventListener("click", e => {
    let timelineWidth = videoTimeline.clientWidth;
    mainVideo.currentTime = (e.offsetX / timelineWidth) * mainVideo.duration;
});

mainVideo.addEventListener("timeupdate", e => {
    let {currentTime, duration} = e.target;
    let percent = (currentTime / duration) * 100;
    progressBar.style.width = `${percent}%`;
    currentVidTime.innerText = formatTime(currentTime);
});

mainVideo.addEventListener("loadeddata", () => {
    videoDuration.innerText = formatTime(mainVideo.duration);
});

mainVideo.addEventListener('ended', playNextVideo);

const draggableProgressBar = e => {
    let timelineWidth = videoTimeline.clientWidth;
    progressBar.style.width = `${e.offsetX}px`;
    mainVideo.currentTime = (e.offsetX / timelineWidth) * mainVideo.duration;
    currentVidTime.innerText = formatTime(mainVideo.currentTime);
}

volumeBtn.addEventListener("click", () => {
    if(!volumeBtn.classList.contains("fa-volume-high")) {
        mainVideo.volume = 0.5;
        volumeBtn.classList.replace("fa-volume-xmark", "fa-volume-high");
    } else {
        mainVideo.volume = 0.0;
        volumeBtn.classList.replace("fa-volume-high", "fa-volume-xmark");
    }
    volumeSlider.value = mainVideo.volume;
});

volumeSlider.addEventListener("input", e => {
    mainVideo.volume = e.target.value;
    if(e.target.value == 0) {
        return volumeBtn.classList.replace("fa-volume-high", "fa-volume-xmark");
    }
    volumeBtn.classList.replace("fa-volume-xmark", "fa-volume-high");
});

speedOptions.querySelectorAll("li").forEach(option => {
    option.addEventListener("click", () => {
        mainVideo.playbackRate = option.dataset.speed;
        speedOptions.querySelector(".active").classList.remove("active");
        option.classList.add("active");
    });
});

document.addEventListener("click", e => {
    if(e.target.tagName !== "SPAN" || e.target.className !== "material-symbols-rounded") {
        speedOptions.classList.remove("show");
    }
});

fullScreenBtn.addEventListener("click", () => {
    container.classList.toggle("fullscreen");
    if(document.fullscreenElement) {
        fullScreenBtn.classList.replace("fa-compress", "fa-expand");
        return document.exitFullscreen();
    }
    fullScreenBtn.classList.replace("fa-expand", "fa-compress");
    container.requestFullscreen();
});

speedBtn.addEventListener("click", () => speedOptions.classList.toggle("show"));
pipBtn.addEventListener("click", () => mainVideo.requestPictureInPicture());
skipBackward.addEventListener("click", () => mainVideo.currentTime -= 5);
skipForward.addEventListener("click", () => mainVideo.currentTime += 5);
mainVideo.addEventListener("play", () => playPauseBtn.classList.replace("fa-play", "fa-pause"));
mainVideo.addEventListener("pause", () => playPauseBtn.classList.replace("fa-pause", "fa-play"));
playPauseBtn.addEventListener("click", () => mainVideo.paused ? mainVideo.play() : mainVideo.pause());
videoTimeline.addEventListener("mousedown", () => videoTimeline.addEventListener("mousemove", draggableProgressBar));
document.addEventListener("mouseup", () => videoTimeline.removeEventListener("mousemove", draggableProgressBar));

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    showLoading('Uploading your video, please wait...');

    const formData = new FormData();
    formData.append('video', document.getElementById('video').files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        console.log('Upload successful:', data.video_url);
        fetchAndLoadVideos(data.video_url);
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
        alert('Upload failed. Please try again.');
    });
});

document.getElementById('play-existing-video').addEventListener('click', function() {
    if (mainVideo.paused) {
        mainVideo.play();
    } else {
        mainVideo.pause();
    }
});

function loadVideo(videoUrl) {
    if (!videoUrl) return;
    const videoSource = document.getElementById('video-source');
    videoSource.src = videoUrl;
    currentVideoUrl = videoUrl;
    mainVideo.load();
    // We don't autoplay here to respect browser policies. User clicks play.
}

function playNextVideo() {
    if (videoPlaylist.length === 0) return;
    currentVideoIndex = (currentVideoIndex + 1) % videoPlaylist.length;
    const nextVideoUrl = videoPlaylist[currentVideoIndex];
    loadVideo(nextVideoUrl);
    mainVideo.play(); // Autoplay the next video in the sequence
}

document.getElementById('next-video').addEventListener('click', playNextVideo);

async function fetchAndLoadVideos(playThisUrlAfterwards = null) {
    try {
        const response = await fetch('/get_videos');
        videoPlaylist = await response.json();

        if (videoPlaylist.length > 0) {
            if (playThisUrlAfterwards) {
                const newVideoIndex = videoPlaylist.findIndex(url => url === playThisUrlAfterwards);
                currentVideoIndex = newVideoIndex !== -1 ? newVideoIndex : 0;
            }
            loadVideo(videoPlaylist[currentVideoIndex]);
        } else {
            console.log("No videos found in the uploads folder.");
        }
    } catch (error) {
        console.error('Error fetching video list:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchAndLoadVideos();

    const videoPlayer = document.getElementById('video-player');
    const captureButton = document.getElementById('capture-button');
    const sidebar = document.querySelector('.sidebar');
    const productList = document.getElementById('product-list');
    const closeButton = document.getElementById('close-button');

    captureButton.addEventListener('click', function() {
        document.body.style.cursor = 'crosshair';
        videoPlayer.addEventListener('click', captureCoordinates, { once: true });
    });

    function captureCoordinates(event) {
        document.body.style.cursor = 'default';
        const rect = videoPlayer.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const timestamp = videoPlayer.currentTime;
        const data = {
            x: x,
            y: y,
            timestamp: timestamp,
            filename: currentVideoUrl
        };

        showLoading('Fetching similar products...');

        fetch('/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            populateProductList(data.products);
            hideLoading();
            showSidebar();
        })
        .catch(error => {
            console.error('Error:', error);
            hideLoading();
            alert('Could not find products. Please try again.');
        });
    }

    function populateProductList(products) {
        productList.innerHTML = '';

        if (!products || products.length === 0) {
            productList.innerHTML = '<li>No products found.</li>';
            return;
        }

        const productsToShow = products.slice(0, 4);

        productsToShow.forEach(product => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = product.link;
            link.target = '_blank';

            const img = document.createElement('img');
            img.src = product.image;
            img.alt = product.name;

            link.appendChild(img);
            listItem.appendChild(link);
            productList.appendChild(listItem);
        });
    }

    function showSidebar() {
        sidebar.classList.add('show');
    }

    function hideSidebar() {
        sidebar.classList.remove('show');
    }

    closeButton.addEventListener('click', hideSidebar);
});
