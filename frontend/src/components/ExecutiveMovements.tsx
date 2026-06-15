'use client'
import { useEffect, useState } from 'react'
import { Signal } from '@/lib/types'

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
    <p className="text-argos-text-dim text-sm">
      No executive movements detected
    </p>
  )

  const getMovementColor = (title: string) => {
    if (title.includes('left')) return '#ef4444'
    if (title.includes('joined')) return '#22c55e'
    return '#eab308'
  }

  return (
    <div className="space-y-2">
      {movements.map(m => (
        <div key={m.id || m.title}
          className="p-3 rounded-lg border border-argos-border 
            hover:border-argos-border-light transition-colors">
          <div className="flex items-start justify-between">
            <p className="text-sm text-argos-text font-medium">
              {m.title}
            </p>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full"
              style={{
                background: `${getMovementColor(m.title)}20`,