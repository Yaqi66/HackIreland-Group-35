import { useEffect, useRef } from "react";

function VideoPreview({ stream }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  if (!stream) return null;

  return (
    <div className="video-preview-container">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="video-preview"
      />
      <div className="video-interactive-cover"></div>
    </div>
  );
}

export default VideoPreview;
