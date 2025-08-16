'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Undo2, Save } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { SketchPicker } from 'react-color'
import ChatboxElements from './ChatboxElements'

// Örnek chatbox verileri
const chatboxList = [
  { id: 1, name: 'Zzen Chatbox', status: 'active', messages: 1247 },
  { id: 2, name: 'Imuntus Kids Chatbox', status: 'active', messages: 890 },
  { id: 3, name: 'Mag4ever Chatbox', status: 'inactive', messages: 456 }
]

export default function ChatboxPrivatization({ themeColors }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState(chatboxList[0])
  const [isChatboxVisible, setIsChatboxVisible] = useState(true)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! It\'s Orbina here!', sender: 'bot', timestamp: new Date() }
  ])
  const [colors, setColors] = useState({
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA',
    buttonBorderColor: '#B794F6',
    buttonIcon: '#FFFFFF'
  })
  const [tempColors, setTempColors] = useState({
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA',
    buttonBorderColor: '#B794F6',
    buttonIcon: '#FFFFFF'
  })
  
  // Başlık state'leri
  const [chatboxTitle, setChatboxTitle] = useState('Zzen Chatbox')
  const [chatboxInitialMessage, setChatboxInitialMessage] = useState("Hello! It's Orbina here!")
  const [tempChatboxTitle, setTempChatboxTitle] = useState('Zzen Chatbox')
  const [tempChatboxInitialMessage, setTempChatboxInitialMessage] = useState("Hello! It's Orbina here!")
  
  
  // Değişiklik takibi
  const [hasChanges, setHasChanges] = useState(false)
  
  // Color picker modal states
  const [activeColorPicker, setActiveColorPicker] = useState(null)
  
  // Click outside handler için refs
  const colorPickerRefs = useRef({})
  
  // Animasyon state'leri
  const [isVisible, setIsVisible] = useState(false)

  // Sayfa yüklendiğinde animasyonu başlat
  useEffect(() => {
    setIsVisible(false)
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

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

  const handleSendMessage = () => {
    if (message.trim()) {
      // Kullanıcı mesajını ekle
      const userMessage = {
        id: messages.length + 1,
        text: message.trim(),
        sender: 'user',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, userMessage])
      setMessage('')
      
      // Demo bot cevabı (2 saniye sonra)
      setTimeout(() => {
        const botMessage = {
          id: messages.length + 2,
          text: 'Mesajınız için teşekkürler! Bu bir demo chatbox\'tır. Gerçek bir backend bağlantısı henüz mevcut değildir.',
          sender: 'bot',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, botMessage])
      }, 2000)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  const handleColorChange = (colorType, newColor) => {
    setTempColors(prev => ({
      ...prev,
      [colorType]: newColor
    }))
    setHasChanges(true)
  }

  const handleTitleChange = (value) => {
    setTempChatboxTitle(value)
    setHasChanges(true)
  }

  const handleInitialMessageChange = (value) => {
    setTempChatboxInitialMessage(value)
    setHasChanges(true)
  }


  const applyChanges = () => {
    setColors(tempColors)
    setChatboxTitle(tempChatboxTitle)
    setChatboxInitialMessage(tempChatboxInitialMessage)
    setHasChanges(false)
  }

  const resetChanges = () => {
    setTempColors(colors)
    setTempChatboxTitle(chatboxTitle)
    setTempChatboxInitialMessage(chatboxInitialMessage)
    setHasChanges(false)
  }

  const handleColorPickerChange = (colorType, colorResult) => {
    handleColorChange(colorType, colorResult.hex)
  }

  const toggleColorPicker = (colorType) => {
    setActiveColorPicker(activeColorPicker === colorType ? null : colorType)
  }

  return (
    <div className="relative">
      
      {/* Ana Container - Chatbox ve Özelleştirme yan yana */}
      <div className="flex gap-4 lg:gap-8 flex-col xl:flex-row" style={{ marginLeft: '20px', marginTop: '20px', marginRight: '20px', paddingBottom: '40px' }}>
        
        {/* Chatbox Elements */}
        <ChatboxElements
          chatboxTitle={tempChatboxTitle}
          initialMessage={tempChatboxInitialMessage}
          colors={{
            primary: tempColors.primary,
            aiMessage: tempColors.aiMessage,
            userMessage: tempColors.userMessage,
            borderColor: tempColors.buttonBorderColor || tempColors.borderColor,
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
            height: '850px', 
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
              <div className="flex flex-col sm:flex-col lg:flex-row gap-2 sm:gap-3 lg:gap-4 xl:gap-8">
                <div className="flex flex-col sm:flex-col lg:flex-row lg:items-center gap-1 sm:gap-2">
                  <p className="text-xs sm:text-sm lg:text-base text-gray-700 whitespace-nowrap">Chatbox Başlık İsmi:</p>
                  <input
                    type="text"
                    value={tempChatboxTitle}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    className="px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-semibold focus:outline-none focus:border-[#6434F8] bg-white flex-1 min-w-0 text-gray-600"
                  />
                </div>
                <div className="flex flex-col sm:flex-col lg:flex-row lg:items-center gap-1 sm:gap-2">
                  <p className="text-xs sm:text-sm lg:text-base text-gray-700 whitespace-nowrap">Chatbox İlk Mesaj:</p>
                  <input
                    type="text"
                    value={tempChatboxInitialMessage}
                    onChange={(e) => handleInitialMessageChange(e.target.value)}
                    className="px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-semibold focus:outline-none focus:border-[#6434F8] bg-white flex-1 min-w-0 text-gray-600"
                  />
                </div>
              </div>
            </div>

            {/* Chatbox Tema */}
            <div>
              <h4 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 lg:mb-5 xl:mb-6">Chatbox Tema</h4>
              <div className="grid grid-cols-1 md:flex md:gap-1 lg:gap-2 xl:gap-4 md:flex-wrap gap-3 sm:gap-4">
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
              <div className="grid grid-cols-1 md:flex md:gap-1 lg:gap-2 xl:gap-4 md:flex-wrap gap-3 sm:gap-4">
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

            {/* Kaydet ve Geri Al Butonları */}
            {hasChanges && (
              <div className="flex justify-center space-x-2 sm:space-x-4 p-3 sm:p-4 lg:p-6">
                <button
                  onClick={resetChanges}
                  className="flex items-center justify-center bg-gray-100 hover:bg-gray-200 p-2 sm:p-3 rounded-lg transition-all duration-300 hover:scale-105 border border-gray-300"
                >
                  <Undo2 className="w-4 sm:w-5 h-4 sm:h-5 text-gray-600" />
                </button>
                <button
                  onClick={applyChanges}
                  className="flex items-center space-x-1 sm:space-x-2 text-white px-4 sm:px-6 lg:px-8 py-2 sm:py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base"
                  style={{ backgroundColor: '#6434F8' }}
                >
                  <Save className="w-4 sm:w-5 h-4 sm:h-5" />
                  <span>Kaydet</span>
                </button>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  )
}