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
