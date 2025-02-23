import { useState, useEffect } from "react";
import "./App.css";
import Avatar from "./components/Avatar";
import VideoPreview from "./components/VideoPreview";
import AudioWave from "./components/AudioWave";
import useStore from "./store/useStore";
import { useSupabase } from "./hooks/useSupabase";
import AuthModal from "./components/AuthModal";
import useWakeWordRecorder from "./hooks/useWakeWordRecorder";
import ImagesPreview from "./components/ImagesPreview";
import YoutubePreview from "./components/YoutubePreview";
import ImageCarouselModal from "./components/ImageCarouselModal";
import YoutubeModal from "./components/YoutubeModal";
import NewsPreview from "./components/NewsPreview";
import NewsModal from "./components/NewsModal";

function App() {
  const { isAwake, isListening, activeYoutubeUrl, setActiveYoutubeUrl, isYoutubeModalOpen, setIsYoutubeModalOpen, setNewsArticles, isNewsModalOpen, setIsNewsModalOpen } = useStore();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isImageCarouselModalOpen, setIsImageCarouselModalOpen] = useState(false);
  const { user, signOut } = useSupabase();
  const { startWakeWordRecording, stopRecording } = useWakeWordRecorder();

  useEffect(() => {
    // Only show modal if user is explicitly null (not undefined)
    if (user === null) {
      setShowAuthModal(true);
    } else if (user) {
      setShowAuthModal(false);
    }
  }, [user]);

  // Start wake word detection when awake
  useEffect(() => {
    if (isAwake && user && !isListening) {
      startWakeWordRecording();
    } else {
      stopRecording();
    }
  }, [isAwake, user, startWakeWordRecording, stopRecording, isListening]);

  useEffect(() => {
    // Fetch news articles on mount
    const fetchNews = async () => {
      try {
        const response = await fetch('http://172.16.6.104:5000/api/news');
        if (!response.ok) throw new Error('Failed to fetch news');
        const articles = await response.json();
        setNewsArticles(articles);
      } catch (error) {
        console.error('Error fetching news:', error);
      }
    };

    fetchNews();
  }, [setNewsArticles]);

  return (
    <div className={`app-container ${isAwake ? "listening" : "not-listening"}`}>
      {user && (
        <button className="sign-out-button" onClick={signOut}>
          Sign Out
        </button>
      )}
      <div className="left-container horizontal-container">
        <div className="top-container left-top corner vertical-container">
          <div 
            className={`suggestion-box top-left ${isAwake ? "show" : ""}`}
            onClick={() => setIsImageCarouselModalOpen(true)}
          >
            <ImagesPreview />
          </div>
        </div>
        <div className="center-container left-center vertical-container"></div>
        <div className="bottom-container left-bottom corner vertical-container">
          <div 
            className={`suggestion-box bottom-left ${isAwake ? "show" : ""}`}
            onClick={() => {
              setActiveYoutubeUrl("https://www.youtube.com/watch?v=fmg-Ks83Jy0");
              setIsYoutubeModalOpen(true);
            }}
          >
            <YoutubePreview url="https://www.youtube.com/watch?v=fmg-Ks83Jy0" />
          </div>
        </div>
      </div>
      <div className="middle-container horizontal-container">
        <div className="top-container middle-top vertical-container"></div>
        <div className="center-container middle-center vertical-container center">
          <Avatar />
          {/* <div className={`audio-wave ${isAwake ? 'active' : ''}`}>
            <AudioWave isListening={isAwake} />
          </div> */}
        </div>
        <div className="bottom-container middle-bottom vertical-container"></div>
      </div>
      <div className="right-container horizontal-container">
        <div className="top-container right-top corner vertical-container">
          <div 
            className={`suggestion-box top-right ${isAwake ? "show" : ""}`}
            onClick={() => {
              setActiveYoutubeUrl("https://www.youtube.com/watch?v=qQzdAsjWGPg");
              setIsYoutubeModalOpen(true);
            }}
          >
            <YoutubePreview url="https://www.youtube.com/watch?v=qQzdAsjWGPg" />
          </div>
        </div>
        <div className="center-container right-center vertical-container"></div>
        <div className="bottom-container right-bottom corner vertical-container">
          <div 
            className={`suggestion-box bottom-right ${isAwake ? "show" : ""}`}
            onClick={() => setIsNewsModalOpen(true)}
          >
            <NewsPreview />
          </div>
        </div>
      </div>
      <ImageCarouselModal 
        isOpen={isImageCarouselModalOpen}
        onClose={() => setIsImageCarouselModalOpen(false)}
      />
      <YoutubeModal
        isOpen={isYoutubeModalOpen}
        onClose={() => setIsYoutubeModalOpen(false)}
        videoUrl={activeYoutubeUrl}
      />
      <NewsModal
        isOpen={isNewsModalOpen}
        onClose={() => setIsNewsModalOpen(false)}
      />
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => user && setShowAuthModal(false)}
      />
    </div>
  );
}

export default App;
