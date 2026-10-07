import { Navigate, Route, Routes } from 'react-router-dom'
import { SecurityQaPage } from './pages/SecurityQaPage'
import { EbtShell } from './components/EbtShell'
import {
  AgendaPage,
  CompanyDetailPage,
  CompaniesPage,
  ContactsPage,
  DashboardPage,
  LoginPage,
  PipelinePage,
  ProspectingPage,
  ReportsPage,
} from './pages/FoundationPages'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<EbtShell />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/empresas" element={<CompaniesPage />} />
        <Route path="/empresas/:companyId" element={<CompanyDetailPage />} />
        <Route path="/contatos" element={<ContactsPage />} />
        <Route path="/prospeccao" element={<ProspectingPage />} />
        <Route path="/pipeline" element={<PipelinePage />} />
        <Route path="/agenda" element={<AgendaPage />} />
        <Route path="/relatorios" element={<ReportsPage />} />
        <Route path="/seguranca-qa" element={<SecurityQaPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
