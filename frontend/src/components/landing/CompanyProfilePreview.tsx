import { Target, Activity, Users, ShieldAlert, Check } from "lucide-react";

export function CompanyProfilePreview() {
  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-24">
      <div className="flex flex-col md:flex-row items-center gap-16">
        
        <div className="md:w-1/2">
          <div className="flex flex-col gap-2 mb-8">
            <h2 className="text-3xl font-bold tracking-tighter uppercase">What Argos Sees</h2>
            <div className="h-px w-full bg-surface-bright/50"></div>
          </div>
          
          <p className="text-on-surface-variant text-lg leading-relaxed mb-8">
            Argos doesn't give you a dashboard of raw news articles. It synthesizes millions of discrete events into a comprehensive, tactical profile of a target entity.
          </p>
          <p className="text-on-surface-variant text-lg leading-relaxed">
            By monitoring specific vectors—hiring, leadership, funding, repositories, and partnerships—Argos determines the strategic posture of your competitors before they announce it.
          </p>