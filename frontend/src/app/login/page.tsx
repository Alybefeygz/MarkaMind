'use client'

import React, { useState, useEffect } from 'react'
import { Eye, EyeOff, Lock, Mail, ArrowRight, AlertTriangle, Chrome } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { DEFAULT_THEME } from '@/lib/theme'

export default function LoginPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Redirect to home if already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/')
    }
  }, [router])

  // Theme colors - TechMall Store sabit renkleri
  const themeColors = DEFAULT_THEME

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Giriş başarısız')
      }

      const data = await response.json()

      // Store tokens
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      // Store user data
      if (data.user) {
        localStorage.setItem('user_data', JSON.stringify(data.user))
      }

      // Redirect to dashboard
      router.push('/')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bir hata oluştu')
    } finally {
      setIsLoading(false)
    }
  }

  const handleOAuthLogin = (provider: 'google' | 'github') => {
    // OAuth implementation will be added later
    console.log(`OAuth login with ${provider}`)
  }

  return (
    <div className="min-h-screen bg-[#F9F9FB] flex items-center justify-center px-4 py-8">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-[#DCFB6D]/5"></div>

      <div className="relative w-full max-w-md">
        {/* Main login card */}
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] border border-transparent">
          {/* Header */}
          <div className="p-8 pb-6">
            <div className="text-center mb-8">
              <h1 className="text-2xl lg:text-3xl font-bold text-[#1F1F1F] mb-2">
                Hoş Geldiniz
              </h1>
              <p className="text-sm text-[#666]">
                MarkaMind hesabınıza giriş yapın
              </p>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-2 animate-slide-from-right">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Login form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-[#666] flex items-center">
                  <Mail className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                  E-posta Adresi
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 text-gray-800 border-gray-200 focus:border-transparent bg-white placeholder-gray-400"
                  style={{
                    focusRingColor: `${themeColors.primary}30`,
                    boxShadow: formData.email ? `0 0 0 2px ${themeColors.primary}30` : undefined
                  }}
                  placeholder="ornek@email.com"
                  required
                  disabled={isLoading}
                />
              </div>

              {/* Password field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-[#666] flex items-center">
                  <Lock className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                  Şifre
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 pr-12 text-gray-800 border-gray-200 focus:border-transparent bg-white placeholder-gray-400"
                    style={{
                      focusRingColor: `${themeColors.primary}30`,
                      boxShadow: formData.password ? `0 0 0 2px ${themeColors.primary}30` : undefined
                    }}
                    placeholder="Şifrenizi girin"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Forgot password link */}
              <div className="text-right">
                <Link
                  href="/forgot-password"
                  className="text-sm text-[#666] hover:text-[#1F1F1F] transition-colors duration-200"
                >
                  Şifrenizi mi unuttunuz?
                </Link>
              </div>

              {/* Login button */}
              <button
                type="submit"
                disabled={isLoading || !formData.email || !formData.password}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl font-medium transition-all duration-300 text-white shadow-sm hover:shadow-md hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Giriş Yap</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Divider */}
          <div className="px-8">
            <div className="relative flex items-center justify-center">
              <div className="border-t border-gray-200 w-full"></div>
              <span className="bg-white px-4 text-sm text-[#666]">veya</span>
              <div className="border-t border-gray-200 w-full"></div>
            </div>
          </div>

          {/* OAuth buttons */}
          <div className="p-8 pt-6 space-y-3">
            <button
              onClick={() => handleOAuthLogin('google')}
              className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-200 text-[#666] rounded-xl font-medium transition-all duration-300 hover:border-gray-300 hover:shadow-sm hover:bg-gray-50"
              disabled={isLoading}
            >
              <Chrome className="w-5 h-5" />
              <span>Google ile Giriş Yap</span>
            </button>

            <button
              onClick={() => handleOAuthLogin('github')}
              className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-200 text-[#666] rounded-xl font-medium transition-all duration-300 hover:border-gray-300 hover:shadow-sm hover:bg-gray-50"
              disabled={isLoading}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>GitHub ile Giriş Yap</span>
            </button>
          </div>

          {/* Register link */}
          <div className="p-8 pt-0 text-center">
            <p className="text-sm text-[#666]">
              Hesabınız yok mu?{' '}
              <Link
                href="/register"
                className="font-medium hover:underline transition-all duration-200"
                style={{ color: themeColors.primary }}
              >
                Kayıt Olun
              </Link>
            </p>
          </div>
        </div>

        {/* Additional info */}
        <div className="mt-8 text-center">
          <p className="text-xs text-[#666]">
            Giriş yaparak{' '}
            <Link href="/terms" className="underline hover:text-[#1F1F1F] transition-colors">
              Kullanım Şartları
            </Link>
            {' '}ve{' '}
            <Link href="/privacy" className="underline hover:text-[#1F1F1F] transition-colors">
              Gizlilik Politikası
            </Link>
            'nı kabul etmiş olursunuz.
          </p>
        </div>
      </div>
    </div>
  )
}