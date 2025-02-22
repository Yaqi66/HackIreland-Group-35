import { useEffect, useRef } from 'react';

function AudioWave({ isAwake }) {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const dataArrayRef = useRef(null);
  const previousDataRef = useRef(null);

  useEffect(() => {
    let mediaStream = null;

    const initAudio = async () => {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        
        analyserRef.current.fftSize = 64;
        analyserRef.current.smoothingTimeConstant = 0.7;
        
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);
        previousDataRef.current = new Uint8Array(bufferLength).fill(128);
        
        const source = audioContextRef.current.createMediaStreamSource(mediaStream);

        // Add noise reduction filter
        const noiseFilter = audioContextRef.current.createBiquadFilter();
        noiseFilter.type = 'highpass';
        noiseFilter.frequency.value = 2000;
        noiseFilter.Q.value = 0.5;

        // Add low pass filter to smooth out high frequencies
        const smoothingFilter = audioContextRef.current.createBiquadFilter();
        smoothingFilter.type = 'lowpass';
        smoothingFilter.frequency.value = 15000;
        smoothingFilter.Q.value = 0.7;
        
        source.connect(noiseFilter);
        noiseFilter.connect(smoothingFilter);
        smoothingFilter.connect(analyserRef.current);
        
        animate();
      } catch (err) {
        console.error('Error accessing microphone:', err);
      }
    };

    const animate = () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const width = canvas.width;
      const height = canvas.height;
      const analyser = analyserRef.current;
      const dataArray = dataArrayRef.current;
      const previousData = previousDataRef.current;

      ctx.clearRect(0, 0, width, height);

      if (!isAwake) {
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        return;
      }

      analyser.getByteFrequencyData(dataArray);

      const points = [];
      const numPoints = 20;
      const step = Math.floor(dataArray.length / numPoints);
      
      for (let i = 0; i < numPoints; i++) {
        let sum = 0;
        for (let j = 0; j < step; j++) {
          sum += dataArray[i * step + j];
        }
        const value = sum / step;
        
        // Simple smoothing
        const smoothedValue = value * 0.3 + previousData[i] * 0.7;
        previousData[i] = smoothedValue;
        
        points.push(smoothedValue);
      }

      ctx.beginPath();
      ctx.moveTo(0, height / 2);

      const pointWidth = width / (points.length - 1);
      const maxAmplitude = height / 3; // Limit maximum amplitude to 1/3 of height
      
      for (let i = 0; i < points.length; i++) {
        const x = i * pointWidth;
        // Scale the wave to fit within the container
        const scaledValue = (points[i] - 128) / 128; // Convert to -1 to 1 range
        const y = height / 2 - (scaledValue * maxAmplitude);
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          const xc = (x + (x - pointWidth)) / 2;
          const yc = (y + previousY) / 2;
          ctx.quadraticCurveTo(xc, yc, x, y);
        }
        
        var previousY = y;
      }

      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.stroke();

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    if (isAwake) {
      initAudio();
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [isAwake]);

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={30}
      style={{
        width: '100%',
        height: '100%',
        background: 'transparent'
      }}
    />
  );
}

export default AudioWave;
