
import React from 'react'
import { api } from '../lib/api'

export default function Billing() {
  const [userId, setUserId] = React.useState('')
  const [metric, setMetric] = React.useState('api_calls')
  const [qty, setQty] = React.useState(1000)
  const [out, setOut] = React.useState<string>('')

  async function addUsage() {
    setOut(''); try { await api.addUsage(userId, metric, qty); setOut('usage recorded') } catch(e:any){ setOut(String(e)) }
  }
  async function genInvoice() {
    setOut(''); try { const inv = await api.generateInvoice(userId); setOut(JSON.stringify(inv, null, 2)) } catch(e:any){ setOut(String(e)) }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Billing</h1>
      <div className="bg-white p-4 rounded shadow space-y-3">
        <div className="flex gap-2 items-center">
          <input value={userId} onChange={e=>setUserId(e.target.value)} className="border px-3 py-2 rounded w-[520px]" placeholder="user_id"/>
        </div>
        <div className="flex gap-2 items-center">
          <input value={metric} onChange={e=>setMetric(e.target.value)} className="border px-3 py-2 rounded w-48"/>
          <input type="number" value={qty} onChange={e=>setQty(parseInt(e.target.value))} className="border px-3 py-2 rounded w-32"/>
          <button onClick={addUsage} className="px-3 py-2 rounded bg-slate-900 text-white">Record Usage</button>
        </div>
        <div>
          <button onClick={genInvoice} className="px-3 py-2 rounded bg-emerald-600 text-white">Generate Invoice</button>
        </div>
        {out && <pre className="bg-slate-100 p-3 rounded overflow-auto text-sm">{out}</pre>}
      </div>
    </div>
  )
}
