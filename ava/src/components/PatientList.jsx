import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useParams, useNavigate } from 'react-router-dom';
import Patient from './Patient'

export default function PatientList({ user }) {
  const [images, setImages] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [activePatient, setActivePatient] = useState(null);
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    age: '',
    gender: '',
    notes: ''
  });

  useEffect(() => {
      loadPatients();
  }, []);

    async function loadPatients() {
        setLoading(true);
        const { data, error } = await supabase.from('patients').select();
        setPatients(data);
        setLoading(false);
    }

  async function handleUpload(e) {
    try {
      setUploading(true);
      setUploadError(null);
      
      const file = e.target.files[0];
      if (!file) return;

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
      await loadPatients();
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
    setPatientInfo(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="patient-images">
        <h1>Patient Management Console</h1>
        {loading
         ? <div className="patient-images">Loading...</div>
         : (activePatient
            ? <Patient back={() => setActivePatient(null)}
                       patient={activePatient}
                       user={user}/>
            : <div>
                  <ul>
                      {patients.map(patient => <li key={patient['id']} class="patient-pane" onClick={() => setActivePatient(patient)}>{patient['name']}</li>)}
                  </ul>
              </div>)
        }
        {patients.length === 0 && (<div className="no-images">No patients registered</div>)}
    </div>
  );
}
