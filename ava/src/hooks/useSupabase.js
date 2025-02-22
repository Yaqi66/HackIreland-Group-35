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
      console.log('Auth state changed:', event, session?.user);
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

  return {
    loading,
    error,
    user,
    signIn,
    signUp,
    signOut,
    insertData,
    getData,
  };
};
