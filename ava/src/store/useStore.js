import { create } from 'zustand';

const useStore = create((set) => ({
  isAwake: false,
  setIsAwake: (state) => set({ isAwake: state }),
  wakeUp: () => set({ isAwake: true }),  // Can only wake up, no going back to sleep
  
  isListening: false,
  setIsListening: (state) => set({ isListening: state }),
  startListening: () => set({ isListening: true }),
  stopListening: () => set({ isListening: false }),
  
  // Avatar emotion state
  activeEmotion: 'happy',
  setActiveEmotion: (emotion) => set({ activeEmotion: emotion }),
  
  lastResponse: null, // Will store the last response from the server
  setLastResponse: (response) => set({ lastResponse: response }),
  
  activeYoutubeUrl: null,
  setActiveYoutubeUrl: (url) => set({ activeYoutubeUrl: url }),
  isYoutubeModalOpen: false,
  setIsYoutubeModalOpen: (state) => set({ isYoutubeModalOpen: state }),

  // News state
  newsArticles: [],
  setNewsArticles: (articles) => set({ newsArticles: articles }),
  isNewsModalOpen: false,
  setIsNewsModalOpen: (state) => set({ isNewsModalOpen: state }),

  // Image carousel state
  isImageCarouselModalOpen: false,
  setIsImageCarouselModalOpen: (state) => set({ isImageCarouselModalOpen: state }),
  carouselImages: [],
  addCarouselImage: (imageUrl) => set((state) => ({
    carouselImages: [...state.carouselImages, imageUrl]
  })),
  clearCarouselImages: () => set({ carouselImages: [] }),

  // Voice state
  voiceIsPlaying: false,
  setVoiceIsPlaying: (state) => set({ voiceIsPlaying: state }),
}));

export default useStore;
