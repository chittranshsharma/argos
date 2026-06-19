/**
 * StrategicAssessment component with outcome resolution controls and evidence logs
 */
"use client";

import { useEffect, useState } from "react";
import { getCompanyHypotheses, getHypothesisEvaluations, getResolutionSuggestions, resolveHypothesis } from "@/lib/api";
import type { Hypothesis, HypothesisEvaluation } from "@/lib/types";
import { Target, TrendingUp, TrendingDown, ChevronDown, ChevronRight, Activity, AlertCircle, ExternalLink, CheckCircle2, XCircle, HelpCircle } from "lucide-react";

export function StrategicAssessment({ companyId, allCompanies = [] }: { companyId: string; allCompanies?: { id: string; name: string }[] }) {
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [evaluations, setEvaluations] = useState<Record<string, HypothesisEvaluation[]>>({});
  const [suggestions, setSuggestions] = useState<Record<string, any>>({});
  const [resolving, setResolving] = useState<string | null>(null);

  const getSourceLabel = (signal: any) => {
    if (signal.source_type) return signal.source_type;
    if (signal.url && signal.url.includes("github.com")) return "GITHUB";
    return "NEWS";
  };

  const formatTheme = (theme: string) => {
    return theme
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(" ");
  };

  useEffect(() => {
    async function load() {
      const data = await getCompanyHypotheses(companyId);
      setHypotheses(data);
      setLoading(false);
    }
    load();
  }, [companyId]);

  const toggleExpand = async (id: string) => {
    if (expanded === id) {
      setExpanded(null);
      return;
    }
    setExpanded(id);
    if (!evaluations[id]) {
      const evals = await getHypothesisEvaluations(id);
      setEvaluations(prev => ({ ...prev, [id]: evals }));
    }
    if (!suggestions[id]) {
      const sugg = await getResolutionSuggestions(id);
      setSuggestions(prev => ({ ...prev, [id]: sugg }));
    }
  };

  const handleResolve = async (id: string, outcome: string) => {
    setResolving(id);
    await resolveHypothesis(id, outcome, "Resolved manually by analyst");
    setHypotheses(prev => prev.map(h => h.id === id ? { ...h, outcome: outcome as any, status: outcome === 'CORRECT' ? 'CONFIRMED' : (outcome === 'INCORRECT' ? 'REJECTED' : 'ACTIVE') } : h));
    setResolving(null);
  };

  if (loading) {
    return <div className="skeleton h-32 w-full" />;
  }

  if (hypotheses.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 mb-8">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold tracking-tight text-on-surface">Strategic Assessment</h2>
        </div>
        <span className="text-xs font-mono text-on-surface-variant bg-surface-bright/20 px-2.5 py-1 rounded-full border border-surface-bright/10">
          {hypotheses.filter(h => h.status === 'ACTIVE').length} active · {hypotheses.filter(h => h.status === 'CONFIRMED').length} confirmed
        </span>
      </div>

      <div className="grid gap-4">
        {hypotheses.map(hyp => {
          return (
            <div key={hyp.id} className="intelligence-card p-0 overflow-hidden border border-surface-bright/20">
              <div 
                className="p-5 cursor-pointer hover:bg-surface-low/50 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
                onClick={() => toggleExpand(hyp.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-primary border border-primary/30 px-2 py-0.5 rounded">
                      {hyp.type}
                    </span>
                    {hyp.status === 'CONFIRMED' && (
                      <span className="text-[10px] font-mono uppercase tracking-widest text-status-success bg-status-success/10 px-2 py-0.5 rounded">
                        CONFIRMED
                      </span>
                    )}
                    {hyp.status === 'REJECTED' && (
                      <span className="text-[10px] font-mono uppercase tracking-widest text-status-error bg-status-error/10 px-2 py-0.5 rounded">
                        REJECTED
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-on-surface leading-tight mt-2">{hyp.title}</h3>
                  <p className="text-sm text-on-surface-variant mt-1 line-clamp-2">{hyp.description}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {hyp.themes.map(t => (
                      <span key={t} className="text-xs text-on-surface-variant bg-surface-lowest px-2 py-1 rounded">#{formatTheme(t)}</span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-6 md:border-l md:border-surface-bright/20 md:pl-6">
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-on-surface-variant uppercase tracking-widest mb-1">Confidence</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className={`text-3xl font-bold ${hyp.confidence > 0.8 ? 'text-status-success' : hyp.confidence < 0.3 ? 'text-status-error' : 'text-primary'}`}>
                        {Math.round(hyp.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  {expanded === hyp.id ? <ChevronDown className="w-5 h-5 text-on-surface-variant" /> : <ChevronRight className="w-5 h-5 text-on-surface-variant" />}
                </div>
              </div>

              {expanded === hyp.id && (
                <div className="bg-surface-lowest border-t border-surface-bright/20">
                  {/* Strategic Forces Section */}
                  <div className="p-5 border-b border-surface-bright/10 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-surface-low border border-surface-bright/20">
                      <strong className="text-status-success uppercase text-[10px] tracking-widest block mb-2">
                        Strategic Driver (Force A)
                      </strong>
                      <p className="text-sm text-on-surface leading-relaxed">
                        Expanding market presence and betting on AI capability leadership.
                      </p>
                    </div>
                    <div className="p-4 rounded-xl bg-surface-low border border-surface-bright/20">
                      <strong className="text-status-elevated uppercase text-[10px] tracking-widest block mb-2">
                        Potential Constraint (Force B)
                      </strong>
                      <p className="text-sm text-on-surface leading-relaxed">
                        Resource limitations and integration overhead for current developer ecosystem.
                      </p>
                    </div>
                  </div>

                  {/* Predictions Horizon Panel */}
                  <div className="p-5 border-b border-surface-bright/10 bg-primary/5">
                    <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant mb-2">
                      <span className="uppercase tracking-widest font-bold text-primary">Intelligence Projection</span>
                      <span>Horizon: {hyp.predicted_time_horizon?.replace("_", " ") || "90 days"}</span>
                    </div>
                    <p className="text-sm text-on-surface leading-relaxed font-medium">
                      Argos expects confirmation of this hypothesis within the specified time horizon based on current signal velocity.
                    </p>
                  </div>

                  {/* Evidence timeline */}
                  <div className="p-5 border-b border-surface-bright/10">
                    <h4 className="text-xs font-mono uppercase tracking-widest text-on-surface-variant mb-4 flex items-center gap-2">
                      <Activity className="w-3 h-3 text-primary" /> Evidence Trail
                    </h4>
                    
                    {evaluations[hyp.id] === undefined ? (
                      <div className="skeleton h-16 w-full rounded-lg" />
                    ) : evaluations[hyp.id].length === 0 ? (
                      <div className="text-sm text-on-surface-variant flex items-center gap-2 p-3 bg-surface-low rounded-xl border border-surface-bright/10">
                        <AlertCircle className="w-4 h-4 text-on-surface-variant" /> No formal evaluations intercepted yet.
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {evaluations[hyp.id].map(ev => (
                          <div key={ev.id} className="flex gap-4 items-start bg-surface-low border border-surface-bright/20 p-4 rounded-xl">
                            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-surface-bright/10 shrink-0">
                              {ev.impact > 0 ? (
                                <TrendingUp className="w-4 h-4 text-status-success" />
                              ) : (
                                <TrendingDown className="w-4 h-4 text-status-error" />
                              )}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <span className="text-[10px] font-mono text-on-surface-variant">
                                  {new Date(ev.created_at).toLocaleDateString()}
                                </span>
                                <span
                                  className={`text-xs font-bold font-mono ${
                                    ev.impact > 0 ? "text-status-success" : "text-status-error"
                                  }`}
                                >
                                  {ev.impact > 0 ? "+" : ""}
                                  {Math.round(ev.impact * 100)}%
                                </span>
                              </div>
                              <p className="text-sm text-on-surface leading-snug">{ev.reasoning}</p>
                              {ev.signals && (
                                <div className="mt-2 pt-2 border-t border-surface-bright/10 flex items-center justify-between gap-2">
                                  <div className="flex items-center gap-1.5 min-w-0">
                                    <span className="text-[10px] font-mono uppercase tracking-wider text-on-surface-variant shrink-0 bg-surface-bright/20 px-1.5 py-0.5 rounded">
                                      {getSourceLabel(ev.signals)}
                                    </span>
                                    {ev.signals.url ? (
                                      <a
                                        href={ev.signals.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 truncate transition-colors group/link"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <span className="truncate">{ev.signals.title}</span>
                                        <ExternalLink className="w-3 h-3 shrink-0 opacity-60 group-hover/link:opacity-100" />
                                      </a>
                                    ) : (
                                      <span className="text-xs text-on-surface-variant truncate">{ev.signals.title}</span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Resolution Panel */}
                  {(!hyp.outcome || hyp.outcome === "PENDING") && (
                    <div className="p-5">
                      <h4 className="text-sm font-bold text-on-surface mb-3 flex items-center gap-2">
                        <Target className="w-4 h-4 text-primary" /> Outcome Resolution
                      </h4>
                      {suggestions[hyp.id] ? (
                        <div className="space-y-4">
                          <div>
                            <strong className="text-primary uppercase text-[10px] tracking-widest block mb-1">
                              Suggested Outcome
                            </strong>
                            <span className="font-mono text-sm text-on-surface">
                              {suggestions[hyp.id].suggested_outcome}
                            </span>
                          </div>
                          <div className="text-sm text-on-surface-variant">
                            <strong className="text-primary uppercase text-[10px] tracking-widest block mb-1">
                              Reasoning
                            </strong>
                            {suggestions[hyp.id].reasoning}
                          </div>
                          <div className="flex gap-3 pt-3 mt-2 border-t border-surface-bright/20">
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "CORRECT")}
                              className="flex-1 py-2 bg-status-success/10 text-status-success hover:bg-status-success hover:text-black font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <CheckCircle2 className="w-4 h-4" /> Correct
                            </button>
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "INCORRECT")}
                              className="flex-1 py-2 bg-status-error/10 text-status-error hover:bg-status-error hover:text-white font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <XCircle className="w-4 h-4" /> Incorrect
                            </button>
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "UNKNOWN")}
                              className="flex-1 py-2 bg-surface-bright/20 text-on-surface hover:bg-surface-bright font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <HelpCircle className="w-4 h-4" /> Unknown
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="skeleton h-24 w-full rounded-lg" />
                      )}
                    </div>
                  )}

                  {/* Final outcome badge */}
                  {hyp.outcome && hyp.outcome !== "PENDING" && (
                    <div
                      className={`mx-5 mb-5 p-4 rounded-xl border ${
                        hyp.outcome === "CORRECT"
                          ? "bg-status-success/10 border-status-success/30"
                          : "bg-status-error/10 border-status-error/30"
                      }`}
                    >
                      <div className="text-xs font-mono uppercase tracking-widest mb-1 text-on-surface-variant">
                        Final Outcome
                      </div>
                      <div
                        className={`font-bold ${
                          hyp.outcome === "CORRECT" ? "text-status-success" : "text-status-error"
                        }`}
                      >
                        {hyp.outcome}
                      </div>
                      {hyp.resolution_reason && (
                        <p className="text-sm text-on-surface-variant mt-1">{hyp.resolution_reason}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
