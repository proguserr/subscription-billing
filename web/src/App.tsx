
import React from 'react'
import Nav from './components/Nav'
import Dashboard from './pages/Dashboard'
import Plans from './pages/Plans'
import Users from './pages/Users'
import Billing from './pages/Billing'
import Invoices from './pages/Invoices'
import Payments from './pages/Payments'

export default function App() {
  const [tab, setTab] = React.useState('Dashboard')
  return (
    <div className="min-h-screen">
      <Nav tab={tab} setTab={setTab} />
      {tab==='Dashboard' && <Dashboard/>}
      {tab==='Plans' && <Plans/>}
      {tab==='Users' && <Users/>}
      {tab==='Billing' && <Billing/>}
        {tab==='Invoices' && <Invoices/>}
        {tab==='Payments' && <Payments/>}
    </div>
  )
}
