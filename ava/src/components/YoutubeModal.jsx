import React, { useState, useEffect } from 'react';
import '../styles/YoutubeModal.css';

const YoutubeModal = ({ isOpen, onClose, videoUrl }) => {
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
    } else {
      const timer = setTimeout(() => setShouldRender(false), 300); // match animation duration
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!shouldRender || !videoUrl) return null;

  // Extract video ID from YouTube URL
  const getVideoId = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  };

  const videoId = getVideoId(videoUrl);

  if (!videoId) {
    return null;
  }

  return (
    <div className={`modal-overlay ${isOpen ? 'modal-show' : 'modal-hide'}`}>
      <div className={`modal-content youtube-modal ${isOpen ? 'modal-show' : 'modal-hide'}`}>
        <button className="modal-close" onClick={onClose}>×</button>
        <div className="youtube-container">
          <iframe
            src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0&enablejsapi=1&rel=0`}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="youtube-iframe"
          />
        </div>
      </div>
    </div>
  );
};

export default YoutubeModal;
