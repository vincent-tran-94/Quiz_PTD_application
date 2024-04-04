var videos = document.querySelectorAll('.video video');
    
        videos.forEach(function(video) {
            video.addEventListener('play', function() {
                pauseOtherVideos(video);
            });
        });
    
        function pauseOtherVideos(currentVideo) {
            videos.forEach(function(video) {
                if (video !== currentVideo && !video.paused) {
                    video.pause();
                }
            });
}