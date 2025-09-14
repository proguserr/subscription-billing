
import React from 'react'
import { api } from '../lib/api'

export default function Dashboard() {
  const [status, setStatus] = React.useState<string>('checking...')
  React.useEffect(()=>{ api.health().then(()=>setStatus('ok')).catch(e=>setStatus(String(e))) },[])
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
      <div className="bg-white p-4 rounded shadow">
        <div>API health: <span className={status==='ok'?'text-green-600':'text-red-600'}>{status}</span></div>
        <p className="text-sm text-slate-500 mt-2">Use the tabs to manage plans, users, subscriptions, usage and invoices.</p>
      </div>
    </div>
  )
}
