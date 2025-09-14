
import React from 'react'

export default function Nav({ tab, setTab }: { tab: string, setTab: (t: string)=>void }) {
  const items = ['Dashboard','Plans','Users','Billing','Invoices','Payments']
  return (
    <nav className="flex gap-3 p-3 bg-white shadow">
      {items.map(i => (
        <button key={i}
          className={`px-3 py-1 rounded ${tab===i?'bg-slate-900 text-white':'bg-slate-200'}`}
          onClick={()=>setTab(i)}>{i}</button>
      ))}
      <div className="ml-auto text-sm text-slate-500">API: {import.meta.env.VITE_API_BASE || 'http://localhost:8080'}</div>
    </nav>
  )
}
