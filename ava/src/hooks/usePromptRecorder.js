import { useState, useRef, useCallback, useEffect } from 'react';
import useStore from '../store/useStore';
import useMediaPlayer from './useMediaPlayer';

const SILENCE_THRESHOLD = 0.01;
const SILENCE_DURATION = 1000; // 1 seconds
const GRACE_PERIOD = 1000; // 0.7 second
const MAX_RECORDING_DURATION = 10000; // 10 seconds

const usePromptRecorder = () => {
  const { setLastResponse, isListening, stopListening, setIsAwake, setActiveEmotion, setIsImageCarouselModalOpen, setIsNewsModalOpen, setActiveYoutubeUrl, setIsYoutubeModalOpen } = useStore();
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const recordedChunks = useRef([]);
  const silenceTimer = useRef(null);
  const maxDurationTimer = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const recordingStartTimeRef = useRef(null);
  const { playAudioFromBase64 } = useMediaPlayer();
  const mouthAnimationInterval = useRef(null);

  // Create media recorder with video
  const createMediaRecorder = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true
      });

      // Set up audio analysis
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      source.connect(analyserRef.current);

      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      recordedChunks.current = [];
      
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunks.current.push(e.data);
        }
      };

      return mediaRecorder.current;
    } catch (error) {
      console.error('Error creating media recorder:', error);
      return null;
    }
  };

  // Convert blob to base64
  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        try {
          console.log("Converting blob of size:", blob.size);
          const base64String = reader.result
            .replace('data:video/webm;base64,', '')
            .replace('data:video/webm;codecs=vp8,opus;base64,', '');
          console.log("Base64 string length:", base64String.length);
          resolve(base64String);
        } catch (error) {
          console.error("Error in base64 conversion:", error);
          reject(error);
        }
      };
      reader.onerror = (error) => {
        console.error("FileReader error:", error);
        reject(error);
      };
      reader.readAsDataURL(blob);
    });
  };

  // Send recording to server
  const sendRecordingToServer = async (blob) => {
    try {
      console.log("Converting video blob to base64...");
      const base64Data = await blobToBase64(blob);
      console.log("Sending video request with base64 data length:", base64Data.length);

      setActiveEmotion('thinking');
      const response = await fetch('http://172.16.6.104:5000/api/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video: base64Data }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setActiveEmotion('very-happy');
      console.log("Response data:", data);

      // Handle commands
      if (data.success && data.command && data.command !== 'none') {
        switch (data.command) {
          case 'news':
            setIsNewsModalOpen(true);
            break;
          case 'show_image':
            setIsImageCarouselModalOpen(true);
            break;
          case 'play_youtube_video':
            setActiveYoutubeUrl("https://www.youtube.com/watch?v=fmg-Ks83Jy0");
            setIsYoutubeModalOpen(true);
            break;
          case 'play_music':
            setActiveYoutubeUrl("https://www.youtube.com/watch?v=qQzdAsjWGPg");
            setIsYoutubeModalOpen(true);
            break;
        }
      }

      // Play the audio response if available
      if (data.success && data.audio) {
        // Start mouth animation
        const randomMouthPosition = () => {
          setActiveEmotion(Math.random() < 0.5 ? 'happy' : 'very-happy');
        };
        
        mouthAnimationInterval.current = setInterval(randomMouthPosition, Math.random() * 100 + 50);
        
        try {
          await playAudioFromBase64(data.audio);
        } finally {
          // Clean up mouth animation
          if (mouthAnimationInterval.current) {
            clearInterval(mouthAnimationInterval.current);
            mouthAnimationInterval.current = null;
            setActiveEmotion('happy');
          }
        }
      }

      setLastResponse(data);
      return data;
    } catch (error) {
      console.error('Error sending recording to server:', error);
      setActiveEmotion('happy');
    }
  };

  // Check for silence
  const checkForSilence = () => {
    if (!analyserRef.current) return;

    // Don't check for silence during grace period
    if (Date.now() - recordingStartTimeRef.current < GRACE_PERIOD) {
      return;
    }

    const dataArray = new Float32Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getFloatTimeDomainData(dataArray);

    // Calculate RMS value
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sum / dataArray.length);

    if (rms < SILENCE_THRESHOLD) {
      if (!silenceTimer.current) {
        silenceTimer.current = setTimeout(() => {
          stopRecording();
        }, SILENCE_DURATION);
      }
    } else {
      if (silenceTimer.current) {
        clearTimeout(silenceTimer.current);
        silenceTimer.current = null;
      }
    }
  };

  // Start recording
  const startRecording = useCallback(async () => {
    if (!mediaRecorder.current) {
      await createMediaRecorder();
    }

    if (mediaRecorder.current && mediaRecorder.current.state === 'inactive') {
      recordedChunks.current = [];
      mediaRecorder.current.start(100);
      setIsRecording(true);
      recordingStartTimeRef.current = Date.now();

      // Start silence detection
      const silenceCheckInterval = setInterval(checkForSilence, 100);

      // Set maximum duration timer
      maxDurationTimer.current = setTimeout(() => {
        console.log("Max duration reached, stopping recording");
        stopRecording();
      }, MAX_RECORDING_DURATION);

      return () => {
        clearInterval(silenceCheckInterval);
        if (maxDurationTimer.current) {
          clearTimeout(maxDurationTimer.current);
        }
      };
    }
  }, []);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (silenceTimer.current) {
      clearTimeout(silenceTimer.current);
      silenceTimer.current = null;
    }

    if (maxDurationTimer.current) {
      clearTimeout(maxDurationTimer.current);
      maxDurationTimer.current = null;
    }

    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
      const blob = new Blob(recordedChunks.current, { type: 'video/webm' });
      sendRecordingToServer(blob);
      setIsRecording(false);
      stopListening();
    }
  }, [stopListening]);

  // Start recording when isListening becomes true
  useEffect(() => {
    if (isListening) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [isListening, startRecording, stopRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorder.current?.stream) {
        mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (silenceTimer.current) {
        clearTimeout(silenceTimer.current);
      }
      if (maxDurationTimer.current) {
        clearTimeout(maxDurationTimer.current);
      }
      if (mouthAnimationInterval.current) {
        clearInterval(mouthAnimationInterval.current);
        mouthAnimationInterval.current = null;
      }
    };
  }, []);

  return {
    isRecording,
    startRecording,
    stopRecording
  };
};

export default usePromptRecorder;
