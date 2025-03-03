import { useState, useEffect } from 'react';
import useStore from '../store/useStore';
import '../styles/HappyAvatar.css';

const HappyAvatar = () => {
  const [isBlinking, setIsBlinking] = useState(false);
  const { activeEmotion, isListening } = useStore();
  
  // Eye dimensions based on emotion
  const eyeHeight = activeEmotion === 'thinking' ? 4 : 11;
  const eyeWidth = activeEmotion === 'thinking' ? 9 : 6.5;
  
  // Mouth scale based on emotion
  const getMouthScale = () => {
    switch (activeEmotion) {
      case 'thinking':
        return 0.7;
      case 'very-happy':
        return 1.5;
      default: // happy
        return 1;
    }
  };

  const mouthScale = getMouthScale();

  useEffect(() => {
    if (activeEmotion === 'thinking') return;

    const blinkInterval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 150);
    }, Math.random()*4000 + 4000);

    return () => clearInterval(blinkInterval);
  }, [activeEmotion]);

  return (
    <svg width="300" height="300" viewBox="0 0 276 276" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g filter="url(#filter0_d_45_2)" className={isListening ? 'avatar-background-listening' : ''}>
        <path d="M225.999 138C225.999 186.601 194.601 174 146 174C97.3987 174 99.9999 177.101 99.9999 128.5C99.9999 79.8989 89.3982 49.9999 137.999 49.9999C186.6 49.9999 225.999 89.3989 225.999 138Z" fill="#D9D9D9"/>
      </g>
      <g filter="url(#filter1_d_45_2)" className={isListening ? 'avatar-background-listening' : ''}>
        <path d="M49.9999 137.469C49.9999 88.8683 81.3985 101.469 130 101.469C178.601 101.469 175.999 98.3683 175.999 146.969C175.999 195.57 186.601 225.469 138 225.469C89.3989 225.469 49.9999 186.07 49.9999 137.469Z" fill="#D9D9D9"/>
      </g>
      <g filter="url(#filter2_d_45_2)" className={isListening ? 'avatar-background-listening' : ''}>
        <circle cx="138" cy="138" r="88" fill="url(#paint0_linear_45_2)"/>
      </g>
      <g filter="url(#filter3_i_45_2)">
        <circle cx="137.999" cy="138" r="76" fill="url(#paint1_radial_45_2)"/>
      </g>
      <circle cx="137.999" cy="138" r="75.5" stroke="white"/>
      <g filter="url(#filter4_d_45_2)" className="avatar-eyes">
        <ellipse 
          cx="111.499" 
          cy="122" 
          rx={eyeWidth} 
          ry={eyeHeight} 
          fill="white"
          className={isBlinking ? "blink" : ""}
        />
      </g>
      <g filter="url(#filter5_d_45_2)" className="avatar-eyes">
        <ellipse 
          cx="164.499" 
          cy="122" 
          rx={eyeWidth} 
          ry={eyeHeight} 
          fill="white"
          className={isBlinking ? "blink" : ""}
        />
      </g>
      <g 
        filter="url(#filter6_d_45_2)" 
        className="avatar-mouth"
        style={{ 
          transform: `scaleX(${mouthScale}) ${activeEmotion === "very-happy" ? `scaleY(${2})` : ""}`,
          transformOrigin: 'center 168px' // Center the scaling around the middle of the mouth
        }}
      >
        <path d="M138.07 164.952C131.995 164.952 126.999 162.286 126.999 165.876C126.999 169.466 131.924 172.376 137.999 172.376C144.074 172.376 148.999 169.466 148.999 165.876C148.999 162.286 144.145 164.952 138.07 164.952Z" fill="white"/>
      </g>
      <defs>
        <filter id="filter0_d_45_2" x="49.0217" y="-7.62939e-05" width="226.978" height="225.469" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="25"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0.784314 0 0 0 0 0.145098 0 0 0 0 0.909804 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <filter id="filter1_d_45_2" x="0" y="50" width="226.978" height="225.469" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="25"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0.211765 0 0 0 0 0.74902 0 0 0 0 0.94902 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <filter id="filter2_d_45_2" x="29.9998" y="29.9999" width="216" height="216" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <filter id="filter3_i_45_2" x="61.9993" y="61.9999" width="152" height="152" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feMorphology radius="1" operator="erode" in="SourceAlpha" result="effect1_innerShadow_45_2"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="4"/>
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.966667 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="shape" result="effect1_innerShadow_45_2"/>
        </filter>
        <filter id="filter4_d_45_2" x="84.9993" y="90.9999" width="53" height="62" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <filter id="filter5_d_45_2" x="137.999" y="90.9999" width="53" height="62" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <filter id="filter6_d_45_2" x="106.999" y="144" width="62" height="48.3762" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_45_2"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_45_2" result="shape"/>
        </filter>
        <linearGradient id="paint0_linear_45_2" x1="202" y1="77.9999" x2="72" y2="196" gradientUnits="userSpaceOnUse">
          <stop stopColor="#EB60F3"/>
          <stop offset="0.0539999" stopColor="#DC10E7"/>
          <stop offset="0.944" stopColor="#25D1F3"/>
          <stop offset="1" stopColor="#84E5F9"/>
        </linearGradient>
        <radialGradient id="paint1_radial_45_2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(98.4993 92.4999) rotate(43.5559) scale(84.1724)">
          <stop stopColor="#8908C9"/>
          <stop offset="0.0889999" stopColor="#6D05A1"/>
          <stop offset="0.879" stopColor="#0A1758"/>
        </radialGradient>
      </defs>
    </svg>
  );
};

export default HappyAvatar;
