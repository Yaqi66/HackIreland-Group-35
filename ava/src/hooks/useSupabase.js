import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export const useSupabase = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Get initial user
    const getInitialUser = async () => {
      try {
        const { data: { user: initialUser } } = await supabase.auth.getUser();
        setUser(initialUser);
      } catch (err) {
        console.error('Error getting initial user:', err);
        setUser(null);
      }
    };
    
    getInitialUser();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null);
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  const signIn = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });
      if (error) throw error;
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const insertData = async (table, data) => {
    try {
      setLoading(true);
      const { data: result, error } = await supabase
        .from(table)
        .insert(data)
        .select();

      if (error) throw error;
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const getData = async (table, query = {}) => {
    try {
      setLoading(true);
      let request = supabase.from(table).select();

      if (query.filters) {
        query.filters.forEach(filter => {
          request = request.filter(filter.column, filter.operator, filter.value);
        });
      }

      if (query.orderBy) {
        request = request.order(query.orderBy.column, { ascending: query.orderBy.ascending });
      }

      const { data, error } = await request;
      if (error) throw error;
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const uploadImage = async (imageUrl) => {
    try {
      setLoading(true);
      setError(null);

      if (!user) throw new Error('User not authenticated');

      // Fetch the image from URL
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error('Failed to fetch image');
      const imageBlob = await response.blob();

      // Generate unique filename
      const timestamp = Date.now();
      const filename = `${timestamp}-${Math.random().toString(36).substring(7)}.jpg`;
      const filePath = `${user.id}/${filename}`;

      // Upload to Supabase Storage in patient-images bucket
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('patient-images')
        .upload(filePath, imageBlob, {
          contentType: 'image/jpeg',
          cacheControl: '3600',
          upsert: false
        });

      if (uploadError) throw uploadError;

      // Get the public URL
      const { data: { publicUrl } } = supabase.storage
        .from('patient-images')
        .getPublicUrl(filePath);

      return { publicUrl };
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    signIn,
    signUp,
    signOut,
    insertData,
    getData,
    uploadImage,
  };
};
