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
        </div>

        <div className="md:w-1/2 w-full">
          {/* Authentic Company Profile Mock */}
          <div className="border border-primary/20 bg-surface-low rounded-xl p-6 relative overflow-hidden group hover:border-primary/50 transition-colors">
            
            {/* Corner Accents */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary/40"></div>
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-primary/40"></div>
            
            <div className="flex justify-between items-start mb-8">
              <div>
                <p className="text-xs font-mono text-primary uppercase tracking-widest mb-1">Target Entity</p>
                <h3 className="text-3xl font-bold text-on-surface">Anthropic</h3>
              </div>
              <div className="text-right">
                <p className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-1">Intelligence Score</p>
                <p className="text-4xl font-mono font-bold text-status-success">91<span className="text-lg text-on-surface-variant">/100</span></p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-surface-lowest p-4 rounded border border-surface-bright/30">
                <p className="text-xs font-mono text-on-surface-variant uppercase mb-2">Signals (30D)</p>
                <p className="text-2xl font-mono text-on-surface">147</p>
              </div>
              <div className="bg-surface-lowest p-4 rounded border border-surface-bright/30">
                <p className="text-xs font-mono text-on-surface-variant uppercase mb-2">Confidence Matrix</p>
                <p className="text-2xl font-mono text-primary">89%</p>
              </div>
            </div>

            <div>
              <p className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-4">Detected Vectors</p>
              <div className="space-y-3">
                {[