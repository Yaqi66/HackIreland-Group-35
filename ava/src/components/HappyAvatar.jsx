import { useEffect, useState, useRef } from 'react';
import useStore from '../store/useStore';

function HappyAvatar() {
  const [eyeHeight, setEyeHeight] = useState(11); // Default eye height from SVG
  const blinkTimeoutRef = useRef(null);
  const { isListening } = useStore();

  const getRandomInterval = () => {
    // Random interval between 4 and 8 seconds
    return Math.random() * 4000 + 4000;
  };

  const blink = () => {
    // Close eyes
    setEyeHeight(1);
    
    // Open eyes after 150ms
    setTimeout(() => {
      setEyeHeight(11);
      
      // Schedule next blink
      blinkTimeoutRef.current = setTimeout(blink, getRandomInterval());
    }, 150);
  };

  useEffect(() => {
    // Start blinking
    blinkTimeoutRef.current = setTimeout(blink, getRandomInterval());

    // Cleanup
    return () => {
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
    };
  }, []);

  return (
    <svg width="300" height="300" viewBox="0 0 216 216" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient 
          id="paint0_linear_23_50" 
          x1="184.962" 
          y1="35.0244" 
          x2="37.4774" 
          y2="182.509" 
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#DC10E7"/>
          <stop offset="1" stopColor="#25D1F3"/>
        </linearGradient>
      </defs>
      <g filter="url(#filter0_d_23_50)" className={isListening ? 'avatar-background-listening' : ''}>
        <circle cx="108" cy="108" r="88" fill="url(#paint0_linear_23_50)"/>
      </g>
      <g filter="url(#filter1_i_23_50)">
        <circle cx="108" cy="108" r="76" fill="url(#paint1_radial_23_50)"/>
      </g>
      <circle cx="108" cy="108" r="75.5" stroke="white"/>
      <g filter="url(#filter2_d_23_50)">
        <ellipse 
          cx="81.5" 
          cy="92" 
          rx="6.5" 
          ry={eyeHeight} 
          fill="white"
          style={{ transition: 'ry 0.1s ease' }}
        />
      </g>
      <g filter="url(#filter3_d_23_50)">
        <ellipse 
          cx="134.5" 
          cy="92" 
          rx="6.5" 
          ry={eyeHeight} 
          fill="white"
          style={{ transition: 'ry 0.1s ease' }}
        />
      </g>
      <g filter="url(#filter4_d_23_50)">
        <path d="M108.071 134.952C101.996 134.952 97 132.286 97 135.876C97 139.466 101.925 142.376 108 142.376C114.075 142.376 119 139.466 119 135.876C119 132.286 114.146 134.952 108.071 134.952Z" fill="white"/>
      </g>
      <defs>
        <filter id="filter0_d_23_50" x="0" y="0" width="216" height="216" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.25 0 0 0 0 0 0 0 0 0.25 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_23_50"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_23_50" result="shape"/>
        </filter>
        <filter id="filter1_i_23_50" x="32" y="32" width="152" height="152" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feMorphology radius="1" operator="erode" in="SourceAlpha" result="effect1_innerShadow_23_50"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="4"/>
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.966667 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="shape" result="effect1_innerShadow_23_50"/>
        </filter>
        <filter id="filter2_d_23_50" x="55" y="61" width="53" height="62" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_23_50"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_23_50" result="shape"/>
        </filter>
        <filter id="filter3_d_23_50" x="108" y="61" width="53" height="62" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_23_50"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_23_50" result="shape"/>
        </filter>
        <filter id="filter4_d_23_50" x="77" y="114" width="62" height="48.3762" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset/>
          <feGaussianBlur stdDeviation="10"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0.9 0 0 0 0 1 0 0 0 1 0"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_23_50"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_23_50" result="shape"/>
        </filter>
        <radialGradient id="paint1_radial_23_50" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(68.5 62.5) rotate(43.5559) scale(84.1724)">
          <stop stopColor="#6D05A1"/>
          <stop offset="1" stopColor="#0A1758"/>
        </radialGradient>
      </defs>
    </svg>
  );
}

export default HappyAvatar;
