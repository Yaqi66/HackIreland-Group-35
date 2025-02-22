import { createClient } from '@supabase/supabase-js'

const supabaseUrl = "https://ernxmpryhwhgxgnbnatw.supabase.co"
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVybnhtcHJ5aHdoZ3hnbmJuYXR3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAyMzk5NTMsImV4cCI6MjA1NTgxNTk1M30.kTsqvJTFuzxTmkxGHz6QSZpdZ270KH3cfL1lm0cXFX0"

export const supabase = createClient(supabaseUrl, supabaseKey)
