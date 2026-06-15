"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const LiveCounter = ({ label, targetValue }: { label: string; targetValue: number }) => {
  const [value, setValue] = useState(targetValue > 1000 ? targetValue - 100 : 0);

  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const stepTime = Math.abs(Math.floor(duration / steps));
    let current = value;
    
    const timer = setInterval(() => {
      const increment = Math.ceil((targetValue - current) / 10);
      current += increment;
      if (current >= targetValue) {
        setValue(targetValue);
        clearInterval(timer);
      } else {
        setValue(current);
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [targetValue]);

  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-mono text-on-surface-variant uppercase tracking-widest">{label}</span>
      <span className="text-2xl font-mono text-primary font-bold">{value.toLocaleString()}</span>
    </div>
  );
};

export function CinematicHero() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="relative w-full h-[90vh] min-h-[600px] flex flex-col items-center justify-center overflow-hidden bg-surface-lowest">
      {/* Background Layers */}
      
      {/* Layer 5: Subtle scanlines */}