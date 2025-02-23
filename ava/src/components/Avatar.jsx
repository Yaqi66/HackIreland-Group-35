import useStore from '../store/useStore';
import usePromptRecorder from '../hooks/usePromptRecorder';
import HappyAvatar from './HappyAvatar';
import SleepingZ from './SleepingZ';
import avatarNoFaceBw from '../assets/avatar-no-face-bw.svg';

function Avatar() {
  const { isAwake, isListening, activeEmotion, wakeUp, startListening } = useStore();
  usePromptRecorder(); // This will handle recording when isListening is true

  const handleClick = () => {
    if (!isAwake) {
      wakeUp();
    } else if (!isListening) {
      startListening();
    }
  };

  const getAvatarContent = () => {
    if (!isAwake) {
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
      {!isAwake && <SleepingZ />}
    </div>
  );
}

export default Avatar;
