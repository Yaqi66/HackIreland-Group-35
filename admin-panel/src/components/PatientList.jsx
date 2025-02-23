import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import Patient from './Patient';

export default function PatientList({ user }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activePatient, setActivePatient] = useState(null);

  useEffect(() => {
    loadPatients();
  }, []);

  async function loadPatients() {
    setLoading(true);
    const { data, error } = await supabase.from('patients').select();
    if (error) {
      console.error('Error loading patients:', error);
    } else {
      setPatients(data || []);
    }
    setLoading(false);
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (activePatient) {
    return (
      <Patient
        back={() => {
          setActivePatient(null);
          loadPatients(); // Refresh the list when going back
        }}
        patient={activePatient}
        user={user}
      />
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Patient Management Console
      </Typography>
      <Paper sx={{ width: '100%', mb: 2 }}>
        <List>
          {patients.map((patient, index) => (
            <div key={patient.id}>
              <ListItem
                button
                onClick={() => setActivePatient(patient)}
                sx={{
                  py: 2,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={
                    <Typography variant="h6" component="div">
                      {patient.name || 'Unnamed Patient'}
                    </Typography>
                  }
                  secondary={
                    <Box component="div" mt={1}>
                      <Typography variant="body2" component="span" color="text.secondary" sx={{ mr: 2 }}>
                        Age: {patient.age || 'N/A'}
                      </Typography>
                      <Typography variant="body2" component="span" color="text.secondary" sx={{ mr: 2 }}>
                        Gender: {patient.gender || 'N/A'}
                      </Typography>
                      {patient.notes && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          Notes: {patient.notes}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < patients.length - 1 && <Divider />}
            </div>
          ))}
        </List>
        {patients.length === 0 && (
          <Box p={3} textAlign="center">
            <Typography color="text.secondary">
              No patients registered
            </Typography>
          </Box>
        )}
      </Paper>
      <Button
        variant="contained"
        onClick={async () => {
          const { data, error } = await supabase
            .from('patients')
            .insert({ name: 'New Patient' })
            .select()
            .single();
          
          if (error) {
            console.error('Error creating patient:', error);
          } else {
            setActivePatient(data);
          }
        }}
      >
        Add New Patient
      </Button>
    </Box>
  );
}
