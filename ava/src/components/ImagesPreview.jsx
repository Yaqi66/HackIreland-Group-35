import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useSupabase } from '../hooks/useSupabase';

const ImagesPreview = () => {
  const [images, setImages] = useState([]);
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

        // Filter for image files and get random ones
        const imageFiles = files.filter(file => 
          file.name.match(/\.(jpg|jpeg|png|gif)$/i)
        );
        
        // Shuffle array and take up to 4 images
        const randomImages = imageFiles
          .sort(() => 0.5 - Math.random())
          .slice(0, 4);

        // Get URLs for the selected images
        const imageUrls = await Promise.all(
          randomImages.map(async (file) => {
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

    fetchImages();
  }, [user]);

  // Calculate grid layout based on number of images
  const getGridClass = () => {
    switch (images.length) {
      case 0:
        return 'grid-empty';
      case 1:
        return 'grid-one';
      case 2:
        return 'grid-two';
      case 3:
        return 'grid-three';
      default:
        return 'grid-four';
    }
  };

  if (images.length === 0) {
    return <div className="images-preview">No images available</div>;
  }

  return (
    <div className={`images-preview ${getGridClass()}`}>
      {images.map((url, index) => (
        <img 
          key={index}
          src={url}
          alt={`Preview ${index + 1}`}
          className="preview-image"
        />
      ))}
    </div>
  );
};

export default ImagesPreview;
