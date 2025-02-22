import useStore from '../store/useStore';
import useRecorder from '../hooks/useRecorder';
import HappyAvatar from './HappyAvatar';
import SleepingZ from './SleepingZ';
import avatarNoFaceBw from '../assets/avatar-no-face-bw.svg';

function Avatar() {
  const { awakeState, isListening, activeEmotion, wakeUp, startListening } = useStore();
  useRecorder(); // This will handle recording when isListening is true

  const handleClick = () => {
    if (!awakeState) {
      wakeUp();
    } else if (!isListening) {
      startListening();
    }
  };

  const getAvatarContent = () => {
    if (!awakeState) {
      return <img src={avatarNoFaceBw} alt="Sleeping avatar" className="avatar-image" />;
    }
    
    switch (activeEmotion) {
      case 'happy':
      default:
        return <HappyAvatar />;
    }
  };

  return (
    <div className="avatar-container" onClick={handleClick}>
      {getAvatarContent()}
      {!awakeState && <SleepingZ />}
    </div>
  );
}

export default Avatar;
