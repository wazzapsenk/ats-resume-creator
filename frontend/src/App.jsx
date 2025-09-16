import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ResumeFormPage from './pages/ResumeFormPage'
import JobPostingFormPage from './pages/JobPostingFormPage'
import AnalysisPage from './pages/AnalysisPage'
import AnalysisResultPage from './pages/AnalysisResultPage'

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return user ? children : <Navigate to="/login" />
}

// Public Route wrapper (redirect to dashboard if authenticated)
function PublicRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return user ? <Navigate to="/dashboard" /> : children
}

function AppRoutes() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        } />

        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/resume/new" element={
          <ProtectedRoute>
            <Layout>
              <ResumeFormPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/resume/edit/:id" element={
          <ProtectedRoute>
            <Layout>
              <ResumeFormPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/job-posting/new" element={
          <ProtectedRoute>
            <Layout>
              <JobPostingFormPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/job-posting/edit/:id" element={
          <ProtectedRoute>
            <Layout>
              <JobPostingFormPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/analysis" element={
          <ProtectedRoute>
            <Layout>
              <AnalysisPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/analysis/:id" element={
          <ProtectedRoute>
            <Layout>
              <AnalysisResultPage />
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App