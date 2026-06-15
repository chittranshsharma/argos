"use client";

import { motion } from "framer-motion";

export function VelocityMatrixShowcase() {
  const companies = ["OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "Mistral", "xAI"];
  const days = Array.from({ length: 14 }).map((_, i) => `D-${14 - i}`);
  
  // Generate a matrix of intensities deterministically to avoid hydration mismatch
  const matrix = companies.map((c, rowIndex) => {
    return days.map((d, colIndex) => {
      // Create some fake deterministic patterns
      let base = ((rowIndex * 37) + (colIndex * 13) + (c.length * 7)) % 100 / 100;
      if (c === "Anthropic" && colIndex > 10) base += 0.5; // recent surge
      if (c === "xAI" && colIndex > 5 && colIndex < 10) base += 0.8; // mid surge
      return Math.min(1, Math.max(0.1, base));
    });
  });

  return (
    <div className="w-full bg-surface-lowest py-24">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="flex flex-col gap-2 mb-12">
          <h2 className="text-sm font-mono text-primary uppercase tracking-widest">Analytics Centerpiece</h2>
          <h3 className="text-3xl font-bold tracking-tighter uppercase">Signal Velocity Matrix</h3>