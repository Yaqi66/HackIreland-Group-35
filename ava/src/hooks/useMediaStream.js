import { useState, useEffect, useRef } from 'react';
import { processVideoStream, getOptimalVideoConstraints } from '../utils/videoProcessor';

const useMediaStream = (isAwake) => {
  const [error, setError] = useState(null);
  const [videoStream, setVideoStream] = useState(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    let chunks = [];

    const startStreaming = async () => {
      try {
        // Get user media stream with both audio and video
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: getOptimalVideoConstraints(480)
        });

        // Process video stream to ensure correct size
        const processedStream = await processVideoStream(stream, 480);
        streamRef.current = processedStream;
        setVideoStream(processedStream);

        // Initialize WebSocket connection
        wsRef.current = new WebSocket('ws://your-backend-url/stream');
        
        // Create MediaRecorder instance
        const mediaRecorder = new MediaRecorder(processedStream, {
          mimeType: 'video/webm;codecs=vp8,opus'
        });
        mediaRecorderRef.current = mediaRecorder;

        // Handle data available event
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            // Option 1: Send chunks immediately
            if (wsRef.current?.readyState === WebSocket.OPEN) {
              wsRef.current.send(event.data);
            }
            
            // Option 2: Collect chunks and send periodically
            chunks.push(event.data);
          }
        };

        // Start recording with smaller chunks for smoother streaming
        mediaRecorder.start(250); // 250ms chunks for video

        // Periodically send collected chunks (if using Option 2)
        const sendInterval = setInterval(() => {
          if (chunks.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
            const blob = new Blob(chunks, { type: 'video/webm;codecs=vp8,opus' });
            wsRef.current.send(blob);
            chunks = [];
          }
        }, 1000);

        // Clean up interval
        return () => clearInterval(sendInterval);

      } catch (err) {
        setError(err.message);
        console.error('Error accessing media devices:', err);
      }
    };

    const stopStreaming = () => {
      // Stop media recorder
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }

      // Stop all tracks in the stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      // Close WebSocket connection
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }

      // Clear video stream
      setVideoStream(null);
    };

    if (isAwake) {
      startStreaming();
    } else {
      stopStreaming();
    }

    // Cleanup on unmount
    return () => {
      stopStreaming();
    };
  }, [isAwake]);

  return { error, videoStream };
};

export default useMediaStream;
