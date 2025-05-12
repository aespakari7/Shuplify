// Supabase/Supabase.js
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://uzoblakkftugdweloxku.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0'; // anonキー

const supabase = createClient(supabaseUrl, supabaseAnonKey);

module.exports = supabase;
