import { useState, useRef, useCallback, useEffect } from 'react';
import useStore from '../store/useStore';

const SILENCE_THRESHOLD = 0.01;
const SILENCE_DURATION = 1500;
const GRACE_PERIOD = 1000;
const RECORDING_DURATION = 2000; // 2 seconds
const STAGGER_DELAY = 1000; // 1 second stagger between recorders

const useWakeWordRecorder = () => {
  const { setLastResponse, startListening } = useStore();
  const [isRecording, setIsRecording] = useState(false);
  const [isListening, setIsListening] = useState(false);
  
  // Two separate media recorders
  const mediaRecorder1 = useRef(null);
  const mediaRecorder2 = useRef(null);
  const recordedChunks1 = useRef([]);
  const recordedChunks2 = useRef([]);
  const audioContextRef = useRef(null);
  const silenceCheckIntervalRef = useRef(null);

  // Create media recorder
  const createMediaAudioRecorder = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false
      });

      // Create two recorders from the same stream
      const recorder1 = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      const recorder2 = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      // Set up handlers for recorder 1
      recorder1.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunks1.current.push(e.data);
        }
      };

      recorder1.onstop = () => {
        console.log("Recorder 1 stopped with", recordedChunks1.current.length, "chunks");
      };

      // Set up handlers for recorder 2
      recorder2.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunks2.current.push(e.data);
        }
      };

      recorder2.onstop = () => {
        console.log("Recorder 2 stopped with", recordedChunks2.current.length, "chunks");
      };

      mediaRecorder1.current = recorder1;
      mediaRecorder2.current = recorder2;

      return { recorder1, recorder2 };
    } catch (error) {
      console.error('Error creating media recorder:', error);
      return null;
    }
  };

  // Function to create blob from chunks
  const createBlobFromChunks = (chunks) => {
    console.log("Creating blob from", chunks.length, "chunks");
    const blob = new Blob(chunks, { type: 'audio/webm' });
    console.log("Created blob size:", blob.size);
    return blob;
  };

  // Convert webm blob to wav blob
  const webmToWav = async (webmBlob) => {
    try {
      // Create audio context
      const audioContext = new AudioContext();
      
      // Convert blob to array buffer
      const arrayBuffer = await webmBlob.arrayBuffer();
      
      // Decode the audio data
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      // Create wav file
      const numberOfChannels = audioBuffer.numberOfChannels;
      const length = audioBuffer.length;
      const sampleRate = audioBuffer.sampleRate;
      const wavBuffer = audioContext.createBuffer(numberOfChannels, length, sampleRate);
      
      // Copy the audio data to the new buffer
      for (let channel = 0; channel < numberOfChannels; channel++) {
        const channelData = audioBuffer.getChannelData(channel);
        wavBuffer.copyToChannel(channelData, channel);
      }
      
      // Create WAV blob
      const wavBlob = await new Promise((resolve) => {
        const offlineContext = new OfflineAudioContext(numberOfChannels, length, sampleRate);
        const source = offlineContext.createBufferSource();
        source.buffer = wavBuffer;
        source.connect(offlineContext.destination);
        source.start();
        
        offlineContext.startRendering().then((renderedBuffer) => {
          const wav = audioBufferToWav(renderedBuffer);
          const wavBlob = new Blob([wav], { type: 'audio/wav' });
          resolve(wavBlob);
        });
      });
      
      console.log("Converted to WAV, size:", wavBlob.size);
      return wavBlob;
    } catch (error) {
      console.error("Error converting to WAV:", error);
      throw error;
    }
  };

  // Convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer) => {
    const numberOfChannels = buffer.numberOfChannels;
    const length = buffer.length * numberOfChannels * 2;
    const sampleRate = buffer.sampleRate;
    
    // Create the WAV file header
    const wavHeader = new ArrayBuffer(44);
    const view = new DataView(wavHeader);
    
    // "RIFF" chunk descriptor
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + length, true);
    writeString(view, 8, 'WAVE');
    
    // "fmt " sub-chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // fmt chunk length
    view.setUint16(20, 1, true); // audio format (PCM)
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numberOfChannels * 2, true); // byte rate
    view.setUint16(32, numberOfChannels * 2, true); // block align
    view.setUint16(34, 16, true); // bits per sample
    
    // "data" sub-chunk
    writeString(view, 36, 'data');
    view.setUint32(40, length, true);
    
    // Write the PCM samples
    const data = new Float32Array(buffer.length * numberOfChannels);
    const channelData = new Float32Array(buffer.length);
    let offset = 0;
    
    for (let channel = 0; channel < numberOfChannels; channel++) {
      buffer.copyFromChannel(channelData, channel);
      for (let i = 0; i < buffer.length; i++) {
        data[offset++] = channelData[i];
      }
    }
    
    // Convert to 16-bit PCM
    const pcmData = new Int16Array(data.length);
    for (let i = 0; i < data.length; i++) {
      const s = Math.max(-1, Math.min(1, data[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    
    return new Uint8Array([...new Uint8Array(wavHeader), ...new Uint8Array(pcmData.buffer)]);
  };

  // Helper function to write strings to DataView
  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
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
            .replace('data:audio/wav;base64,', '')
            .replace('data:audio/webm;base64,', '')
            .replace('data:video/webm;base64,', '');
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

  // Function to check for wake word
  const checkWakeWord = async (blob) => {
    try {
      console.log("Converting webm to wav...");
      const wavBlob = await webmToWav(blob);
      console.log("Converting wav to base64...");
      const base64Data = await blobToBase64(wavBlob);
      console.log("Sending wake word request with base64 data length:", base64Data.length);
      // do not delete: http://172.16.6.104:5000
      const response = await fetch('http://172.16.5.234:5000/api/detect-wake-word', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio: base64Data
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Wake word response:", data);
      return data.wake_word_detected;
    } catch (error) {
      console.error('Error checking wake word:', error);
      return false;
    }
  };

  // Start a single recorder cycle
  const startRecorderCycle = async (recorder, chunks, delay = 0) => {
    setTimeout(() => {
      if (recorder && recorder.state === 'inactive') {
        chunks.length = 0; // Clear chunks
        recorder.start(100);
        
        // Stop after 2 seconds
        setTimeout(async () => {
          if (recorder.state === 'recording') {
            recorder.stop();
            
            // Process the recording after it's stopped
            setTimeout(async () => {
              const blob = createBlobFromChunks(chunks);
              const isWakeWord = await checkWakeWord(blob);
              console.log("Wake word check result:", isWakeWord);
              
              if (isWakeWord) {
                stopAllRecording();
                startListening();
              } else {
                // Start next cycle
                startRecorderCycle(recorder, chunks, 0);
              }
            }, 100);
          }
        }, RECORDING_DURATION);
      }
    }, delay);
  };

  // Start wake word detection with overlapping recorders
  const startWakeWordRecording = useCallback(async () => {
    if (!mediaRecorder1.current || !mediaRecorder2.current) {
      await createMediaAudioRecorder();
    }

    // Start first recorder immediately
    startRecorderCycle(mediaRecorder1.current, recordedChunks1.current, 0);
    
    // Start second recorder after 1 second delay
    startRecorderCycle(mediaRecorder2.current, recordedChunks2.current, STAGGER_DELAY);
  }, []);

  // Stop all recording
  const stopAllRecording = useCallback(() => {
    [mediaRecorder1.current, mediaRecorder2.current].forEach(recorder => {
      if (recorder && recorder.state === 'recording') {
        recorder.stop();
      }
    });
    
    clearInterval(silenceCheckIntervalRef.current);
    setIsRecording(false);
    setIsListening(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAllRecording();
      if (mediaRecorder1.current?.stream) {
        mediaRecorder1.current.stream.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [stopAllRecording]);

  return {
    isRecording,
    isListening,
    startWakeWordRecording,
    stopRecording: stopAllRecording,
  };
};

export default useWakeWordRecorder;
