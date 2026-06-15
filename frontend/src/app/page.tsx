import Link from "next/link";
import { createClient } from "@/utils/supabase/server";

// Components
import { CinematicHero } from "@/components/landing/CinematicHero";
import { LiveMarketIntercepts } from "@/components/landing/LiveMarketIntercepts";
import { CompanyProfilePreview } from "@/components/landing/CompanyProfilePreview";
import { IntelligencePipeline } from "@/components/landing/IntelligencePipeline";
import { GraphShowcase } from "@/components/landing/GraphShowcase";
import { VelocityMatrixShowcase } from "@/components/landing/VelocityMatrixShowcase";
import { BriefingShowcase } from "@/components/landing/BriefingShowcase";

export default async function LandingPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  return (
    <div className="min-h-screen bg-surface-lowest text-on-surface selection:bg-primary/30 flex flex-col overflow-x-hidden">
      
      {/* Absolute Header overlaying the Hero */}
      <header className="absolute top-0 left-0 right-0 z-50 flex h-20 items-center justify-between px-8 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 border border-primary/30">
            <span className="text-primary font-bold text-base">A</span>
          </div>
          <span className="text-xl font-bold tracking-tight text-on-surface">Argos</span>
        </div>
        <div className="flex items-center gap-6">
          {!user ? (
            <Link href="/login" className="text-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors">
              Sign Up
            </Link>
          ) : (
            <Link href="/dashboard" className="text-sm font-medium bg-primary text-black px-5 py-2 rounded-lg hover:scale-105 transition-transform">
              Launch Command Center
            </Link>
          )}
        </div>
      </header>

      {/* Sections */}
      <CinematicHero />
      <LiveMarketIntercepts />
      <CompanyProfilePreview />
      <IntelligencePipeline />
      <GraphShowcase />
      <VelocityMatrixShowcase />
      <BriefingShowcase />

      {/* Final CTA */}
      <div className="w-full bg-surface-low border-t border-surface-bright/30 py-32 text-center flex flex-col items-center">
        <h2 className="text-5xl md:text-7xl font-bold tracking-tighter uppercase mb-6">
          Stop Reading News.<br/>
          <span className="text-primary">Start Reading Intent.</span>
        </h2>
        
        <p className="text-xl text-on-surface-variant max-w-2xl mb-12 font-mono">
          Argos transforms fragmented signals into actionable intelligence.
        </p>

        <Link 
          href={user ? "/dashboard" : "/login"} 
          className="bg-primary text-black font-bold text-lg px-10 py-5 rounded-xl hover:bg-primary-hover hover:scale-105 active:scale-95 transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)]"
        >
          {user ? "ENTER COMMAND CENTER" : "REQUEST ACCESS"}
        </Link>
      </div>

    </div>
  );
}