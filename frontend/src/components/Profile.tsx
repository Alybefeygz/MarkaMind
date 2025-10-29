'use client'

import { User, Mail, Hash, Store, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

interface ProfileProps {
  themeColors: {
    primary: string
    secondary: string
    text: string
  }
}

// Örnek kullanıcı verisi
const userData = {
  name: 'Ahmet Yılmaz',
  email: 'ahmet.yilmaz@markamind.com',
  userId: 'MM-2024-A7F2',
  profilePhoto: 'https://ui-avatars.com/api/?name=Ahmet+Yilmaz&background=ff6925&color=fff&size=200',
  stores: [
    { id: 1, name: 'TechMall Store', platform: 'WooCommerce', status: 'active' },
    { id: 2, name: 'Digital Market', platform: 'Magento', status: 'active' },
    { id: 3, name: 'Style Shop', platform: 'Shopify', status: 'inactive' }
  ]
}

export default function Profile({ themeColors }: ProfileProps) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showOldPassword, setShowOldPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const handleSavePassword = () => {
    if (newPassword !== confirmPassword) {
      alert('Yeni şifreler eşleşmiyor!')
      return
    }
    // Şifre güncelleme işlemi burada yapılacak
    alert('Şifre başarıyla güncellendi!')
    setOldPassword('')
    setNewPassword('')
    setConfirmPassword('')
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 lg:gap-6 w-full mt-4 lg:mt-6 px-2 sm:px-4">

      {/* Profil Bilgileri Kartı */}
      <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 min-h-[600px] lg:min-h-[700px]" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
        <div className="flex items-center px-4 sm:px-6 py-4 sm:py-5 border-b border-gray-200">
          <h3 className="text-lg sm:text-xl lg:text-2xl">
            <span
              className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
              style={{
                backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
              }}
            >
              Profil
            </span>
            <span
              className="font-normal bg-gradient-to-r bg-clip-text text-transparent ml-1"
              style={{
                backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
              }}
            >
              Bilgileri
            </span>
          </h3>
        </div>
        <div className="flex-1 p-4 sm:p-5 lg:p-6 flex flex-col space-y-5 overflow-y-auto">

          {/* Profil Fotoğrafı */}
          <div className="flex flex-col items-center py-2">
            <div className="relative">
              <img
                src={userData.profilePhoto}
                alt={userData.name}
                className="w-20 h-20 sm:w-24 sm:h-24 rounded-full object-cover border-3 shadow-lg"
                style={{ borderColor: themeColors.primary }}
              />
            </div>
          </div>

          {/* Kullanıcı Bilgileri */}
          <div className="space-y-3">
            {/* İsim */}
            <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${themeColors.primary}15` }}
              >
                <User className="w-4 h-4" style={{ color: themeColors.primary }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 mb-0.5">Ad Soyad</p>
                <p className="text-sm font-semibold text-gray-900 truncate">{userData.name}</p>
              </div>
            </div>

            {/* Email */}
            <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${themeColors.primary}15` }}
              >
                <Mail className="w-4 h-4" style={{ color: themeColors.primary }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 mb-0.5">E-posta</p>
                <p className="text-sm font-semibold text-gray-900 truncate">{userData.email}</p>
              </div>
            </div>

            {/* Kullanıcı ID */}
            <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${themeColors.primary}15` }}
              >
                <Hash className="w-4 h-4" style={{ color: themeColors.primary }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 mb-0.5">Kullanıcı ID</p>
                <p className="text-sm font-semibold text-gray-900 font-mono">{userData.userId}</p>
              </div>
            </div>
          </div>

          {/* Mağazalar */}
          <div className="pt-3 border-t border-gray-200">
            <div className="flex items-center space-x-2 mb-3">
              <Store className="w-4 h-4" style={{ color: themeColors.primary }} />
              <h4 className="text-sm font-semibold text-gray-900">Mağazalarım</h4>
            </div>
            <div className="space-y-2">
              {userData.stores.map((store) => (
                <div
                  key={store.id}
                  className="flex items-center justify-between p-2.5 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer"
                  style={{
                    backgroundColor: store.status === 'active' ? `${themeColors.primary}05` : 'transparent'
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-900 truncate">{store.name}</p>
                    <p className="text-xs text-gray-500">{store.platform}</p>
                  </div>
                  <div className="flex items-center space-x-1.5 flex-shrink-0 ml-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${store.status === 'active' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                    <span className={`text-xs font-medium ${store.status === 'active' ? 'text-green-600' : 'text-gray-500'}`}>
                      {store.status === 'active' ? 'Aktif' : 'Pasif'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Güvenlik Kartı */}
      <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 min-h-[600px] lg:min-h-[700px]" style={{ borderColor: '#E5E7EB', animationDelay: '300ms' }}>
        <div className="flex items-center px-4 sm:px-6 py-4 sm:py-5 border-b border-gray-200">
          <h3 className="text-lg sm:text-xl lg:text-2xl">
            <span
              className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
              style={{
                backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
              }}
            >
              Güvenlik
            </span>
          </h3>
        </div>
        <div className="flex-1 p-4 sm:p-5 lg:p-6 flex flex-col overflow-y-auto">
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Şifre Yenileme</h4>

            {/* Eski Şifre */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                Eski Şifre
              </label>
              <div className="relative">
                <input
                  type={showOldPassword ? 'text' : 'password'}
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none transition-all"
                  onFocus={(e) => {
                    e.target.style.borderColor = themeColors.primary
                    e.target.style.boxShadow = `0 0 0 3px ${themeColors.primary}15`
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#E5E7EB'
                    e.target.style.boxShadow = 'none'
                  }}
                  placeholder="Mevcut şifrenizi girin"
                />
                <button
                  type="button"
                  onClick={() => setShowOldPassword(!showOldPassword)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showOldPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Yeni Şifre */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                Yeni Şifre
              </label>
              <div className="relative">
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none transition-all"
                  onFocus={(e) => {
                    e.target.style.borderColor = themeColors.primary
                    e.target.style.boxShadow = `0 0 0 3px ${themeColors.primary}15`
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#E5E7EB'
                    e.target.style.boxShadow = 'none'
                  }}
                  placeholder="Yeni şifrenizi girin"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Yeni Şifre Tekrar */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                Yeni Şifre (Tekrar)
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none transition-all"
                  onFocus={(e) => {
                    e.target.style.borderColor = themeColors.primary
                    e.target.style.boxShadow = `0 0 0 3px ${themeColors.primary}15`
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#E5E7EB'
                    e.target.style.boxShadow = 'none'
                  }}
                  placeholder="Yeni şifrenizi tekrar girin"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Kaydet Butonu */}
            <button
              onClick={handleSavePassword}
              className="w-full px-4 py-2.5 text-sm text-white rounded-lg font-medium transition-all duration-300 mt-6 shadow-sm hover:shadow-md"
              style={{
                background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Şifreyi Kaydet
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
