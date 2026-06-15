import type { Metadata } from "next";
import { Hanken_Grotesk, JetBrains_Mono, Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const fontSans = Hanken_Grotesk({
  subsets: ["latin"],
  variable: "--font-sans",
});

const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

const fontBody = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Argos Intelligence",
  description: "Strategy Command Center for competitive intelligence",
};