
import React from 'react'
import { paymentsByUser } from '../lib/api'

function Badge({status}:{status:string}){
  const cls = status==='succeeded' ? 'bg-emerald-100 text-emerald-700' :
              status==='processing' ? 'bg-amber-100 text-amber-700' :
              'bg-rose-100 text-rose-700'
  return <span className={`px-2 py-1 rounded text-xs font-medium ${cls}`}>{status}</span>
}

export default function Payments(){
  const [userId, setUserId] = React.useState('')
  const [rows, setRows] = React.useState<any[]>([])
  const [state, setState] = React.useState<'idle'|'loading'|'error'>('idle')
  const [err, setErr] = React.useState('')

  async function load(){
    setState('loading'); setErr('')
    try { const data = await paymentsByUser(userId); setRows(data); setState('idle') }
    catch(e:any){ setErr(String(e)); setState('error') }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Payments</h1>
      <div className="bg-white p-4 rounded shadow">
        <div className="flex gap-2 items-center">
          <input value={userId} onChange={e=>setUserId(e.target.value)}
            className="border px-3 py-2 rounded w-[520px]" placeholder="user_id"/>
          <button onClick={load} className="px-3 py-2 rounded bg-slate-900 text-white">Load</button>
        </div>
        {state==='loading' && <div className="mt-3 text-slate-500 animate-pulse">Loading…</div>}
        {err && <div className="mt-3 text-rose-600">{err}</div>}
        {rows.length>0 && (
          <table className="mt-4 w-full text-sm">
            <thead><tr className="text-left text-slate-500">
              <th className="py-2">Payment</th><th>Invoice</th><th>Provider</th><th>Status</th><th>Created</th>
            </tr></thead>
            <tbody>
              {rows.map(r=> (
                <tr key={r.id} className="border-t">
                  <td className="py-2 font-mono text-xs">{r.id}</td>
                  <td className="font-mono text-xs">{r.invoice_id}</td>
                  <td>{r.provider}</td>
                  <td><Badge status={r.status}/></td>
                  <td>{new Date(r.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {rows.length===0 && state==='idle' && <div className="mt-3 text-slate-500">No payments.</div>}
      </div>
    </div>
  )
}
