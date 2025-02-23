import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useSupabase } from '../hooks/useSupabase';
import '../styles/ImageCarouselModal.css';

const ImageCarouselModal = ({ isOpen, onClose }) => {
  const [images, setImages] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [shouldRender, setShouldRender] = useState(false);
  const { user } = useSupabase();

  useEffect(() => {
    const fetchImages = async () => {
      if (!user) return;

      try {
        const { data: files, error } = await supabase.storage
          .from('patient-images')
          .list(user.id);

        if (error) {
          console.error('Error fetching images:', error);
          return;
        }

        const imageFiles = files.filter(file => 
          file.name.match(/\.(jpg|jpeg|png|gif)$/i)
        );

        const imageUrls = await Promise.all(
          imageFiles.map(async (file) => {
            const { data: { publicUrl } } = supabase.storage
              .from('patient-images')
              .getPublicUrl(`${user.id}/${file.name}`);
            return publicUrl;
          })
        );

        setImages(imageUrls);
      } catch (error) {
        console.error('Error processing images:', error);
      }
    };

    if (isOpen) {
      fetchImages();
    }
  }, [user, isOpen]);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
    } else {
      const timer = setTimeout(() => setShouldRender(false), 300); // match animation duration
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const handlePrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === images.length - 1 ? 0 : prevIndex + 1
    );
  };

  if (!shouldRender) return null;

  return (
    <div className={`modal-overlay ${isOpen ? 'modal-show' : 'modal-hide'}`}>
      <div className={`modal-content ${isOpen ? 'modal-show' : 'modal-hide'}`}>
        <button className="modal-close" onClick={onClose}>×</button>
        <div className="carousel-container">
          {images.length > 0 ? (
            <>
              <button className="carousel-button prev" onClick={handlePrevious}>
                ‹
              </button>
              <div className="carousel-image-container">
                <img
                  src={images[currentIndex]}
                  alt={`Image ${currentIndex + 1}`}
                  className="carousel-image"
                />
                <div className="image-counter">
                  {currentIndex + 1} / {images.length}
                </div>
              </div>
              <button className="carousel-button next" onClick={handleNext}>
                ›
              </button>
            </>
          ) : (
            <div className="no-images">No images available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageCarouselModal;
