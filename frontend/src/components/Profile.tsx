'use client'

import { User, Mail, Hash, Eye, EyeOff, AtSign } from 'lucide-react'
import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { createPortal } from 'react-dom'

interface ProfileProps {
  themeColors: {
    primary: string
    secondary: string
    text: string
  }
}

interface UserData {
  name: string
  email: string
  userId: string
  username?: string
  profilePhoto: string
  stores: Array<{
    id: number
    name: string
    platform: string
    status: string
  }>
}

interface Brand {
  id: string
  name: string
  slug: string
  description: string | null
  logo_url: string | null
  theme_color: string
  is_active: boolean
  created_at: string
}

export default function Profile({ themeColors }: ProfileProps) {
  const router = useRouter()

  // Kullanıcı verisi state'i
  const [userData, setUserData] = useState<UserData>({
    name: 'Kullanıcı',
    email: 'user@markamind.com',
    userId: 'MM-2024-XXXX',
    profilePhoto: '',
    stores: []
  })
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [brands, setBrands] = useState<Brand[]>([])
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)

  // Brand creation modal states
  const [showBrandModal, setShowBrandModal] = useState(false)
  const [editingBrandId, setEditingBrandId] = useState<string | null>(null)
  const [brandForm, setBrandForm] = useState({
    name: '',
    description: '',
    theme_color: '#3B82F6'
  })
  const [brandLogoFile, setBrandLogoFile] = useState<File | null>(null)
  const [brandLogoPreview, setBrandLogoPreview] = useState<string | null>(null)
  const [isCreatingBrand, setIsCreatingBrand] = useState(false)
  const brandLogoInputRef = useRef<HTMLInputElement>(null)

  // Brand menu states
  const [openMenuBrandId, setOpenMenuBrandId] = useState<string | null>(null)
  const [menuPosition, setMenuPosition] = useState<{ top: number; right: number } | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deletingBrandId, setDeletingBrandId] = useState<string | null>(null)
  const [isDeletingBrand, setIsDeletingBrand] = useState(false)
  const menuButtonRefs = useRef<{ [key: string]: HTMLButtonElement | null }>({})

  // Password change states
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showOldPassword, setShowOldPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  // Avatar upload states
  const [previewAvatar, setPreviewAvatar] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [showAvatarConfirm, setShowAvatarConfirm] = useState(false)
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Logout function - Token süresi dolduğunda çağrılır
  const handleLogout = useCallback(() => {
    // LocalStorage'ı temizle
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')

    // Login sayfasına yönlendir
    router.push('/login')
  }, [router])

  // Backend'den güncel kullanıcı verilerini al - useCallback ile wrap edildi
  const loadUserData = useCallback(async () => {
    try {
      setIsLoadingProfile(true)
      console.log('🔄 Kullanıcı verileri yenileniyor...')

      // Önce backend'den güncel veriyi çek
      const token = localStorage.getItem('access_token')

      if (token) {
        try {
          const response = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })

          // Token süresi dolmuşsa logout yap
          if (response.status === 401) {
            console.error('❌ Token süresi dolmuş. Çıkış yapılıyor...')
            handleLogout()
            return
          }

          if (response.ok) {
            const user = await response.json()

            console.log('✅ Backend user data:', user)
            console.log('🖼️ Avatar URL:', user.avatar_url)

            // localStorage'ı güncel veri ile güncelle
            localStorage.setItem('user_data', JSON.stringify(user))

            // State'i güncelle
            const fullName = user.full_name || user.name || 'Kullanıcı'
            const encodedName = encodeURIComponent(fullName)

            // Clean avatar URL (remove trailing ?)
            const cleanAvatarUrl = user.avatar_url ? user.avatar_url.replace(/\?+$/, '') : null

            const avatarUrl = cleanAvatarUrl
              ? cleanAvatarUrl
              : `https://ui-avatars.com/api/?name=${encodedName}&background=ff6925&color=fff&size=200`

            console.log('📸 Using avatar URL:', avatarUrl)
            console.log('🔍 Avatar URL Length:', avatarUrl?.length)
            console.log('🔍 Is valid URL:', avatarUrl?.startsWith('http'))

            setUserData({
              name: fullName,
              email: user.email || 'user@markamind.com',
              userId: user.id ? `MM-2024-${user.id}` : 'MM-2024-XXXX',
              username: user.username,
              profilePhoto: avatarUrl,
              stores: user.stores || []
            })

            setIsLoadingProfile(false)
            return // Backend'den başarıyla aldık
          }
        } catch (err) {
          console.error('Backend\'den veri çekilemedi, localStorage kullanılacak:', err)
        }
      }

      // Backend'den alınamazsa localStorage'dan oku (fallback)
      const storedUserData = localStorage.getItem('user_data')

      if (storedUserData) {
        const user = JSON.parse(storedUserData)

        console.log('📦 LocalStorage user data:', user)

        const fullName = user.full_name || user.name || 'Kullanıcı'
        const encodedName = encodeURIComponent(fullName)

        // Clean avatar URL (remove trailing ?)
        const cleanAvatarUrl = user.avatar_url ? user.avatar_url.replace(/\?+$/, '') : null

        const avatarUrl = cleanAvatarUrl
          ? cleanAvatarUrl
          : `https://ui-avatars.com/api/?name=${encodedName}&background=ff6925&color=fff&size=200`

        setUserData({
          name: fullName,
          email: user.email || 'user@markamind.com',
          userId: user.id ? `MM-2024-${user.id}` : 'MM-2024-XXXX',
          username: user.username,
          profilePhoto: avatarUrl,
          stores: user.stores || []
        })
      }
      setIsLoadingProfile(false)
    } catch (error) {
      console.error('Kullanıcı verileri yüklenirken hata:', error)
      setIsLoadingProfile(false)
    }
  }, [handleLogout])

  // Backend'den markaları yükle
  const loadBrands = useCallback(async () => {
    try {
      setIsLoadingBrands(true)
      const token = localStorage.getItem('access_token')

      if (!token) {
        console.warn('⚠️ Token bulunamadı')
        setIsLoadingBrands(false)
        return
      }

      const response = await fetch('http://localhost:8000/api/v1/brands/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      // Token süresi dolmuşsa logout yap
      if (response.status === 401) {
        console.error('❌ Token süresi dolmuş. Çıkış yapılıyor...')
        handleLogout()
        return
      }

      if (response.ok) {
        const data = await response.json()
        console.log('✅ Brands loaded:', data)
        // Backend returns pagination response: { items: [...], total: N, page: 1, size: 20, pages: 1 }
        setBrands(data.items || [])
      }
    } catch (error) {
      console.error('Markalar yüklenirken hata:', error)
    } finally {
      setIsLoadingBrands(false)
    }
  }, [handleLogout])

  // Component mount olduğunda veriler yüklensin
  useEffect(() => {
    // İlk yüklemede çalış
    loadUserData()
    loadBrands()
  }, []) // Sadece component mount olduğunda çalışsın

  // Close dropdown menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      if (openMenuBrandId) {
        setOpenMenuBrandId(null)
        setMenuPosition(null)
      }
    }

    if (openMenuBrandId) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [openMenuBrandId])

  // Manuel refresh handler
  const handleManualRefresh = () => {
    loadUserData()
    loadBrands()
  }

  // Brand modal handlers
  const handleBrandFormChange = (field: string, value: string) => {
    setBrandForm(prev => ({ ...prev, [field]: value }))
  }

  const handleBrandLogoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      alert('Sadece resim dosyaları yüklenebilir (JPEG, PNG, WebP)')
      return
    }

    // Validate file size (2MB for logo)
    if (file.size > 2 * 1024 * 1024) {
      alert('Dosya boyutu 2MB\'dan küçük olmalıdır')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setBrandLogoPreview(e.target?.result as string)
      setBrandLogoFile(file)
    }
    reader.readAsDataURL(file)
  }

  const handleCreateBrand = async () => {
    // Validation
    if (!brandForm.name.trim()) {
      alert('Lütfen marka adını girin')
      return
    }

    setIsCreatingBrand(true)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Oturum bulunamadı. Lütfen tekrar giriş yapın.')
        return
      }

      if (editingBrandId) {
        // UPDATE existing brand
        const brandResponse = await fetch(`http://localhost:8000/api/v1/brands/${editingBrandId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            name: brandForm.name,
            description: brandForm.description || null,
            theme_color: brandForm.theme_color
          })
        })

        if (!brandResponse.ok) {
          const errorData = await brandResponse.json()
          throw new Error(errorData.detail || 'Marka güncellenemedi')
        }

        console.log('✅ Brand updated')

        // Upload logo if selected
        if (brandLogoFile) {
          const formData = new FormData()
          formData.append('file', brandLogoFile)

          const logoResponse = await fetch(`http://localhost:8000/api/v1/brands/${editingBrandId}/logo/upload`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
          })

          if (logoResponse.ok) {
            console.log('✅ Logo updated successfully')
          }
        }

        alert('✅ Marka başarıyla güncellendi!')
      } else {
        // CREATE new brand
        const brandResponse = await fetch('http://localhost:8000/api/v1/brands/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            name: brandForm.name,
            description: brandForm.description || null,
            theme_color: brandForm.theme_color
          })
        })

        if (!brandResponse.ok) {
          const errorData = await brandResponse.json()
          throw new Error(errorData.detail || 'Marka oluşturulamadı')
        }

        const newBrand = await brandResponse.json()
        console.log('✅ Brand created:', newBrand)

        // Upload logo if selected
        if (brandLogoFile && newBrand.id) {
          const formData = new FormData()
          formData.append('file', brandLogoFile)

          const logoResponse = await fetch(`http://localhost:8000/api/v1/brands/${newBrand.id}/logo/upload`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
          })

          if (logoResponse.ok) {
            console.log('✅ Logo uploaded successfully')
          }
        }

        alert('✅ Marka başarıyla oluşturuldu!')
      }

      // Success! Refresh brands list
      await loadBrands()

      // Reset form and close modal
      setBrandForm({ name: '', description: '', theme_color: '#3B82F6' })
      setBrandLogoFile(null)
      setBrandLogoPreview(null)
      setEditingBrandId(null)
      setShowBrandModal(false)

    } catch (error) {
      alert(error instanceof Error ? error.message : 'İşlem sırasında bir hata oluştu')
    } finally {
      setIsCreatingBrand(false)
    }
  }

  const handleCancelBrand = () => {
    setBrandForm({ name: '', description: '', theme_color: '#3B82F6' })
    setBrandLogoFile(null)
    setBrandLogoPreview(null)
    setEditingBrandId(null)
    setShowBrandModal(false)
  }

  // Edit brand handler
  const handleEditBrand = (brand: Brand) => {
    setEditingBrandId(brand.id)
    setBrandForm({
      name: brand.name,
      description: brand.description || '',
      theme_color: brand.theme_color
    })
    setBrandLogoPreview(brand.logo_url)
    setShowBrandModal(true)
    setOpenMenuBrandId(null)
  }

  // Delete confirmation handlers
  const handleDeleteClick = (brandId: string) => {
    setDeletingBrandId(brandId)
    setShowDeleteConfirm(true)
    setOpenMenuBrandId(null)
  }

  const handleConfirmDelete = async () => {
    if (!deletingBrandId) return

    setIsDeletingBrand(true)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Oturum bulunamadı. Lütfen tekrar giriş yapın.')
        return
      }

      const response = await fetch(`http://localhost:8000/api/v1/brands/${deletingBrandId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Marka silinemedi')
      }

      console.log('✅ Brand deleted')

      // Refresh brands list
      await loadBrands()

      setShowDeleteConfirm(false)
      setDeletingBrandId(null)

      alert('✅ Marka başarıyla silindi!')

    } catch (error) {
      alert(error instanceof Error ? error.message : 'Marka silinirken bir hata oluştu')
    } finally {
      setIsDeletingBrand(false)
    }
  }

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false)
    setDeletingBrandId(null)
  }

  // Handle menu toggle with position calculation
  const handleMenuToggle = (brandId: string, event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation()
    if (openMenuBrandId === brandId) {
      setOpenMenuBrandId(null)
      setMenuPosition(null)
    } else {
      const button = event.currentTarget
      const rect = button.getBoundingClientRect()
      setMenuPosition({
        top: rect.bottom + 4,
        right: window.innerWidth - rect.right
      })
      setOpenMenuBrandId(brandId)
    }
  }

  // Avatar upload handlers
  const handleAvatarClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      alert('Sadece resim dosyaları yüklenebilir (JPEG, PNG, GIF, WebP)')
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Dosya boyutu 5MB\'dan küçük olmalıdır')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewAvatar(e.target?.result as string)
      setSelectedFile(file)
      setShowAvatarConfirm(true)
    }
    reader.readAsDataURL(file)
  }

  const handleAvatarConfirm = async () => {
    if (!selectedFile) return

    setIsUploadingAvatar(true)
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Oturum bulunamadı. Lütfen tekrar giriş yapın.')
        return
      }

      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('http://localhost:8000/api/v1/users/avatar/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Avatar yüklenemedi')
      }

      const data = await response.json()

      console.log('🎉 Avatar upload başarılı! Yeni avatar:', data.avatar_url)

      // Avatar upload başarılı, tüm kullanıcı verilerini yeniden yükle
      await loadUserData()
      await loadBrands()

      // TEMİZLE: Preview ve confirmation state'lerini sıfırla
      setShowAvatarConfirm(false)
      setPreviewAvatar(null)
      setSelectedFile(null)

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      alert('✅ Profil fotoğrafı başarıyla güncellendi!')

    } catch (error) {
      alert(error instanceof Error ? error.message : 'Avatar yüklenirken bir hata oluştu')
    } finally {
      setIsUploadingAvatar(false)
    }
  }

  const handleAvatarCancel = () => {
    setPreviewAvatar(null)
    setSelectedFile(null)
    setShowAvatarConfirm(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSavePassword = async () => {
    // Reset messages
    setPasswordError('')
    setPasswordSuccess('')

    // Validation
    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError('Lütfen tüm alanları doldurun')
      return
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('Yeni şifreler eşleşmiyor!')
      return
    }

    if (newPassword.length < 8) {
      setPasswordError('Yeni şifre en az 8 karakter olmalıdır')
      return
    }

    setIsChangingPassword(true)

    try {
      // Get token from localStorage
      const token = localStorage.getItem('access_token')

      if (!token) {
        setPasswordError('Oturum bulunamadı. Lütfen tekrar giriş yapın.')
        return
      }

      const response = await fetch('http://localhost:8000/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: oldPassword,
          new_password: newPassword,
          confirm_new_password: confirmPassword
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Şifre değiştirme başarısız')
      }

      setPasswordSuccess('Şifre başarıyla güncellendi!')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')

      // Şifre değişikliğinden sonra kullanıcı verilerini yenile
      await loadUserData()
      await loadBrands()
    } catch (error) {
      setPasswordError(error instanceof Error ? error.message : 'Bir hata oluştu')
    } finally {
      setIsChangingPassword(false)
    }
  }

  return (
    <>
      {/* Dropdown Menu Portal */}
      {openMenuBrandId && menuPosition && typeof window !== 'undefined' && createPortal(
        <div
          className="fixed bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-[9999] min-w-[120px]"
          style={{
            top: `${menuPosition.top}px`,
            right: `${menuPosition.right}px`
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => {
              const brand = brands.find(b => b.id === openMenuBrandId)
              if (brand) handleEditBrand(brand)
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <span>Düzenle</span>
          </button>
          <button
            onClick={() => handleDeleteClick(openMenuBrandId)}
            className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center space-x-2"
            style={{ color: themeColors.primary }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>Sil</span>
          </button>
        </div>,
        document.body
      )}

      <div className="flex flex-col lg:flex-row gap-4 lg:gap-6 w-full mt-4 lg:mt-6 px-2 sm:px-4">

      {/* Delete Confirmation Modal - Bottom Right */}
      {showDeleteConfirm && (
        <div className="fixed bottom-6 right-6 z-50 bg-white border-2 rounded-2xl shadow-2xl p-6 max-w-sm w-full animate-slide-from-right"
             style={{ borderColor: themeColors.primary }}>
          <div className="flex flex-col space-y-4">
            {/* Icon */}
            <div className="flex justify-center">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${themeColors.primary}20` }}
              >
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: themeColors.primary }}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
            </div>

            {/* Message */}
            <div className="text-center">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Markayı Sil</h3>
              <p className="text-sm text-gray-600">
                Bu markayı silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleCancelDelete}
                disabled={isDeletingBrand}
                className="flex-1 px-4 py-2.5 text-sm text-gray-700 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Vazgeç
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={isDeletingBrand}
                className="flex-1 px-4 py-2.5 text-sm text-white rounded-lg font-medium transition-all duration-300 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                {isDeletingBrand ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Siliniyor...</span>
                  </div>
                ) : (
                  'Evet, Sil'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Brand Creation Modal - Bottom Right */}
      {showBrandModal && (
        <div className="fixed bottom-6 right-6 z-50 bg-white border-2 rounded-2xl shadow-2xl p-6 max-w-md w-full animate-slide-from-right"
             style={{ borderColor: themeColors.primary }}>
          <div className="flex flex-col space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-gray-900">{editingBrandId ? 'Marka Düzenle' : 'Yeni Marka Oluştur'}</h3>
              <button
                onClick={handleCancelBrand}
                disabled={isCreatingBrand}
                className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Logo Upload */}
            <div className="flex flex-col items-center space-y-2">
              <div
                onClick={() => brandLogoInputRef.current?.click()}
                className="w-24 h-24 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-gray-400 transition-all overflow-hidden"
                style={{ backgroundColor: brandLogoPreview ? 'transparent' : brandForm.theme_color + '20' }}
              >
                {brandLogoPreview ? (
                  <img src={brandLogoPreview} alt="Logo preview" className="w-full h-full object-cover" />
                ) : (
                  <div className="flex flex-col items-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <p className="text-xs text-gray-500 mt-1">Logo</p>
                  </div>
                )}
              </div>
              <input
                ref={brandLogoInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleBrandLogoSelect}
                className="hidden"
              />
              <p className="text-xs text-gray-500">Logo yüklemek için tıklayın</p>
            </div>

            {/* Brand Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Marka Adı *</label>
              <input
                type="text"
                value={brandForm.name}
                onChange={(e) => handleBrandFormChange('name', e.target.value)}
                placeholder="Örn: Acme Corp"
                disabled={isCreatingBrand}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 text-gray-900 disabled:opacity-50"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Açıklama</label>
              <textarea
                value={brandForm.description}
                onChange={(e) => handleBrandFormChange('description', e.target.value)}
                placeholder="Markanız hakkında kısa bir açıklama..."
                rows={3}
                disabled={isCreatingBrand}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 text-gray-900 resize-none disabled:opacity-50"
              />
            </div>

            {/* Theme Color */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tema Rengi</label>
              <div className="flex items-center space-x-3">
                <input
                  type="color"
                  value={brandForm.theme_color}
                  onChange={(e) => handleBrandFormChange('theme_color', e.target.value)}
                  disabled={isCreatingBrand}
                  className="w-12 h-12 rounded-lg border-2 border-gray-200 cursor-pointer disabled:opacity-50"
                />
                <input
                  type="text"
                  value={brandForm.theme_color}
                  onChange={(e) => handleBrandFormChange('theme_color', e.target.value)}
                  placeholder="#3B82F6"
                  disabled={isCreatingBrand}
                  className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 text-gray-900 font-mono text-sm disabled:opacity-50"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-2">
              <button
                onClick={handleCancelBrand}
                disabled={isCreatingBrand}
                className="flex-1 px-4 py-2.5 text-sm text-gray-700 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                İptal Et
              </button>
              <button
                onClick={handleCreateBrand}
                disabled={isCreatingBrand || !brandForm.name.trim()}
                className="flex-1 px-4 py-2.5 text-sm text-white rounded-lg font-medium transition-all duration-300 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                {isCreatingBrand ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Kaydediliyor...</span>
                  </div>
                ) : (
                  'Kaydet'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Avatar Confirmation Dialog - Bottom Right */}
      {showAvatarConfirm && (
        <div className="fixed bottom-6 right-6 z-50 bg-white border-2 rounded-2xl shadow-2xl p-5 max-w-sm animate-slide-from-right"
             style={{ borderColor: themeColors.primary }}>
          <div className="flex flex-col space-y-4">
            {/* Preview Image */}
            <div className="flex items-center space-x-3">
              <img
                src={previewAvatar || ''}
                alt="Preview"
                className="w-16 h-16 rounded-full object-cover border-2"
                style={{ borderColor: themeColors.primary }}
              />
              <div>
                <h4 className="text-sm font-semibold text-gray-900">Profil Fotoğrafını Onayla</h4>
                <p className="text-xs text-gray-500">Bu fotoğrafı kullanmak istiyor musunuz?</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={handleAvatarConfirm}
                disabled={isUploadingAvatar}
                className="flex-1 px-4 py-2 text-sm text-white rounded-lg font-medium transition-all duration-300 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                {isUploadingAvatar ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Yükleniyor...</span>
                  </div>
                ) : (
                  'Evet, Kullan'
                )}
              </button>
              <button
                onClick={handleAvatarCancel}
                disabled={isUploadingAvatar}
                className="flex-1 px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                İptal
              </button>
            </div>
          </div>
        </div>
      )}


      {/* Profil Bilgileri Kartı */}
      <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 min-h-[600px] lg:min-h-[700px]" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
        <div className="flex items-center justify-between px-4 sm:px-6 py-4 sm:py-5 border-b border-gray-200">
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
          {/* Manuel Yenile Butonu */}
          <button
            onClick={handleManualRefresh}
            disabled={isLoadingProfile || isLoadingBrands}
            className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Profil bilgilerini ve markaları yenile"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`w-5 h-5 ${(isLoadingProfile || isLoadingBrands) ? 'animate-spin' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style={{ color: themeColors.primary }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        <div className="flex-1 p-4 sm:p-5 lg:p-6 flex flex-col space-y-5 overflow-y-auto">

          {/* Profil Fotoğrafı */}
          <div className="flex flex-col items-center py-2">
            <div className="relative group">
              {isLoadingProfile ? (
                <div
                  className="w-20 h-20 sm:w-24 sm:h-24 rounded-full border-3 shadow-lg flex items-center justify-center bg-gray-100"
                  style={{ borderColor: themeColors.primary }}
                >
                  <div className="w-8 h-8 border-3 border-gray-300 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <img
                  src={userData.profilePhoto || `https://ui-avatars.com/api/?name=${encodeURIComponent(userData.name)}&background=ff6925&color=fff&size=200`}
                  alt={userData.name}
                  crossOrigin="anonymous"
                  onClick={handleAvatarClick}
                  onLoad={(e) => {
                    console.log('✅ Avatar loaded successfully:', userData.profilePhoto)
                  }}
                  onError={(e) => {
                    console.error('❌ Avatar yükleme hatası:', userData.profilePhoto)
                    console.error('❌ Error event:', e)
                    // Fallback to initials
                    e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(userData.name)}&background=ff6925&color=fff&size=200`
                  }}
                  className="w-20 h-20 sm:w-24 sm:h-24 rounded-full object-cover border-3 shadow-lg cursor-pointer transition-all duration-300 hover:opacity-80 hover:scale-105"
                  style={{ borderColor: themeColors.primary, backgroundColor: 'transparent' }}
                />
              )}
              {/* Upload overlay - only show when not loading */}
              {!isLoadingProfile && (
                <div
                  onClick={handleAvatarClick}
                  className="absolute inset-0 rounded-full flex items-center justify-center transition-all duration-300 cursor-pointer pointer-events-none group-hover:pointer-events-auto"
                  style={{
                    backgroundColor: 'transparent',
                    zIndex: 10
                  }}
                >
                  <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-40 rounded-full transition-opacity duration-300 pointer-events-none"></div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 relative z-10"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              )}
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">Fotoğrafı değiştirmek için tıklayın</p>
          </div>

          {/* Kullanıcı Bilgileri */}
          <div className="space-y-3">
            {/* İsim ve Email - Yan Yana */}
            <div className="grid grid-cols-2 gap-3">
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
            </div>

            {/* Kullanıcı Adı */}
            {userData.username && (
              <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${themeColors.primary}15` }}
                >
                  <AtSign className="w-4 h-4" style={{ color: themeColors.primary }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 mb-0.5">Kullanıcı Adı</p>
                  <p className="text-sm font-semibold text-gray-900 truncate">@{userData.username}</p>
                </div>
              </div>
            )}

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

          {/* Markalarım */}
          <div className="pt-3 border-t border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4" style={{ color: themeColors.primary }}>
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5"></path>
                  <path d="M2 12l10 5 10-5"></path>
                </svg>
                <h4 className="text-sm font-semibold text-gray-900">Markalarım</h4>
              </div>
              <button
                onClick={() => setShowBrandModal(true)}
                className="w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110 hover:shadow-md"
                style={{
                  backgroundColor: `${themeColors.primary}20`,
                  color: themeColors.primary
                }}
                title="Yeni marka ekle"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
            </div>

            {isLoadingBrands ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-gray-300 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : brands.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-xs text-gray-500">Henüz marka eklenmemiş</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                {brands.map((brand) => (
                  <div
                    key={brand.id}
                    className="relative flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
                    style={{
                      backgroundColor: brand.is_active ? `${themeColors.primary}05` : 'transparent'
                    }}
                  >
                    {/* Logo */}
                    <div
                      className="w-12 h-12 rounded-lg flex-shrink-0 flex items-center justify-center overflow-hidden border border-gray-200"
                      style={{ backgroundColor: brand.logo_url ? 'transparent' : brand.theme_color }}
                    >
                      {brand.logo_url ? (
                        <img
                          src={brand.logo_url}
                          alt={brand.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Fallback to theme color with first letter
                            e.currentTarget.style.display = 'none'
                            e.currentTarget.parentElement!.innerHTML = `<span class="text-white text-lg font-bold">${brand.name.charAt(0)}</span>`
                          }}
                        />
                      ) : (
                        <span className="text-white text-lg font-bold">{brand.name.charAt(0)}</span>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-semibold text-gray-900 truncate">{brand.name}</p>
                      </div>
                      {brand.description && (
                        <p className="text-xs text-gray-500 line-clamp-2">{brand.description}</p>
                      )}
                      {!brand.description && (
                        <p className="text-xs text-gray-400 italic">Açıklama yok</p>
                      )}
                    </div>

                    {/* 3-dot Menu */}
                    <div className="absolute top-2 right-2">
                      <button
                        onClick={(e) => handleMenuToggle(brand.id, e)}
                        className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
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

            {/* Error Message */}
            {passwordError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2 animate-slide-from-right">
                <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-xs text-red-700">{passwordError}</p>
              </div>
            )}

            {/* Success Message */}
            {passwordSuccess && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-2 animate-slide-from-right">
                <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <p className="text-xs text-green-700">{passwordSuccess}</p>
              </div>
            )}

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
                  className="w-full px-3 py-2.5 text-sm text-gray-900 border border-gray-200 rounded-lg focus:outline-none transition-all"
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
                  className="w-full px-3 py-2.5 text-sm text-gray-900 border border-gray-200 rounded-lg focus:outline-none transition-all"
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
                  className="w-full px-3 py-2.5 text-sm text-gray-900 border border-gray-200 rounded-lg focus:outline-none transition-all"
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
              disabled={isChangingPassword}
              className="w-full px-4 py-2.5 text-sm text-white rounded-lg font-medium transition-all duration-300 mt-6 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              style={{
                background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
              }}
              onMouseEnter={(e) => {
                if (!isChangingPassword) {
                  e.currentTarget.style.transform = 'translateY(-1px)'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              {isChangingPassword ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Kaydediliyor...</span>
                </>
              ) : (
                <span>Şifreyi Kaydet</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
    </>
  )
}
