
import React from 'react'
import { api } from '../lib/api'

export default function Plans() {
  const [plans, setPlans] = React.useState<any[]>([])
  const [err, setErr] = React.useState<string>('')
  React.useEffect(()=>{ api.plans().then(setPlans).catch(e=>setErr(String(e))) },[])
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Plans</h1>
      {err && <div className="text-red-600">{err}</div>}
      <div className="grid md:grid-cols-3 gap-4">
        {plans.map(p => (
          <div key={p.code} className="bg-white rounded shadow p-4">
            <div className="text-lg font-medium">{p.name}</div>
            <div className="text-slate-500">{p.code.toUpperCase()}</div>
            <div className="mt-2 text-xl">${(p.amount_cents/100).toFixed(2)}/mo</div>
            <div className="text-sm text-slate-500">Trial: {p.trial_days}d</div>
          </div>
        ))}
      </div>
    </div>
  )
}
