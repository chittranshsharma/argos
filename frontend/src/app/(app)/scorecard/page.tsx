"use client";

import { useEffect, useState } from "react";
import { getAnalystScorecard } from "@/lib/api";
import { Target, Activity, CheckCircle2, XCircle, HelpCircle, BarChart3, Clock } from "lucide-react";

export default function ScorecardPage() {
  const [scorecard, setScorecard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const data = await getAnalystScorecard();
      setScorecard(data);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="skeleton h-96 w-full" />;
  }

  if (!scorecard) {
    return <div className="text-on-surface-variant">Failed to load scorecard.</div>;
  }

  const {
    total_hypotheses,
    resolved_count,
    resolution_rate,
    global_accuracy,
    correct_predictions,
    incorrect_predictions,
    accuracy_by_type
  } = scorecard;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
          <Target className="w-8 h-8 text-primary" />
          Analyst Scorecard
        </h1>
        <p className="text-on-surface-variant mt-2 max-w-2xl">
          System performance metrics and hypothesis outcome tracking. This provides ground-truth on how well Argos predicts the future.
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="intelligence-card p-5 border-l-4 border-l-primary">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-2">Total Generated</div>
          <div className="text-3xl font-bold text-on-surface">{total_hypotheses}</div>
        </div>
        <div className="intelligence-card p-5 border-l-4 border-l-status-elevated">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-2">Resolution Rate</div>
          <div className="text-3xl font-bold text-status-elevated">{(resolution_rate * 100).toFixed(1)}%</div>
          <div className="text-xs text-on-surface-variant mt-1">{resolved_count} resolved</div>
        </div>
        <div className="intelligence-card p-5 border-l-4 border-l-status-success">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-2">Global Accuracy</div>
          <div className="text-3xl font-bold text-status-success">{(global_accuracy * 100).toFixed(1)}%</div>
          <div className="text-xs text-on-surface-variant mt-1">{correct_predictions} correct</div>
        </div>
        <div className="intelligence-card p-5 border-l-4 border-l-status-error">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-2">False Positives</div>
          <div className="text-3xl font-bold text-status-error">{incorrect_predictions}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-xl border border-surface-bright/20">
          <h3 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" /> Accuracy by Narrative Type
          </h3>
          <div className="space-y-4">
            {Object.entries(accuracy_by_type).map(([type, accuracy]: [string, any]) => (
              <div key={type} className="flex flex-col gap-1.5">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-on-surface-variant font-medium">{type.replace(/_/g, ' ')}</span>
                  <span className="font-mono text-xs font-bold">{(accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${accuracy >= 0.7 ? 'bg-status-success' : accuracy >= 0.5 ? 'bg-status-elevated' : 'bg-status-error'}`} 
                    style={{ width: `${accuracy * 100}%` }} 
                  />
                </div>
              </div>
            ))}
            {Object.keys(accuracy_by_type).length === 0 && (
              <div className="text-sm text-on-surface-variant">Not enough resolved hypotheses to calculate accuracy by type.</div>
            )}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-surface-bright/20">
          <h3 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary" /> Upcoming Resolutions
          </h3>
          <div className="text-sm text-on-surface-variant">
            Time horizon tracking will be available here, allowing you to see which hypotheses are nearing their 30/90/180 day horizons and require analyst review.
          </div>
        </div>
      </div>
    </div>
  );
}
