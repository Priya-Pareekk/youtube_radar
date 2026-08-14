import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// If these aren't set, the app still works — it just runs "logged out"
// (session-only history, no watches). That keeps local dev simple even
// before Supabase is configured.
export const supabase = url && anonKey ? createClient(url, anonKey) : null;
export const authEnabled = Boolean(supabase);
