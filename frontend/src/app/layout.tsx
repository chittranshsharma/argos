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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={cn(
          "min-h-screen bg-background text-foreground antialiased selection:bg-primary/30",
          fontSans.variable,
          fontMono.variable,
          fontBody.variable
        )}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}