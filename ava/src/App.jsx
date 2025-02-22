import "./App.css";
import Avatar from "./components/Avatar";
import VideoPreview from "./components/VideoPreview";
import AudioWave from "./components/AudioWave";
import useStore from "./store/useStore";
import useWebRTC from "./hooks/useWebRTC";

function App() {
  const { awakeState, isListening } = useStore();
  const { videoStream, error } = useWebRTC(awakeState);

  return (
    <div
      className={`app-container ${awakeState ? "listening" : "not-listening"}`}
    >
      <div className="left-container horizontal-container">
        <div className="top-container left-top corner vertical-container">
          <div
            className={`suggestion-box top-left ${awakeState ? "show" : ""}`}
          >
            {isListening ? "Listening..." : "Tap to Start"}
          </div>
        </div>
        <div className="center-container left-center vertical-container"></div>
        <div className="bottom-container left-bottom corner vertical-container">
          <div
            className={`suggestion-box bottom-left ${awakeState ? "show" : ""}`}
          >
            Suggestion 3
          </div>
        </div>
      </div>
      <div className="middle-container horizontal-container">
        <div className="top-container middle-top vertical-container"></div>
        <div className="center-container middle-center vertical-container center">
          <Avatar />
          {/* <div className={`audio-wave ${awakeState ? 'active' : ''}`}>
            <AudioWave isListening={awakeState} />
          </div> */}
        </div>
        <div className="bottom-container middle-bottom vertical-container"></div>
      </div>
      <div className="right-container horizontal-container">
        <div className="top-container right-top corner vertical-container">
          <div
            className={`suggestion-box top-right ${awakeState ? "show" : ""}`}
          >
            Suggestion 2
          </div>
        </div>
        <div className="center-container right-center vertical-container"></div>
        <div className="bottom-container right-bottom corner vertical-container">
          <div
            className={`suggestion-box bottom-right ${
              awakeState ? "show" : ""
            }`}
          >
            {/* <VideoPreview stream={videoStream} /> */}
            {error && <div className="error-message">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
