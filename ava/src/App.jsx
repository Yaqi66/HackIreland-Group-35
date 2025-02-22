import { useState, useEffect } from 'react'
import "./App.css";
import Avatar from "./components/Avatar";
import VideoPreview from "./components/VideoPreview";
import AudioWave from "./components/AudioWave";
import useStore from "./store/useStore";
import useWebRTC from "./hooks/useWebRTC";
import { useSupabase } from './hooks/useSupabase'
import AuthModal from './components/AuthModal'
import PatientImages from './components/PatientImages'

function App() {
  const { awakeState, isListening } = useStore();
  const { videoStream, error } = useWebRTC(awakeState);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user, signOut } = useSupabase();

  useEffect(() => {
    console.log("user:", user);
    // Only show modal if user is explicitly null (not undefined)
    if (user === null) {
      setShowAuthModal(true);
    } else if (user) {
      setShowAuthModal(false);
    }
  }, [user]);

  useEffect(()=>{
    console.log("showAuthModal:", showAuthModal);
  },[showAuthModal]) 

  return (
    <div
      className={`app-container ${awakeState ? "listening" : "not-listening"}`}
    >
      {user && (
        <button onClick={signOut} className="sign-out-button">
          Sign Out
        </button>
      )}

      {!user ? undefined : (
        <div className="main-content">
          <PatientImages />
        </div>
      )}

      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => user && setShowAuthModal(false)} 
      />
    </div>
  );
}

export default App;
