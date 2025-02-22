import { useEffect, useRef } from 'react';
import useStore from '../store/useStore';

const SILENCE_THRESHOLD = 0.01; // Adjust this value based on testing
const SILENCE_DURATION = 1500; // 2 seconds in milliseconds
const GRACE_PERIOD = 1000; // 1 second grace period before checking for silence

export default function useRecorder() {
  const { isListening, stopListening, setLastResponse } = useStore();
  
  const mediaRecorderRef = useRef(null);
  const silenceStartRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const silenceCheckIntervalRef = useRef(null);
  const recordingStartTimeRef = useRef(null);

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
    console.log("Audio level:", rms);

    if (rms < SILENCE_THRESHOLD) {
      if (!silenceStartRef.current) {
        silenceStartRef.current = Date.now();
      } else if (Date.now() - silenceStartRef.current >= SILENCE_DURATION) {
        stopRecording();
      }
    } else {
      silenceStartRef.current = null;
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
      
      // Set up audio analysis
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 2048;

      // Set up recording
      mediaRecorderRef.current = new MediaRecorder(stream);
      recordedChunksRef.current = [];
      recordingStartTimeRef.current = Date.now(); // Set recording start time

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        
        // Create form data
        const formData = new FormData();
        formData.append('video', blob, 'recording.webm');

        try {
          const response = await fetch('/api/process-recording', {
            method: 'POST',
            body: formData
          });

          if (!response.ok) throw new Error('Failed to process recording');

          const data = await response.json();
          setLastResponse(data);
        } catch (error) {
          console.error('Error processing recording:', error);
        }

        // Cleanup
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      mediaRecorderRef.current.start(1000); // Collect data every second
      silenceCheckIntervalRef.current = setInterval(checkForSilence, 100);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      if (silenceCheckIntervalRef.current) {
        clearInterval(silenceCheckIntervalRef.current);
      }
      stopListening();
    }
  };

  useEffect(() => {
    if (isListening) {
      startRecording();
    }

    return () => {
      stopRecording();
    };
  }, [isListening]);

  return { isRecording: mediaRecorderRef.current?.state === 'recording' };
}
