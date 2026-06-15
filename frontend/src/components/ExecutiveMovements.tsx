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