import { create } from 'zustand';

const useStore = create((set) => ({
  isAwake: false,
  isListening: false,
  activeEmotion: 'happy',
  lastResponse: null, // Will store the last response from the server

  setAwakeState: (state) => set({ isAwake: state }),
  wakeUp: () => set({ isAwake: true }),  // Can only wake up, no going back to sleep
  
  setIsListening: (state) => set({ isListening: state }),
  startListening: () => set({ isListening: true }),
  stopListening: () => set({ isListening: false }),
  
  setActiveEmotion: (emotion) => set({ activeEmotion: emotion }),
  setLastResponse: (response) => set({ lastResponse: response }),
}));

export default useStore;
