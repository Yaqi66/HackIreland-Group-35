import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { ArrowBack, Close as CloseIcon, Delete as DeleteIcon } from '@mui/icons-material';

export default function Patient({ back, patient, user }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [imageToDelete, setImageToDelete] = useState(null);
  const [patientInfo, setPatientInfo] = useState({
    name: patient['name'] || '',
    age: patient['age'] || '',
    gender: patient['gender'] || '',
    notes: patient['notes'] || ''
  });
  const [saving, setSaving] = useState(false);

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
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith('image/'))
        throw new Error('Please upload an image file');

      // Generate a unique filename with timestamp
      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}.${fileExt}`;
      const { error: uploadError } = await supabase.storage
        .from('patient-images')
        .upload(`${user.id}/${fileName}`, file);

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

  const handleDeleteImage = async () => {
    if (!imageToDelete) return;

    try {
      const { error } = await supabase.storage
        .from('patient-images')
        .remove([`${user.id}/${imageToDelete.name}`]);

      if (error) throw error;

      // Remove the image from the local state
      setImages(images.filter(img => img.id !== imageToDelete.id));
      setDeleteDialogOpen(false);
      setImageToDelete(null);
    } catch (error) {
      console.error('Error deleting image:', error);
    }
  };

  const handlePatientInfoChange = (e) => {
    const { name, value } = e.target;
    setPatientInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const upsertPatientData = async () => {
    try {
      setSaving(true);
      const { data, error } = await supabase.from('patients').upsert({
        id: patient['id'],
        name: patientInfo['name'],
        age: patientInfo['age'],
        gender: patientInfo['gender'],
        notes: patientInfo['notes']
      }).select();

      if (error) throw error;
      back(); // Go back after successful save
    } catch (error) {
      console.error('Error saving patient data:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={back} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4">
          Patient Details
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Patient Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={patientInfo.name}
              onChange={handlePatientInfoChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Age"
              name="age"
              type="number"
              value={patientInfo.age}
              onChange={handlePatientInfoChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                name="gender"
                value={patientInfo.gender}
                onChange={handlePatientInfoChange}
                label="Gender"
              >
                <MenuItem value="">Select gender</MenuItem>
                <MenuItem value="male">Male</MenuItem>
                <MenuItem value="female">Female</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              name="notes"
              multiline
              rows={4}
              value={patientInfo.notes}
              onChange={handlePatientInfoChange}
            />
          </Grid>
        </Grid>

        <Box mt={3}>
          <Button
            variant="contained"
            onClick={upsertPatientData}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Image Gallery
        </Typography>
        <Box mb={3}>
          <input
            type="file"
            accept="image/*"
            onChange={handleUpload}
            style={{ display: 'none' }}
            id="image-upload"
          />
          <label htmlFor="image-upload">
            <Button
              variant="contained"
              component="span"
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Image'}
            </Button>
          </label>
          {uploadError && (
            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
              {uploadError}
            </Typography>
          )}
        </Box>

        <Grid container spacing={2}>
          {images
            .filter(file => file.name !== ".emptyFolderPlaceholder")
            .map(file => {
              const { data: { publicUrl } } = supabase.storage
                .from('patient-images')
                .getPublicUrl(`${user.id}/${file.name}`);
              return (
                <Grid item xs={12} sm={6} md={4} key={file.id}>
                  <Paper
                    sx={{
                      p: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      position: 'relative',
                    }}
                  >
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        bgcolor: 'rgba(0, 0, 0, 0.5)',
                        '&:hover': {
                          bgcolor: 'rgba(0, 0, 0, 0.7)',
                        },
                      }}
                      onClick={() => {
                        setImageToDelete(file);
                        setDeleteDialogOpen(true);
                      }}
                    >
                      <DeleteIcon sx={{ color: 'white' }} />
                    </IconButton>
                    <Box
                      component="img"
                      src={publicUrl}
                      alt={file.name}
                      sx={{
                        width: '100%',
                        height: 200,
                        objectFit: 'cover',
                        borderRadius: 1,
                      }}
                    />
                    <Typography variant="caption" sx={{ mt: 1 }}>
                      {new Date(file.created_at).toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>
              );
            })}
        </Grid>
        {images.length === 0 && (
          <Typography color="text.secondary" align="center">
            No images found
          </Typography>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setImageToDelete(null);
        }}
      >
        <DialogTitle>Delete Image</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this image? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDeleteDialogOpen(false);
              setImageToDelete(null);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleDeleteImage} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
