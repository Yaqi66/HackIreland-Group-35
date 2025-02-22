export const processVideoStream = (stream, targetHeight = 480) => {
  return new Promise((resolve) => {
    const videoTrack = stream.getVideoTracks()[0];
    const { width, height } = videoTrack.getSettings();
    
    // Calculate new width maintaining aspect ratio
    const aspectRatio = width / height;
    const targetWidth = Math.round(targetHeight * aspectRatio);

    // Create video element for processing
    const videoElement = document.createElement('video');
    videoElement.srcObject = new MediaStream([videoTrack]);
    videoElement.autoplay = true;

    // Create canvas for resizing
    const canvas = document.createElement('canvas');
    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext('2d');

    // Process video frame
    const processFrame = () => {
      ctx.drawImage(videoElement, 0, 0, targetWidth, targetHeight);
      canvas.captureStream(5).getVideoTracks().forEach(track => {
        // Set frame rate constraint on the track
        track.applyConstraints({ frameRate: 5 });
        stream.addTrack(track);
      });
      resolve(stream);
    };

    videoElement.onplay = () => {
      // Wait a frame to ensure video is ready
      requestAnimationFrame(processFrame);
    };
  });
};

export const getOptimalVideoConstraints = (targetHeight = 480) => {
  return {
    width: { ideal: 1280 },
    height: { ideal: targetHeight },
    frameRate: { exact: 5 }, // Limit to 5 fps
    aspectRatio: { ideal: 16/9 }
  };
};
