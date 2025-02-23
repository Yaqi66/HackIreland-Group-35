import { useCallback } from 'react';
import useStore from '../store/useStore';

const useMediaPlayer = () => {
  const { setVoiceIsPlaying } = useStore();

  const playAudioFromBase64 = useCallback(async (base64Audio) => {
    try {
      // Convert base64 to blob
      const byteCharacters = atob(base64Audio);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/mp3' });

      // Create audio element
      const audio = new Audio(URL.createObjectURL(blob));

      // Set up event listeners
      audio.addEventListener('play', () => {
        setVoiceIsPlaying(true);
      });

      audio.addEventListener('ended', () => {
        setVoiceIsPlaying(false);
        URL.revokeObjectURL(audio.src); // Clean up the URL object
      });

      audio.addEventListener('pause', () => {
        setVoiceIsPlaying(false);
      });

      audio.addEventListener('error', (error) => {
        console.error('Error playing audio:', error);
        setVoiceIsPlaying(false);
        URL.revokeObjectURL(audio.src);
      });

      // Play the audio
      await audio.play();

      return audio; // Return the audio element in case we need to control it later
    } catch (error) {
      console.error('Error in playAudioFromBase64:', error);
      setVoiceIsPlaying(false);
      return null;
    }
  }, [setVoiceIsPlaying]);

  return {
    playAudioFromBase64
  };
};

export default useMediaPlayer;
