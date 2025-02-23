import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export default function Patient({ back, patient, user }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [patientInfo, setPatientInfo] = useState({
    name: patient['name'] || '',
    age: patient['age'] || '',
    gender: patient['gender'] || '',
    notes: patient['notes'] || ''
  });

  useEffect(() => {
    loadImages();
  }, []);

  async function loadImages() {
    const { data, error } = await supabase.storage
      .from('patient-images')
      .list(`${user.id}/`);
    
    if (data) {
      setImages(data);
    }
    setLoading(false);
  }

  async function handleUpload(e) {
    try {
      setUploading(true);
      setUploadError(null);
      const file = e.target.files[0];
        if (!file)
            return;
      // Validate file type
      if (!file.type.startsWith('image/'))
        throw new Error('Please upload an image file');
      // Generate a unique filename with timestamp
      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}.${fileExt}`;
      const { error: uploadError } = await supabase.storage
        .from('patient-images')
        .upload(fileName, file);
      if (uploadError) {
        throw uploadError;
      }
      // Refresh the image list
      await loadImages();
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError(error.message);
    } finally {
      setUploading(false);
      // Reset the file input
      e.target.value = '';
    }
  }

  const handlePatientInfoChange = (e) => {
    const { name, value } = e.target;
    setPatientInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

    const upsertPatientData = async () => {
        const { data, error } = await supabase.from('patients').upsert({
            id: patient['id'],
            name: patientInfo['name'],
            notes: patientInfo['notes']
        })
              .select()
    }
    
  if (loading) return <div className="patient-images">Loading...</div>;

  return (
    <div className="patient-images">
      <div className="patient-info-section">
        <h2>Patient Information</h2>
        <div className="patient-form">
            <div className="form-group">
            <label htmlFor="name">Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={patientInfo.name}
              onChange={handlePatientInfoChange}
              placeholder="Enter patient name"
            />
          </div>
          <div className="form-group">
            <label htmlFor="age">Age:</label>
            <input
              type="number"
              id="age"
              name="age"
              value={patientInfo.age}
              onChange={handlePatientInfoChange}
              placeholder="Enter patient age"
            />
          </div>
          <div className="form-group">
            <label htmlFor="gender">Gender:</label>
            <select
              id="gender"
              name="gender"
              value={patientInfo.gender}
              onChange={handlePatientInfoChange}
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="notes">Notes:</label>
            <textarea
              id="notes"
              name="notes"
              value={patientInfo.notes}
              onChange={handlePatientInfoChange}
              placeholder="Enter patient notes"
              rows="3"
            />
          </div>
        </div>
      </div>
      <div className="patient-images-header">
        <h2>Image Gallery</h2>
        <div className="upload-section">
          <label className="upload-button" htmlFor="file-upload">
            {uploading ? 'Uploading...' : 'Upload Image'}
            <input
              id="file-upload"
              type="file"
              accept="image/*"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
          {uploadError && <div className="upload-error">{uploadError}</div>}
        </div>
      </div>
      <button onClick={back}>Press Me To Back Out</button> <button onClick={upsertPatientData}>Press Me To Upsert</button>

      <div className="image-list">
        {images
        .filter(file => file.name != ".emptyFolderPlaceholder")
        .map(file => {
          const { data: { publicUrl } } = supabase.storage
            .from('patient-images')
            .getPublicUrl(`${user.id}/${file.name}`);
          return (
            <div key={file.id} className="image-item">
              <img 
                src={publicUrl}
                alt={file.name}
              />
              <span>
                {new Date(file.created_at).toLocaleString()}
              </span>
            </div>
          );
        })}
        {images.length === 0 && (
          <div className="no-images">No images found</div>
        )}
      </div>
    </div>
  );
}
