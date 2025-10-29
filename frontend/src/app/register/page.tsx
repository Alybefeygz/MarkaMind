'use client'

import React, { useState } from 'react'
import { Eye, EyeOff, Lock, Mail, User, ArrowRight, AlertTriangle, Chrome, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    username: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Theme colors - matching the design system
  const themeColors = {
    primary: '#DCFB6D',
    secondary: '#232228',
    text: '#FFFFFF'
  }

  // Username validation
  const validateUsername = (username: string) => {
    const minLength = username.length >= 3
    const maxLength = username.length <= 30
    const validChars = /^[a-zA-Z0-9_-]+$/.test(username)

    return {
      minLength,
      maxLength,
      validChars,
      isValid: minLength && maxLength && validChars && username.length > 0
    }
  }

  // Password validation
  const validatePassword = (password: string) => {
    const minLength = password.length >= 8
    const hasUpperCase = /[A-Z]/.test(password)
    const hasLowerCase = /[a-z]/.test(password)
    const hasNumbers = /\d/.test(password)
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)

    return {
      minLength,
      hasUpperCase,
      hasLowerCase,
      hasNumbers,
      hasSpecialChar,
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers
    }
  }

  const usernameValidation = validateUsername(formData.username)
  const passwordValidation = validatePassword(formData.password)
  const passwordsMatch = formData.password === formData.confirmPassword && formData.confirmPassword !== ''

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear messages when user starts typing
    if (error) setError('')
    if (success) setSuccess('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    // Client-side validation
    if (!usernameValidation.isValid) {
      setError('Kullanıcı adı gereksinimlerini karşılamıyor')
      setIsLoading(false)
      return
    }

    if (!passwordValidation.isValid) {
      setError('Şifre gereksinimlerini karşılamıyor')
      setIsLoading(false)
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Şifreler eşleşmiyor')
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          username: formData.username,
          full_name: formData.full_name
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Kayıt başarısız')
      }

      const data = await response.json()

      // Store tokens
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      setSuccess('Hesabınız başarıyla oluşturuldu! Yönlendiriliyorsunuz...')

      // Redirect to dashboard after a short delay
      setTimeout(() => {
        router.push('/')
      }, 2000)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bir hata oluştu')
    } finally {
      setIsLoading(false)
    }
  }

  const handleOAuthRegister = (provider: 'google' | 'github') => {
    // OAuth implementation will be added later
    console.log(`OAuth register with ${provider}`)
  }

  const isFormValid = formData.email &&
                     formData.full_name &&
                     formData.username &&
                     usernameValidation.isValid &&
                     passwordValidation.isValid &&
                     passwordsMatch

  return (
    <div className="min-h-screen bg-[#F9F9FB] flex items-center justify-center px-4 py-8">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-[#DCFB6D]/5"></div>

      <div className="relative w-full max-w-md">
        {/* Main register card */}
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] border border-transparent">
          {/* Header */}
          <div className="p-8 pb-6">
            <div className="text-center mb-8">
              <h1 className="text-2xl lg:text-3xl font-bold text-[#1F1F1F] mb-2">
                Hesap Oluşturun
              </h1>
              <p className="text-sm text-[#666]">
                MarkaMind'a katılın ve AI destekli chatbot'unuzu oluşturun
              </p>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-2 animate-slide-from-right">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Success message */}
            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center space-x-2 animate-slide-from-right">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <p className="text-sm text-green-600">{success}</p>
              </div>
            )}

            {/* Register form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Full Name field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-[#666] flex items-center">
                  <User className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                  Ad Soyad
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 text-gray-800 border-gray-200 focus:border-transparent bg-white placeholder-gray-400"
                  style={{
                    focusRingColor: `${themeColors.primary}30`,
                    boxShadow: formData.full_name ? `0 0 0 2px ${themeColors.primary}30` : undefined
                  }}
                  placeholder="Adınızı ve soyadınızı girin"
                  required
                  disabled={isLoading}
                />
              </div>

              {/* Username field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-[#666] flex items-center">
                  <User className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                  Kullanıcı Adı
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 text-gray-800 border-gray-200 focus:border-transparent bg-white placeholder-gray-400"
                  style={{
                    focusRingColor: `${themeColors.primary}30`,
                    boxShadow: formData.username ? `0 0 0 2px ${usernameValidation.isValid ? '#10B981' : '#EF4444'}30` : undefined
                  }}
                  placeholder="Benzersiz kullanıcı adı seçin"
                  required
                  disabled={isLoading}
                  pattern="^[a-zA-Z0-9_-]{3,30}$"
                  title="Kullanıcı adı 3-30 karakter olmalı ve sadece harf, rakam, - ve _ içerebilir"
                />
                {formData.username && (
                  <div className={`flex items-center space-x-2 text-xs ${usernameValidation.isValid ? 'text-green-600' : 'text-red-600'}`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${usernameValidation.isValid ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span>
                      {usernameValidation.isValid ?
                        'Kullanıcı adı geçerli' :
                        '3-30 karakter, sadece harf, rakam, tire (-) ve alt çizgi (_) kullanın'
                      }
                    </span>
                  </div>
                )}
              </div>

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
                    placeholder="Güvenli bir şifre oluşturun"
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

                {/* Password requirements */}
                {formData.password && (
                  <div className="space-y-2 mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-[#666] font-medium">Şifre gereksinimleri:</p>
                    <div className="space-y-1">
                      <div className={`flex items-center space-x-2 text-xs ${passwordValidation.minLength ? 'text-green-600' : 'text-gray-500'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${passwordValidation.minLength ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                        <span>En az 8 karakter</span>
                      </div>
                      <div className={`flex items-center space-x-2 text-xs ${passwordValidation.hasUpperCase ? 'text-green-600' : 'text-gray-500'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${passwordValidation.hasUpperCase ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                        <span>En az bir büyük harf</span>
                      </div>
                      <div className={`flex items-center space-x-2 text-xs ${passwordValidation.hasLowerCase ? 'text-green-600' : 'text-gray-500'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${passwordValidation.hasLowerCase ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                        <span>En az bir küçük harf</span>
                      </div>
                      <div className={`flex items-center space-x-2 text-xs ${passwordValidation.hasNumbers ? 'text-green-600' : 'text-gray-500'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${passwordValidation.hasNumbers ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                        <span>En az bir rakam</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-[#666] flex items-center">
                  <Lock className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                  Şifre Tekrarı
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 pr-12 text-gray-800 border-gray-200 focus:border-transparent bg-white placeholder-gray-400"
                    style={{
                      focusRingColor: `${themeColors.primary}30`,
                      boxShadow: formData.confirmPassword ? `0 0 0 2px ${passwordsMatch ? '#10B981' : '#EF4444'}30` : undefined
                    }}
                    placeholder="Şifrenizi tekrar girin"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                    disabled={isLoading}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>

                {/* Password match indicator */}
                {formData.confirmPassword && (
                  <div className={`flex items-center space-x-2 text-xs ${passwordsMatch ? 'text-green-600' : 'text-red-600'}`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${passwordsMatch ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span>{passwordsMatch ? 'Şifreler eşleşiyor' : 'Şifreler eşleşmiyor'}</span>
                  </div>
                )}
              </div>

              {/* Register button */}
              <button
                type="submit"
                disabled={isLoading || !isFormValid}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl font-medium transition-all duration-300 text-white shadow-sm hover:shadow-md hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Hesap Oluştur</span>
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
              onClick={() => handleOAuthRegister('google')}
              className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-200 text-[#666] rounded-xl font-medium transition-all duration-300 hover:border-gray-300 hover:shadow-sm hover:bg-gray-50"
              disabled={isLoading}
            >
              <Chrome className="w-5 h-5" />
              <span>Google ile Kayıt Ol</span>
            </button>

            <button
              onClick={() => handleOAuthRegister('github')}
              className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-200 text-[#666] rounded-xl font-medium transition-all duration-300 hover:border-gray-300 hover:shadow-sm hover:bg-gray-50"
              disabled={isLoading}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>GitHub ile Kayıt Ol</span>
            </button>
          </div>

          {/* Login link */}
          <div className="p-8 pt-0 text-center">
            <p className="text-sm text-[#666]">
              Zaten hesabınız var mı?{' '}
              <Link
                href="/login"
                className="font-medium hover:underline transition-all duration-200"
                style={{ color: themeColors.primary }}
              >
                Giriş Yapın
              </Link>
            </p>
          </div>
        </div>

        {/* Additional info */}
        <div className="mt-8 text-center">
          <p className="text-xs text-[#666]">
            Kayıt olarak{' '}
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