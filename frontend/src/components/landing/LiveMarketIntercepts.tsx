"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

type Signal = {
  id: string;
  time: string;
  type: string;
  company: string;
  description: string;
  confidence: number;
  impact: string;
};

const INITIAL_SIGNALS: Signal[] = [
  { id: "1", time: "12:05:01", type: "FUNDING", company: "DefenseTech", description: "Series B detected ($78M)", confidence: 94, impact: "HIGH" },
  { id: "2", time: "12:04:12", type: "EXECUTIVE MOVEMENT", company: "Cohere", description: "Former OpenAI VP joined Cohere", confidence: 99, impact: "STRATEGIC" },
  { id: "3", time: "12:03:47", type: "PARTNERSHIP", company: "Accenture", description: "Accenture x NVIDIA alliance detected", confidence: 88, impact: "MEDIUM" },
  { id: "4", time: "12:03:11", type: "HIRING SURGE", company: "Anthropic", description: "Anthropic opened 24 AI Safety positions", confidence: 92, impact: "HIGH" },
];

const NEW_SIGNALS: Signal[] = [
  { id: "5", time: "12:06:22", type: "PRODUCT LAUNCH", company: "Palantir", description: "AIP for Defense v3.0 released", confidence: 98, impact: "STRATEGIC" },
  { id: "6", time: "12:07:05", type: "HIRING SURGE", company: "Scale AI", description: "Massive RLHF engineering hiring spike", confidence: 85, impact: "HIGH" },
  { id: "7", time: "12:08:14", type: "PARTNERSHIP", company: "Microsoft", description: "Exclusive cloud compute deal signed", confidence: 91, impact: "STRATEGIC" },
  { id: "8", time: "12:09:59", type: "EXECUTIVE MOVEMENT", company: "xAI", description: "Chief Scientist departure detected", confidence: 77, impact: "HIGH" },
];