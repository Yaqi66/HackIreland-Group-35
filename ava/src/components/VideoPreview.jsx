import { useEffect, useRef } from 'react';

function VideoPreview({ stream }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  if (!stream) return null;

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="video-preview"
    />
  );
}

export default VideoPreview;
