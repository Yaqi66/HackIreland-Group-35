import { useState, useEffect, useRef } from 'react';
import { processVideoStream, getOptimalVideoConstraints } from '../utils/videoProcessor';

const configuration = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
  ],
};

// Configure low-bandwidth video encoding
const videoEncodingParams = {
  maxBitrate: 250000, // 250 Kbps
  maxFramerate: 5
};

const useWebRTC = (isAwake) => {
  const [error, setError] = useState(null);
  const [videoStream, setVideoStream] = useState(null);
  const peerConnectionRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    let localStream;

    const startStreaming = async () => {
      try {
        // Get user media stream with both audio and video
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: getOptimalVideoConstraints(480)
        });

        // Process video stream to ensure correct size
        const processedStream = await processVideoStream(stream, 480);
        localStream = processedStream;
        streamRef.current = processedStream;
        setVideoStream(processedStream);

        // Create and configure WebRTC peer connection
        const peerConnection = new RTCPeerConnection(configuration);
        peerConnectionRef.current = peerConnection;

        // Add tracks to the peer connection with specific encoding parameters
        processedStream.getTracks().forEach(track => {
          const sender = peerConnection.addTrack(track, processedStream);
          if (track.kind === 'video') {
            const params = sender.getParameters();
            params.encodings = [{
              maxBitrate: videoEncodingParams.maxBitrate,
              maxFramerate: videoEncodingParams.maxFramerate
            }];
            sender.setParameters(params);
          }
        });

        // Connect to signaling server
        wsRef.current = new WebSocket('ws://your-signaling-server');
        
        // Handle WebSocket messages for signaling
        wsRef.current.onmessage = async (event) => {
          const message = JSON.parse(event.data);
          
          if (message.type === 'offer') {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(message));
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            wsRef.current.send(JSON.stringify(answer));
          } else if (message.type === 'ice-candidate') {
            await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
          }
        };

        // Handle ICE candidates
        peerConnection.onicecandidate = (event) => {
          if (event.candidate) {
            wsRef.current.send(JSON.stringify({
              type: 'ice-candidate',
              candidate: event.candidate
            }));
          }
        };

        // Create and send offer with video codec preferences
        const offer = await peerConnection.createOffer({
          offerToReceiveVideo: true,
          offerToReceiveAudio: true
        });
        
        // Set codec preferences for lower bandwidth
        const modifiedSDP = offer.sdp.replace(/(a=fmtp:\d+ apt=\d+)/g, '$1;x-google-max-bitrate=250;x-google-min-bitrate=100;x-google-start-bitrate=150');
        offer.sdp = modifiedSDP;

        await peerConnection.setLocalDescription(offer);
        wsRef.current.send(JSON.stringify(offer));

        // Handle connection state changes
        peerConnection.onconnectionstatechange = () => {
          if (peerConnection.connectionState === 'failed') {
            setError('Connection failed. Retrying...');
            stopStreaming();
            startStreaming();
          }
        };

      } catch (err) {
        setError(err.message);
        console.error('Error setting up WebRTC:', err);
      }
    };

    const stopStreaming = () => {
      // Stop all tracks in the stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      // Close peer connection
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
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

export default useWebRTC;
