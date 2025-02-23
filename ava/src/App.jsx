import { useState, useEffect } from "react";
import "./App.css";
import Avatar from "./components/Avatar";
import VideoPreview from "./components/VideoPreview";
import AudioWave from "./components/AudioWave";
import useStore from "./store/useStore";
import { useSupabase } from "./hooks/useSupabase";
import AuthModal from "./components/AuthModal";
import PatientList from "./components/PatientList";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Link,
  Navigate,
} from "react-router-dom";
import useWakeWordRecorder from "./hooks/useWakeWordRecorder";
import ImagesPreview from "./components/ImagesPreview";
import YoutubePreview from "./components/YoutubePreview";

function App() {
  const { isAwake, isListening } = useStore();
  const [showAuthModal, setShowAuthModal] = useState(false);
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

  return (
    <div className={`app-container ${isAwake ? "listening" : "not-listening"}`}>
      {user && (
        <button className="sign-out-button" onClick={signOut}>
          Sign Out
        </button>
      )}
      <div className="left-container horizontal-container">
        <div className="top-container left-top corner vertical-container">
          <div className={`suggestion-box top-left ${isAwake ? "show" : ""}`}>
            <ImagesPreview />
          </div>
        </div>
        <div className="center-container left-center vertical-container"></div>
        <div className="bottom-container left-bottom corner vertical-container">
          <div
            className={`suggestion-box bottom-left ${isAwake ? "show" : ""}`}
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
          <div className={`suggestion-box top-right ${isAwake ? "show" : ""}`}>
            <YoutubePreview url="https://www.youtube.com/watch?v=qQzdAsjWGPg" />
          </div>
        </div>
        <div className="center-container right-center vertical-container"></div>
        <div className="bottom-container right-bottom corner vertical-container">
          <div
            className={`suggestion-box bottom-right ${isAwake ? "show" : ""}`}
          >
            {/* <VideoPreview stream={videoStream} /> */}
            {/* {error && <div className="error-message">{error}</div>} */}
          </div>
        </div>
      </div>
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => user && setShowAuthModal(false)}
      />
    </div>
  );
}

export default App;
