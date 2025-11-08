'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Save } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { SketchPicker } from 'react-color'
import ChatboxElements from './ChatboxElements'

export default function ChatboxPrivatization({ selectedChatbox, themeColors, isCreatingNew, onCancelCreate, chatboxData, setChatboxData }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isChatboxVisible, setIsChatboxVisible] = useState(true)
  const [isLoadingChatboxData, setIsLoadingChatboxData] = useState(!isCreatingNew && selectedChatbox?.id ? true : false)

  const [colors, setColors] = useState({
    primary: '',
    aiMessage: '',
    userMessage: '',
    borderColor: '',
    aiTextColor: '',
    userTextColor: '',
    buttonPrimary: '',
    buttonBorderColor: '',
    buttonIcon: ''
  })
  const [tempColors, setTempColors] = useState({
    primary: '',
    aiMessage: '',
    userMessage: '',
    borderColor: '',
    aiTextColor: '',
    userTextColor: '',
    buttonPrimary: '',
    buttonBorderColor: '',
    buttonIcon: ''
  })

  // Başlık state'leri
  const [chatboxName, setChatboxName] = useState('')
  const [chatboxTitle, setChatboxTitle] = useState('')
  const [chatboxInitialMessage, setChatboxInitialMessage] = useState('')
  const [tempChatboxName, setTempChatboxName] = useState('')
  const [tempChatboxTitle, setTempChatboxTitle] = useState('')
  const [tempChatboxInitialMessage, setTempChatboxInitialMessage] = useState('')

  // Değişiklik tracking için state
  const [hasChanges, setHasChanges] = useState(false)


  // Color picker modal states
  const [activeColorPicker, setActiveColorPicker] = useState(null)
  
  // Click outside handler için refs
  const colorPickerRefs = useRef({})
  
  // Animasyon state'leri
  const [isVisible, setIsVisible] = useState(false)

  // Portal container için state
  const [portalContainer, setPortalContainer] = useState<HTMLElement | null>(null)

  // Sayfa yüklendiğinde animasyonu başlat
  useEffect(() => {
    setIsVisible(false)
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  // Portal container'ı bul
  useEffect(() => {
    const container = document.getElementById('chatbox-save-buttons-container')
    setPortalContainer(container)
  }, [])

  // Backend'den seçili chatbox verilerini yükle
  useEffect(() => {
    const loadChatboxDetails = async () => {
      if (selectedChatbox?.id && !isCreatingNew) {
        setIsLoadingChatboxData(true)
        try {
          const token = localStorage.getItem('access_token')
          if (!token) {
            setIsLoadingChatboxData(false)
            return
          }

          const response = await fetch(
            `http://localhost:8000/api/v1/chatboxes/${selectedChatbox.id}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          )

          if (response.ok) {
            const chatbox = await response.json()
            console.log('✅ [ChatboxPrivatization] Chatbox detayları yüklendi:', chatbox)

            // Renkleri güncelle
            setColors({
              primary: chatbox.primary_color || '#FF6925',
              aiMessage: chatbox.ai_message_color || '#E5E7EB',
              userMessage: chatbox.user_message_color || '#FF6925',
              borderColor: chatbox.button_border_color || '#FFB380',
              aiTextColor: chatbox.ai_text_color || '#1F2937',
              userTextColor: chatbox.user_text_color || '#FFFFFF',
              buttonPrimary: chatbox.button_primary_color || '#FF6925',
              buttonBorderColor: chatbox.button_border_color || '#FFB380',
              buttonIcon: chatbox.button_icon_color || '#FFFFFF'
            })

            setTempColors({
              primary: chatbox.primary_color || '#FF6925',
              aiMessage: chatbox.ai_message_color || '#E5E7EB',
              userMessage: chatbox.user_message_color || '#FF6925',
              borderColor: chatbox.button_border_color || '#FFB380',
              aiTextColor: chatbox.ai_text_color || '#1F2937',
              userTextColor: chatbox.user_text_color || '#FFFFFF',
              buttonPrimary: chatbox.button_primary_color || '#FF6925',
              buttonBorderColor: chatbox.button_border_color || '#FFB380',
              buttonIcon: chatbox.button_icon_color || '#FFFFFF'
            })

            // Başlıkları güncelle
            setChatboxName(chatbox.name || '')
            setTempChatboxName(chatbox.name || '')
            setChatboxTitle(chatbox.chatbox_title || '')
            setTempChatboxTitle(chatbox.chatbox_title || '')
            setChatboxInitialMessage(chatbox.initial_message || '')
            setTempChatboxInitialMessage(chatbox.initial_message || '')
          }
        } catch (error) {
          console.error('❌ [ChatboxPrivatization] Chatbox detayları yüklenirken hata:', error)
        } finally {
          setIsLoadingChatboxData(false)
        }
      } else if (isCreatingNew) {
        // Yeni chatbox oluşturma modunda default renkleri yükle
        if (chatboxData) {
          const defaultColors = {
            primary: chatboxData.primary_color || '#FF6925',
            aiMessage: chatboxData.ai_message_color || '#E5E7EB',
            userMessage: chatboxData.user_message_color || '#FF6925',
            borderColor: chatboxData.button_border_color || '#FFB380',
            aiTextColor: chatboxData.ai_text_color || '#1F2937',
            userTextColor: chatboxData.user_text_color || '#FFFFFF',
            buttonPrimary: chatboxData.button_primary_color || '#FF6925',
            buttonBorderColor: chatboxData.button_border_color || '#FFB380',
            buttonIcon: chatboxData.button_icon_color || '#FFFFFF'
          }

          setColors(defaultColors)
          setTempColors(defaultColors)

          // Başlıkları da yükle
          setChatboxName(chatboxData.name || '')
          setTempChatboxName(chatboxData.name || '')
          setChatboxTitle(chatboxData.chatbox_title || '')
          setTempChatboxTitle(chatboxData.chatbox_title || '')
          setChatboxInitialMessage(chatboxData.initial_message || '')
          setTempChatboxInitialMessage(chatboxData.initial_message || '')
        }
        setIsLoadingChatboxData(false)
      }
    }

    loadChatboxDetails()
  }, [selectedChatbox?.id, isCreatingNew])

  // Yeni chatbox modunda chatboxData değişince renkleri güncelle
  useEffect(() => {
    if (isCreatingNew && chatboxData) {
      const defaultColors = {
        primary: chatboxData.primary_color || '#FF6925',
        aiMessage: chatboxData.ai_message_color || '#E5E7EB',
        userMessage: chatboxData.user_message_color || '#FF6925',
        borderColor: chatboxData.button_border_color || '#FFB380',
        aiTextColor: chatboxData.ai_text_color || '#1F2937',
        userTextColor: chatboxData.user_text_color || '#FFFFFF',
        buttonPrimary: chatboxData.button_primary_color || '#FF6925',
        buttonBorderColor: chatboxData.button_border_color || '#FFB380',
        buttonIcon: chatboxData.button_icon_color || '#FFFFFF'
      }

      setColors(defaultColors)
      setTempColors(defaultColors)
    }
  }, [isCreatingNew, chatboxData])

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (activeColorPicker) {
        // Tüm color picker konteynerlerini ve renk seçici butonlarını kontrol et
        let clickedInside = false
        
        // Aktif color picker'ın kendisini kontrol et
        const activePickerRef = colorPickerRefs.current[activeColorPicker]
        if (activePickerRef && activePickerRef.contains(event.target)) {
          clickedInside = true
        }
        
        // Renk seçici butonlarını kontrol et
        const colorButtons = document.querySelectorAll('[data-color-button]')
        colorButtons.forEach(button => {
          if (button.contains(event.target)) {
            clickedInside = true
          }
        })
        
        if (!clickedInside) {
          setActiveColorPicker(null)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [activeColorPicker])

  // Animasyon fonksiyonları
  const getCardAnimation = (index) => {
    const baseClasses = "transition-all duration-700 ease-out"
    if (isVisible) {
      return `${baseClasses} opacity-100 translate-y-0 scale-100`
    }
    return `${baseClasses} opacity-0 translate-y-12 scale-90`
  }

  // Chatbox özel animasyon fonksiyonu  
  const getChatboxAnimation = () => {
    if (isVisible) {
      return "opacity-100 translate-y-0 scale-100"
    }
    return "opacity-0 translate-y-12 scale-90"
  }

  const getAnimationDelay = (index) => {
    return `${index * 150}ms`
  }

  const handleChatboxSelect = (chatbox) => {
    setSelectedChatbox(chatbox)
    setIsDropdownOpen(false)
  }

  const handleToggleChatbox = () => {
    setIsChatboxVisible(!isChatboxVisible)
  }

  const handleColorChange = (colorType, newColor) => {
    setTempColors(prev => ({
      ...prev,
      [colorType]: newColor
    }))

    // Değişiklik olduğunu işaretle
    if (!isCreatingNew) {
      setHasChanges(true)
    }

    // Parent state'i güncelle (sadece yeni chatbox modunda)
    if (setChatboxData && isCreatingNew) {
      const colorFieldMap = {
        primary: 'primary_color',
        aiMessage: 'ai_message_color',
        userMessage: 'user_message_color',
        aiTextColor: 'ai_text_color',
        userTextColor: 'user_text_color',
        buttonPrimary: 'button_primary_color',
        buttonBorderColor: 'button_border_color',
        buttonIcon: 'button_icon_color'
      }

      const fieldName = colorFieldMap[colorType]
      if (fieldName) {
        setChatboxData(prev => ({ ...prev, [fieldName]: newColor }))
      }
    }
  }

  const handleNameChange = (value) => {
    setTempChatboxName(value)

    // Değişiklik olduğunu işaretle
    if (!isCreatingNew) {
      setHasChanges(true)
    }

    // Parent state'i güncelle (sadece yeni chatbox modunda)
    if (setChatboxData && isCreatingNew) {
      setChatboxData(prev => ({ ...prev, name: value }))
    }
  }

  const handleTitleChange = (value) => {
    setTempChatboxTitle(value)

    // Değişiklik olduğunu işaretle
    if (!isCreatingNew) {
      setHasChanges(true)
    }

    // Parent state'i güncelle (sadece yeni chatbox modunda)
    if (setChatboxData && isCreatingNew) {
      setChatboxData(prev => ({ ...prev, chatbox_title: value }))
    }
  }

  const handleInitialMessageChange = (value) => {
    setTempChatboxInitialMessage(value)

    // Değişiklik olduğunu işaretle
    if (!isCreatingNew) {
      setHasChanges(true)
    }

    // Parent state'i güncelle (sadece yeni chatbox modunda)
    if (setChatboxData && isCreatingNew) {
      setChatboxData(prev => ({ ...prev, initial_message: value }))
    }
  }

  const handleColorPickerChange = (colorType, colorResult) => {
    handleColorChange(colorType, colorResult.hex)
  }

  const toggleColorPicker = (colorType) => {
    setActiveColorPicker(activeColorPicker === colorType ? null : colorType)
  }

  // Değişiklikleri kaydet
  const handleSaveChanges = async () => {
    if (!selectedChatbox?.id || isCreatingNew) return

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Oturum süreniz dolmuş. Lütfen giriş yapın.')
        return
      }

      const updatePayload = {
        name: tempChatboxName,
        chatbox_title: tempChatboxTitle,
        initial_message: tempChatboxInitialMessage,
        primary_color: tempColors.primary,
        ai_message_color: tempColors.aiMessage,
        user_message_color: tempColors.userMessage,
        ai_text_color: tempColors.aiTextColor,
        user_text_color: tempColors.userTextColor,
        button_primary_color: tempColors.buttonPrimary,
        button_border_color: tempColors.buttonBorderColor,
        button_icon_color: tempColors.buttonIcon
      }

      const response = await fetch(
        `http://localhost:8000/api/v1/chatboxes/${selectedChatbox.id}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updatePayload)
        }
      )

      if (response.ok) {
        const updatedChatbox = await response.json()
        console.log('✅ Chatbox başarıyla güncellendi:', updatedChatbox)

        // Kalıcı state'leri güncelle
        setColors(tempColors)
        setChatboxName(tempChatboxName)
        setChatboxTitle(tempChatboxTitle)
        setChatboxInitialMessage(tempChatboxInitialMessage)

        // Değişiklik bayrağını kapat
        setHasChanges(false)

        alert('Chatbox başarıyla güncellendi!')
      } else {
        const error = await response.json()
        console.error('❌ Chatbox güncellenemedi:', error)
        alert('Chatbox güncellenirken bir hata oluştu: ' + (error.detail || 'Bilinmeyen hata'))
      }
    } catch (error) {
      console.error('❌ Chatbox güncellenirken hata:', error)
      alert('Chatbox güncellenirken bir hata oluştu')
    }
  }

  // Değişiklikleri geri al
  const handleCancelChanges = () => {
    // Temp state'leri kalıcı state'lere geri döndür
    setTempColors(colors)
    setTempChatboxName(chatboxName)
    setTempChatboxTitle(chatboxTitle)
    setTempChatboxInitialMessage(chatboxInitialMessage)

    // Değişiklik bayrağını kapat
    setHasChanges(false)
  }

  // Loading durumunu kontrol et
  if (isLoadingChatboxData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{ borderColor: themeColors.primary }}></div>
          <p className="text-gray-600">Chatbox yükleniyor...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="relative">

      {/* Ana Container - Chatbox ve Özelleştirme yan yana */}
      <div className="flex gap-4 lg:gap-8 flex-col lg:flex-row" style={{ marginLeft: '20px', marginTop: '20px', marginRight: '20px', paddingBottom: '40px' }}>

        {/* Chatbox Elements */}
        <ChatboxElements
          chatboxTitle={tempChatboxTitle || chatboxTitle || 'Chatbox'}
          initialMessage={tempChatboxInitialMessage || chatboxInitialMessage || 'Merhaba!'}
          colors={{
            primary: tempColors.primary || '#FF6925',
            aiMessage: tempColors.aiMessage || '#E5E7EB',
            userMessage: tempColors.userMessage || '#FF6925',
            borderColor: tempColors.buttonBorderColor || tempColors.borderColor || '#FFB380',
            aiTextColor: tempColors.aiTextColor,
            userTextColor: tempColors.userTextColor,
            buttonPrimary: tempColors.buttonPrimary,
            buttonIcon: tempColors.buttonIcon
          }}
          isVisible={isChatboxVisible}
          onToggle={handleToggleChatbox}
          className={getCardAnimation(0)}
          style={{
            animationDelay: getAnimationDelay(0)
          }}
        />

        {/* Chatbox Özelleştirme Kartı */}
        <div
          className={`bg-white border-2 rounded-2xl flex flex-col flex-1 ${getCardAnimation(1)}`}
          style={{
            minHeight: '850px',
            height: 'auto',
            borderColor: '#E5E7EB',
            animationDelay: getAnimationDelay(1),
            maxWidth: '100%',
            minWidth: '0'
          }}
        >
          {/* Özellikler Header */}
          <div className="flex items-center p-3 sm:p-4 lg:p-6 xl:p-8 border-b border-gray-200">
            <h3 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl">
              <span
                className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Chatbox
              </span>
              <span
                className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Özelleştirme
              </span>
            </h3>
          </div>
          
          {/* Özellikler İçerik Alanı */}
          <div className="flex-1 p-3 sm:p-4 lg:p-6 xl:p-8 flex flex-col">
            <div className="space-y-3 sm:space-y-4 lg:space-y-5 xl:space-y-6 flex-1">
            
            {/* Chatbox Başlık */}
            <div>
              <h4 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-2 sm:mb-3 lg:mb-4">Chatbox</h4>
              <div className="flex flex-col gap-2 sm:gap-3 lg:gap-4">
                <div className="flex flex-col gap-1 sm:gap-2">
                  <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox İsmi:</p>
                  <input
                    type="text"
                    value={tempChatboxName}
                    onChange={(e) => handleNameChange(e.target.value)}
                    className="px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-semibold focus:outline-none focus:border-[#6434F8] bg-white w-full text-gray-600"
                    placeholder="örn: destek-chatbox, satis-chatbox"
                  />
                </div>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox Başlık İsmi:</p>
                  <input
                    type="text"
                    value={tempChatboxTitle}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    className="px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-semibold focus:outline-none focus:border-[#6434F8] bg-white w-full text-gray-600"
                    placeholder="örn: Zzen Chatbox, Destek Chatbox"
                  />
                </div>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox İlk Mesaj:</p>
                  <input
                    type="text"
                    value={tempChatboxInitialMessage}
                    onChange={(e) => handleInitialMessageChange(e.target.value)}
                    className="px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-semibold focus:outline-none focus:border-[#6434F8] bg-white w-full text-gray-600"
                    placeholder="örn: Merhaba! Size nasıl yardımcı olabilirim?"
                  />
                </div>
              </div>
            </div>

            {/* Chatbox Tema */}
            <div>
              <h4 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 lg:mb-5 xl:mb-6">Chatbox Tema</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Ana Renk:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('primary')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      🎨
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.primary }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'primary' && (
                    <div ref={(el) => colorPickerRefs.current['primary'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.primary}
                        onChange={(color) => handleColorPickerChange('primary', color)}
                      />
                    </div>
                  )}
                </div>

                {/* AI Mesaj Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">AI Renk:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('aiMessage')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      🤖
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.aiMessage }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'aiMessage' && (
                    <div ref={(el) => colorPickerRefs.current['aiMessage'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.aiMessage}
                        onChange={(color) => handleColorPickerChange('aiMessage', color)}
                      />
                    </div>
                  )}
                </div>

                {/* Kullanıcı Mesaj Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Kullanıcı Renk:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('userMessage')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      👤
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.userMessage }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'userMessage' && (
                    <div ref={(el) => colorPickerRefs.current['userMessage'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.userMessage}
                        onChange={(color) => handleColorPickerChange('userMessage', color)}
                      />
                    </div>
                  )}
                </div>

                {/* AI Mesaj Yazı Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">AI Yazı:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('aiTextColor')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      📝
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.aiTextColor }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'aiTextColor' && (
                    <div ref={(el) => colorPickerRefs.current['aiTextColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.aiTextColor}
                        onChange={(color) => handleColorPickerChange('aiTextColor', color)}
                      />
                    </div>
                  )}
                </div>

                {/* Kullanıcı Mesaj Yazı Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Kullanıcı Yazı:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('userTextColor')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      ✍️
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.userTextColor }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'userTextColor' && (
                    <div ref={(el) => colorPickerRefs.current['userTextColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.userTextColor}
                        onChange={(color) => handleColorPickerChange('userTextColor', color)}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Chatbox Buton */}
            <div>
              <h4 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 lg:mb-5 xl:mb-6">Chatbox Buton</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Ana Renk:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('buttonPrimary')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      🎨
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.buttonPrimary }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'buttonPrimary' && (
                    <div ref={(el) => colorPickerRefs.current['buttonPrimary'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.buttonPrimary}
                        onChange={(color) => handleColorPickerChange('buttonPrimary', color)}
                      />
                    </div>
                  )}
                </div>

                {/* Çerçeve Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Çerçeve Rengi:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('buttonBorderColor')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      🎨
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.buttonBorderColor || tempColors.borderColor }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'buttonBorderColor' && (
                    <div ref={(el) => colorPickerRefs.current['buttonBorderColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.buttonBorderColor || tempColors.borderColor}
                        onChange={(color) => handleColorPickerChange('buttonBorderColor', color)}
                      />
                    </div>
                  )}
                </div>

                {/* Sembol Rengi */}
                <div className="flex flex-col space-y-1.5 md:space-y-1 lg:space-y-2 relative md:flex-1 md:min-w-[60px] lg:min-w-[80px]">
                  <p className="text-xs sm:text-sm font-medium text-gray-700">Sembol Rengi:</p>
                  <div 
                    className="flex items-center space-x-2 md:space-x-1 lg:space-x-2 bg-white rounded-lg md:rounded-lg lg:rounded-xl shadow-sm p-1.5 sm:p-2 md:p-2 lg:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => toggleColorPicker('buttonIcon')}
                    data-color-button
                  >
                    <div className="w-5 sm:w-6 md:w-6 lg:w-7 xl:w-8 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md md:rounded-md lg:rounded-lg flex items-center justify-center text-xs md:text-xs lg:text-sm border border-gray-200">
                      💬
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6 md:h-6 lg:h-7 xl:h-8">
                      <div 
                        className="w-full h-full rounded-md md:rounded-lg border border-gray-400 md:border-[#555] shadow-inner"
                        style={{ backgroundColor: tempColors.buttonIcon || '#FFFFFF' }}
                      ></div>
                    </div>
                  </div>
                  {activeColorPicker === 'buttonIcon' && (
                    <div ref={(el) => colorPickerRefs.current['buttonIcon'] = el} className="absolute top-full left-0 z-50 mt-2">
                      <SketchPicker
                        color={tempColors.buttonIcon || '#FFFFFF'}
                        onChange={(color) => handleColorPickerChange('buttonIcon', color)}
                      />
                    </div>
                  )}
                </div>

              </div>
            </div>

            </div>

          </div>
        </div>

      </div>
    </div>

      {/* Kaydet/Vazgeç Butonları - Portal ile tab menüsüne render et */}
      {!isCreatingNew && hasChanges && portalContainer && createPortal(
        <>
          {/* Vazgeç Butonu */}
          <button
            onClick={handleCancelChanges}
            className="flex items-center justify-center text-gray-600 hover:text-gray-800 p-1 sm:p-1.5 rounded-lg font-medium border border-gray-300 hover:border-gray-400 bg-white hover:bg-gray-50 transition-all duration-300 hover:scale-105"
            title="Vazgeç"
          >
            <ArrowLeft className="w-3.5 sm:w-4 h-3.5 sm:h-4" />
          </button>

          {/* Kaydet Butonu */}
          <button
            onClick={handleSaveChanges}
            className="flex items-center space-x-1 text-white px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg font-medium shadow-sm hover:shadow-md transition-all duration-300 hover:scale-105 text-xs sm:text-sm"
            style={{
              background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
            }}
          >
            <Save className="w-3 sm:w-3.5 h-3 sm:h-3.5" />
            <span>Kaydet</span>
          </button>
        </>,
        portalContainer
      )}
    </>
  )
}