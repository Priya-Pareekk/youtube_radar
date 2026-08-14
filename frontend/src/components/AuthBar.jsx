import { authEnabled, supabase } from "../supabaseClient.js";

export default function AuthBar({ user }) {
  if (!authEnabled) {
    return (
      <span className="result-meta" title="Set VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY to enable">
        Sign-in not configured
      </span>
    );
  }

  if (!user) {
    return (
      <button
        className="history-toggle"
        onClick={() =>
          supabase.auth.signInWithOAuth({
            provider: "google",
            options: { redirectTo: window.location.origin },
          })
        }
      >
        Sign in with Google
      </button>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <span className="result-meta">{user.email}</span>
      <button className="history-toggle" onClick={() => supabase.auth.signOut()}>
        Sign out
      </button>
    </div>
  );
}
