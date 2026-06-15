"use client";

import Link from "next/link";
import { ArrowLeft, Lock, Loader2 } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/utils/supabase/client";

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const router = useRouter();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    const supabase = createClient();
    
    if (isSignUp) {
      const result = await supabase.auth.signUp({ email, password });
      if (result.error) {
        setError(result.error.message);
        setLoading(false);
      } else if (result.data.user && !result.data.session) {
        setSuccessMsg("Account created! Please check your email to verify your identity.");
        setLoading(false);
      } else {
        router.push("/dashboard");
        router.refresh();
      }
    } else {
      const result = await supabase.auth.signInWithPassword({ email, password });
      if (result.error) {
        setError(result.error.message);
        setLoading(false);
      } else {
        router.push("/dashboard");
        router.refresh();
      }
    }
  };

  return (
    <div className="min-h-screen bg-surface-lowest text-on-surface flex flex-col justify-center items-center p-6">
      
      <div className="w-full max-w-md animate-slide-up">
        <Link href="/" className="inline-flex items-center gap-2 text-sm text-on-surface-variant hover:text-primary transition-colors mb-8">
          <ArrowLeft className="w-4 h-4" />
          Back to Gateway
        </Link>

        <div className="glass-panel p-8 rounded-2xl">
          <div className="flex flex-col items-center mb-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 border border-primary/30 mb-4">
              <Lock className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-on-surface text-center">
              {isSignUp ? "Register Account" : "Authenticate"}
            </h1>
            <p className="text-sm text-on-surface-variant mt-2 text-center">
              {isSignUp ? "Create a new operator identity" : "Secure access to the Command Center"}
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleAuth}>
            <div className="space-y-2">
              <label className="text-xs font-mono text-on-surface-variant uppercase tracking-widest">
                Operator ID
              </label>
              <input 
                type="email" 
                placeholder="agent@argos.local"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-surface-lowest border border-surface-bright/50 rounded-lg px-4 py-2.5 text-sm text-on-surface focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-mono text-on-surface-variant uppercase tracking-widest">
                Passkey
              </label>
              <input 
                type="password" 
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-surface-lowest border border-surface-bright/50 rounded-lg px-4 py-2.5 text-sm text-on-surface focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
              />
            </div>

            {error && (
              <div className="text-sm text-status-danger bg-status-danger/10 p-3 rounded border border-status-danger/20">
                {error}
              </div>
            )}
            {successMsg && (
              <div className="text-sm text-status-success bg-status-success/10 p-3 rounded border border-status-success/20">
                {successMsg}
              </div>
            )}

            <button 
              type="submit"
              disabled={loading}
              className="flex items-center justify-center w-full bg-primary text-black font-bold text-sm px-4 py-3 rounded-lg hover:bg-primary-hover transition-colors mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isSignUp ? "Create Account" : "Initialize Session")}
            </button>
            
            <div className="text-center mt-4">
              <button
                type="button"
                onClick={() => setIsSignUp(!isSignUp)}
                className="text-xs text-on-surface-variant hover:text-primary transition-colors"
              >
                {isSignUp ? "Already have an account? Sign in." : "Don't have an account? Sign up."}
              </button>
            </div>
          </form>
        </div>
      </div>
      
    </div>
  );
}