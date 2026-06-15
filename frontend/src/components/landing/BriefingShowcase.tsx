export function BriefingShowcase() {
  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-24">
      <div className="flex flex-col md:flex-row gap-16 items-center">
        
        <div className="md:w-1/2">
          <div className="flex flex-col gap-2 mb-8">
            <h2 className="text-3xl font-bold tracking-tighter uppercase">Executive Briefing</h2>
            <div className="h-px w-full bg-surface-bright/50"></div>
          </div>
          <p className="text-on-surface-variant text-lg leading-relaxed mb-8">
            Data is useless without synthesis. Argos automatically generates classified-style executive briefings that translate raw anomalies into strategic assessments.
          </p>
          <p className="text-on-surface-variant text-lg leading-relaxed">
            Answer the "So what?" immediately. Distribute findings to your leadership team with clear impact and confidence scoring.
          </p>
        </div>

        <div className="md:w-1/2 w-full">
          <div className="bg-[#0a0a0a] border border-surface-bright/30 p-8 rounded-sm shadow-2xl relative font-mono">
            {/* Top Secret Stamp */}
            <div className="absolute top-4 right-4 border-2 border-primary/40 text-primary/40 px-2 py-1 text-xs uppercase font-bold transform rotate-12 select-none">
              INTERNAL
            </div>

            <div className="border-b-2 border-on-surface/20 pb-4 mb-6">
              <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Monitored Entity</h4>
              <h3 className="text-2xl font-bold text-on-surface tracking-tight uppercase">Anthropic</h3>
            </div>

            <div className="space-y-6 text-sm text-on-surface leading-relaxed">
              <div>
                <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-2">Primary Assessment</h4>
                <p className="bg-surface-lowest/50 p-4 border-l-2 border-primary/50 text-justify">
                  Anthropic has increased hiring velocity 41% over the last 60 days and expanded recruitment specifically targeting infrastructure scaling and enterprise safety research teams.
                </p>
              </div>

              <div>
                <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-2">Strategic Implication</h4>
                <p className="text-justify">
                  Recent executive recruitment patterns and infrastructure build-outs strongly indicate preparation for large-scale enterprise deployment initiatives in the European theater.
                </p>
              </div>

              <div className="flex gap-8 pt-4 border-t border-on-surface/10">
                <div>
                  <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Confidence</h4>
                  <p className="text-xl font-bold text-status-success">89%</p>
                </div>
                <div>
                  <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Impact</h4>
                  <p className="text-xl font-bold text-primary">STRATEGIC</p>
                </div>
                <div>
                  <h4 className="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Generated</h4>
                  <p className="text-lg text-on-surface">TODAY 14:00Z</p>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}