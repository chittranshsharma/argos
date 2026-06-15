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