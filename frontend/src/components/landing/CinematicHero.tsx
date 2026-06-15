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
      <div className="absolute inset-0 pointer-events-none opacity-20" style={{
        backgroundImage: `linear-gradient(rgba(0,0,0,0) 50%, rgba(0,0,0,0.25) 50%)`,
        backgroundSize: '100% 4px',
        zIndex: 5
      }}></div>

      {/* Layer 3: Radar sweeps */}
      <motion.div 
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0 pointer-events-none opacity-[0.03] z-10"
        style={{
          background: 'conic-gradient(from 0deg, transparent 0deg, var(--color-primary) 90deg, transparent 90deg)',
          borderRadius: '50%',
          width: '200vw',
          height: '200vw',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        }}
      />

      {/* Layer 1: Slow intelligence network (simulated via radial gradients moving) */}
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/10 via-surface-lowest to-surface-lowest"
      />

      {/* Layer 4: Moving anomaly markers */}
      {mounted && (
        <div className="absolute inset-0 z-10 pointer-events-none">
          {Array.from({ length: 5 }).map((_, i) => (
            <motion.div
              key={`anomaly-${i}`}
              className="absolute w-2 h-2 bg-status-critical rounded-full"
              initial={{ 
                x: `${Math.random() * 100}vw`, 
                y: `${Math.random() * 100}vh`,
                opacity: 0,
                scale: 0
              }}
              animate={{
                opacity: [0, 1, 0],
                scale: [0, 1.5, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 2,
                repeatType: "loop",
                ease: "circOut"
              }}
            />
          ))}
        </div>
      )}

      {/* Layer 2: Floating classified signals (faint text blocks in bg) */}
      {mounted && (
        <div className="absolute inset-0 z-0 overflow-hidden opacity-10 font-mono text-[8px] sm:text-xs text-primary/40 whitespace-pre">
          {Array.from({ length: 20 }).map((_, i) => (
            <motion.div
              key={`sig-${i}`}
              className="absolute"
              initial={{ x: `${Math.random() * 100}vw`, y: `${Math.random() * 100}vh` }}
              animate={{ y: [`${Math.random() * 100}vh`, `${Math.random() * 100 - 20}vh`] }}
              transition={{ duration: 15 + Math.random() * 10, repeat: Infinity, ease: "linear" }}
            >
              [SIG_INT] {Math.random().toString(36).substring(2, 10).toUpperCase()} - {Math.floor(Math.random() * 100)}% CONFIDENCE
            </motion.div>
          ))}
        </div>
      )}

      {/* Content Container */}
      <div className="relative z-20 w-full max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
        
        {/* Headline */}
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-6xl md:text-8xl font-bold tracking-tighter mb-8 uppercase"
        >