"use client"

import { useState, useEffect } from "react"
import { Shield, Check, X, AlertTriangle, Info, Loader2 } from "lucide-react"

export default function IntelligenceReviewPage() {
  const [signals, setSignals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState<string | null>(null)
  const [rejectReason, setRejectReason] = useState("")
  const [rejectingSignal, setRejectingSignal] = useState<any | null>(null)

  useEffect(() => {
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      const res = await fetch("http://localhost:8001/api/admin/signals/pending")
      if (res.ok) {
        const data = await res.json()
        setSignals(data)
      }
    } catch (e) {
      console.error("Failed to fetch pending signals", e)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (signalId: string) => {
    setProcessingId(signalId)
    try {
      await fetch(`http://localhost:8001/api/admin/signals/${signalId}/approve`, {
        method: "POST"
      })
      setSignals(signals.filter(s => s.id !== signalId))
    } catch (e) {
      console.error(e)
    } finally {
      setProcessingId(null)
    }
  }

  const handleReject = async () => {
    if (!rejectingSignal || !rejectReason.trim()) return
    setProcessingId(rejectingSignal.id)
    try {
      await fetch(`http://localhost:8001/api/admin/signals/${rejectingSignal.id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: rejectReason })
      })
      setSignals(signals.filter(s => s.id !== rejectingSignal.id))
      setRejectingSignal(null)
      setRejectReason("")
    } catch (e) {
      console.error(e)
    } finally {
      setProcessingId(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          Intelligence Review Queue
        </h1>
        <p className="text-gray-400 mt-2">
          Review low-confidence signals and suspicious extraction before they contaminate the knowledge graph. Rejections act as negative reinforcement training data.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>
      ) : signals.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400 flex flex-col items-center">
          <Check className="w-12 h-12 text-green-500 mb-4 opacity-50" />
          <h3 className="text-xl font-medium text-white">Queue is empty</h3>
          <p className="mt-2">No pending signals require manual review.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {signals.map(signal => {
            const reasoning = signal.payload?.confidence_reasoning || {}
            return (
              <div key={signal.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 relative">
                {processingId === signal.id && (
                  <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-xl">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                  </div>
                )}
                
                <div className="flex items-start justify-between">
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold bg-gray-800 text-gray-300 px-2 py-0.5 rounded-md border border-gray-700">
                          {signal.company_name}
                        </span>
                        <span className="text-xs font-semibold bg-blue-900/30 text-blue-400 px-2 py-0.5 rounded-md border border-blue-900/50">
                          {signal.signal_type} / {signal.subtype}
                        </span>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-md border ${
                          signal.confidence < 0.7 ? 'bg-red-900/30 text-red-400 border-red-900/50' : 'bg-yellow-900/30 text-yellow-400 border-yellow-900/50'
                        }`}>
                          {Math.round((signal.confidence || 0) * 100)}% Confidence
                        </span>
                      </div>
                      <h3 className="text-lg font-medium text-white">{signal.title}</h3>
                      <p className="text-sm text-gray-400 max-w-3xl">{signal.content}</p>
                    </div>

                    <div className="bg-gray-950 rounded-lg p-3 border border-gray-800 text-sm grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-gray-500 text-xs block mb-1">Source Agent</span>
                        <span className="text-gray-300">{signal.agent}</span>
                      </div>
                      <div>
                        <span className="text-gray-500 text-xs block mb-1">Source Reliability</span>
                        <span className="text-gray-300">{(reasoning.source_score || 0).toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500 text-xs block mb-1">Confirming Sources</span>
                        <span className="text-gray-300">{reasoning.source_count || 1}</span>
                      </div>
                      <div>
                        <span className="text-gray-500 text-xs block mb-1">Value/Entity Detected</span>
                        <span className="text-gray-300">
                          {reasoning.value_indicators_detected || reasoning.named_entities ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>
                    
                    {signal.url && (
                      <a href={signal.url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                        <Info className="w-3 h-3" /> View Source Article
                      </a>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 min-w-[140px]">
                    <button 
                      onClick={() => handleApprove(signal.id)}
                      className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors"
                    >
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button 
                      onClick={() => setRejectingSignal(signal)}
                      className="px-4 py-2 bg-gray-800 hover:bg-red-900/50 hover:text-red-400 text-gray-300 border border-gray-700 hover:border-red-900/50 font-medium rounded-lg flex items-center justify-center gap-2 transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Reject Modal */}
      {rejectingSignal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Reject Signal
            </h3>
            <p className="text-sm text-gray-400 mb-4">
              Please provide a reason. This will be stored in the `rejected_signals` table for future model fine-tuning.
            </p>
            <textarea
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-sm text-gray-200 min-h-[100px] focus:outline-none focus:border-blue-500 transition-colors mb-4"
              placeholder="e.g. Hallucinated executive movement, company name misinterpreted as person..."
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              autoFocus
            />
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => {
                  setRejectingSignal(null)
                  setRejectReason("")
                }}
                className="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleReject}
                disabled={!rejectReason.trim()}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
