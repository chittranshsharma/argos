'use client'
import { useEffect, useState } from 'react'
import { Signal } from '@/lib/types'
import { Users } from 'lucide-react'

export function ExecutiveMovements({ companyId }: { companyId: string }) {
  const [movements, setMovements] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/companies/${companyId}/executives`
    )
      .then(r => r.json())
      .then(data => setMovements(data.movements || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [companyId])

  if (loading) return (
    <div className="space-y-2">
      {[1,2].map(i => (
        <div key={i} className="h-14 bg-argos-surface-2 rounded animate-pulse" />
      ))}
    </div>
  )

  if (movements.length === 0) return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold tracking-tight text-on-surface flex items-center gap-2">
          <Users className="w-5 h-5 text-primary" /> Executive Movements
        </h2>
      </div>
      <div className="glass-panel p-8 text-center rounded-xl border border-surface-bright/20">
        <p className="text-on-surface-variant text-sm">
          No executive movements detected.
        </p>
      </div>
    </div>
  )

  const getMovementColor = (title: string, content: string) => {
    const text = (title + " " + content).toUpperCase();
    if (text.includes('DEPARTED') || text.includes('LEFT') || text.includes('RESIGNED') || text.includes('STEPPED_DOWN')) return '#ef4444'
    if (text.includes('JOINED') || text.includes('APPOINTED') || text.includes('HIRED')) return '#22c55e'
    return '#eab308' // PROMOTED, etc.
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold tracking-tight text-on-surface flex items-center gap-2">
          <Users className="w-5 h-5 text-primary" /> Executive Movements
        </h2>
      </div>
      
      <div className="space-y-3">
        {movements.map(m => {
          const payload = m.payload || {};
          const previousCompany = payload.previous_company;
          const newCompany = payload.new_company;
          const reason = payload.reason_for_leaving;
          const color = getMovementColor(m.title, m.content || "");
          
          return (
            <div key={m.id || m.title}
              className="p-4 rounded-xl border border-surface-bright/30 bg-surface-low hover:bg-surface-bright/10 transition-colors">
              <div className="flex items-start justify-between">
                <p className="text-sm text-on-surface font-semibold">
                  {m.title}
                </p>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full"
                  style={{
                    background: `${color}20`,
                    color: color,
                    border: `1px solid ${color}40`
                  }}>
                  {payload.movement_type || "Executive"}
                </span>
              </div>
              
              {m.content && !previousCompany && !newCompany && (
                <p className="text-xs text-on-surface-variant mt-2 line-clamp-2">
                  {m.content}
                </p>
              )}

              {(previousCompany || newCompany || reason) && (
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs font-mono text-on-surface-variant">
                  {previousCompany && (
                    <span className="flex items-center gap-1">
                      <span className="opacity-50">From:</span> <span className="text-on-surface">{previousCompany}</span>
                    </span>
                  )}
                  {newCompany && (
                    <span className="flex items-center gap-1">
                      <span className="opacity-50">To:</span> <span className="text-on-surface">{newCompany}</span>
                    </span>
                  )}
                  {reason && (
                    <span className="flex items-center gap-1">
                      <span className="opacity-50">Reason:</span> <span className="text-on-surface italic">{reason}</span>
                    </span>
                  )}
                </div>
              )}
              
              <div className="flex justify-between items-center mt-3">
                <p className="text-[10px] text-on-surface-variant opacity-70 font-mono">
                  {new Date(m.collected_at).toLocaleDateString()}
                </p>
                {m.url && (
                  <a href={m.url} target="_blank" rel="noreferrer" className="text-[10px] text-primary hover:underline font-mono">
                    Source
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}