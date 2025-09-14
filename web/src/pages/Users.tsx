
import React from 'react'
import { api } from '../lib/api'

export default function Users() {
  const [email, setEmail] = React.useState('demo@example.com')
  const [user, setUser] = React.useState<any | null>(null)
  const [plan, setPlan] = React.useState('basic')
  const [msg, setMsg] = React.useState<string>('')

  async function onCreate() {
    setMsg(''); try { const u = await api.createUser(email); setUser(u); setMsg('user created') } catch(e:any){ setMsg(String(e)) }
  }
  async function onSubscribe() {
    if (!user) return setMsg('create a user first')
    setMsg(''); try { const r = await api.subscribe(user.id, plan); setMsg(`subscribed: ${JSON.stringify(r)}`) } catch(e:any){ setMsg(String(e)) }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Users & Subscriptions</h1>
      <div className="bg-white p-4 rounded shadow space-y-3">
        <div className="flex gap-2 items-center">
          <input value={email} onChange={e=>setEmail(e.target.value)} className="border px-3 py-2 rounded w-72" placeholder="email"/>
          <button onClick={onCreate} className="px-3 py-2 rounded bg-slate-900 text-white">Create User</button>
          {user && <span className="text-sm text-slate-600">id: {user.id}</span>}
        </div>
        <div className="flex gap-2 items-center">
          <select value={plan} onChange={e=>setPlan(e.target.value)} className="border px-3 py-2 rounded">
            <option value="basic">basic</option>
            <option value="pro">pro</option>
            <option value="ent">ent</option>
          </select>
          <button onClick={onSubscribe} className="px-3 py-2 rounded bg-slate-900 text-white">Subscribe</button>
        </div>
        {msg && <div className="text-sm">{msg}</div>}
      </div>
    </div>
  )
}
