import { useState, useEffect } from 'react'
import "./App.css";
import Avatar from "./components/Avatar";
import VideoPreview from "./components/VideoPreview";
import AudioWave from "./components/AudioWave";
import useStore from "./store/useStore";
import { useSupabase } from './hooks/useSupabase'
import AuthModal from './components/AuthModal'
import PatientList from './components/PatientList'
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import useWakeWordRecorder from './hooks/useWakeWordRecorder';

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

    const MainContent = () =>(
          <>
        {user && (
            <button className="sign-out-button" onClick={signOut}>
                Sign Out
            </button>
        )}
        <div className="left-container horizontal-container">
            <div className="top-container left-top corner vertical-container">
                <div
                    className={`suggestion-box top-left ${isAwake ? "show" : ""}`}
                >
                    {isListening ? "Listening..." : "Tap to Start"}
                </div>
            </div>
            <div className="center-container left-center vertical-container"></div>
            <div className="bottom-container left-bottom corner vertical-container">
                <div
                    className={`suggestion-box bottom-left ${isAwake ? "show" : ""}`}
                >
                    Suggestion 3
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
                        >
                            Suggestion 2
                        </div>
                    </div>
                    <div className="center-container right-center vertical-container"></div>
                    <div className="bottom-container right-bottom corner vertical-container">
                        <div
                            className={`suggestion-box bottom-right ${
              isAwake ? "show" : ""
            }`}
                        >
                            {/* <VideoPreview stream={videoStream} /> */}
                        </div>
                </div>
        </div>
        <AuthModal 
            isOpen={showAuthModal} 
            onClose={() => user && setShowAuthModal(false)} 
        />
        </>
    );

    return (<div className={`app-container ${isAwake ? "listening" : "not-listening"}`}>
                <Router>
                    <Routes>
                        <Route path="/" element={<MainContent/>}/>
                        <Route path="/admin" element={<PatientList user={user}/>}/>
                    </Routes>
                </Router>
            </div>)
}

export default App;
