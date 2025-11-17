'use client'

import { ArrowLeft, Plus, MessageSquare, Upload, X, Save } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { SketchPicker } from 'react-color'
import ChatboxElements from './ChatboxElements'

export default function ChatboxCreate({ themeColors, storeList, onBack, onSave }) {
  // Yeni chatbox state'i
  const [newChatbox, setNewChatbox] = useState({
    name: '',
    description: '',
    chatboxTitle: 'Zzen Chatbox',
    initialMessage: "Hello! It's Orbina here!",
    colors: {
      primary: '#7B4DFA',
      aiMessage: '#E5E7EB',
      userMessage: '#7B4DFA',
      borderColor: '#B794F6',
      aiTextColor: '#1F2937',
      userTextColor: '#FFFFFF',
      buttonPrimary: '#7B4DFA',
      buttonBorderColor: '#B794F6',
      buttonIcon: '#FFFFFF'
    },
    status: 'active'
  })

  // UI state'leri
  const [activeColorPicker, setActiveColorPicker] = useState(null)
  const [isChatboxVisible, setIsChatboxVisible] = useState(true)

  // Refs
  const colorPickerRefs = useRef({})

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Color picker click outside
      if (activeColorPicker) {
        let clickedInside = false

        const activePickerRef = colorPickerRefs.current[activeColorPicker]
        if (activePickerRef && activePickerRef.contains(event.target)) {
          clickedInside = true
        }

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

  const toggleColorPicker = (colorType) => {
    setActiveColorPicker(activeColorPicker === colorType ? null : colorType)
  }

  const handleColorPickerChange = (colorType, color) => {
    setNewChatbox(prev => ({
      ...prev,
      colors: {
        ...prev.colors,
        [colorType]: color.hex
      }
    }))
  }

  const handleSave = () => {
    if (onSave) {
      onSave(newChatbox)
    }
  }

  const colorPickerConfig = [
    { key: 'primary', label: 'Ana Renk', emoji: '🎨' },
    { key: 'aiMessage', label: 'AI Mesaj', emoji: '🤖' },
    { key: 'userMessage', label: 'Kullanıcı Mesaj', emoji: '👤' },
    { key: 'aiTextColor', label: 'AI Yazı Rengi', emoji: '📝' },
    { key: 'userTextColor', label: 'Kullanıcı Yazı', emoji: '✍️' },
    { key: 'buttonPrimary', label: 'Buton Ana Renk', emoji: '🔘' },
    { key: 'buttonBorderColor', label: 'Buton Çerçeve', emoji: '⭕' },
    { key: 'buttonIcon', label: 'Buton Sembol', emoji: '💬' }
  ]

  return (
    <div className="relative">

      {/* Banner */}
      <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 mb-4 sm:mb-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
            {/* Geri Dön Butonu */}
            <button
              onClick={onBack}
              className="p-1.5 sm:p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 sm:w-5 h-4 sm:h-5 text-[#666]" />
            </button>

            {/* İkon */}
            <div
              className="w-8 sm:w-10 lg:w-12 h-8 sm:h-10 lg:h-12 rounded-full flex items-center justify-center"
              style={{
                background: `linear-gradient(to bottom right, ${themeColors.primary}10, ${themeColors.secondary}10)`,
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: `${themeColors.primary}20`
              }}
            >
              <Plus
                className="w-4 sm:w-5 lg:w-6 h-4 sm:h-5 lg:h-6"
                style={{ color: themeColors.primary }}
              />
            </div>

            {/* Başlık */}
            <div>
              <h2 className="text-base sm:text-lg lg:text-xl font-bold text-[#1F1F1F]">
                Yeni Chatbox Ekle
              </h2>
              <p className="text-xs sm:text-sm text-[#666]">
                Chatbox bilgilerini girin
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="flex flex-col xl:flex-row gap-4 sm:gap-6 xl:gap-8 mx-3 sm:mx-6 lg:mx-12 xl:mx-20">

        {/* Sol Taraf - Form */}
        <div className="w-full xl:w-1/2">
          <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-fit space-y-3 sm:space-y-4 lg:space-y-6">

            {/* Chatbox İsmi */}
            <div>
              <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                Chatbox İsmi
              </label>
              <input
                type="text"
                value={newChatbox.name}
                onChange={(e) => setNewChatbox({...newChatbox, name: e.target.value})}
                placeholder="Chatbox ismini girin (örn: TechMall AI Assistant)"
                className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 placeholder-gray-500 text-sm sm:text-base"
              />
            </div>

            {/* Chatbox Açıklaması */}
            <div>
              <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                Chatbox Açıklaması
              </label>
              <textarea
                value={newChatbox.description}
                onChange={(e) => setNewChatbox({...newChatbox, description: e.target.value})}
                placeholder="Chatbox'ınızın ne işe yaradığını açıklayın"
                rows={4}
                className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors resize-none text-gray-900 placeholder-gray-500 text-sm sm:text-base"
              />
            </div>

            {/* Renk Seçimi */}
            <div>
              <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-2 sm:mb-3">
                Chatbox Renkleri
              </label>

              <div className="grid grid-cols-2 gap-3 sm:gap-4">
                {colorPickerConfig.map((config) => (
                  <div key={config.key} className="flex flex-col space-y-1.5 sm:space-y-2 relative">
                    <label className="block text-xs text-[#666] mb-1">
                      {config.label}
                    </label>
                    <div
                      data-color-button
                      className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-2 sm:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => toggleColorPicker(config.key)}
                    >
                      <div className="w-6 sm:w-7 h-6 sm:h-7 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs sm:text-sm border border-gray-200">
                        {config.emoji}
                      </div>
                      <div className="relative flex-1 h-6 sm:h-7">
                        <div
                          className="w-full h-full rounded-md border border-gray-400 shadow-inner"
                          style={{ backgroundColor: newChatbox.colors[config.key] }}
                        ></div>
                      </div>
                    </div>
                    {activeColorPicker === config.key && (
                      <div
                        ref={(el) => colorPickerRefs.current[config.key] = el}
                        className="absolute top-full left-0 z-50 mt-2"
                      >
                        <SketchPicker
                          color={newChatbox.colors[config.key]}
                          onChange={(color) => handleColorPickerChange(config.key, color)}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Butonlar */}
            <div className="flex items-center space-x-2 sm:space-x-3 pt-3 sm:pt-4">
              <button
                onClick={onBack}
                className="flex items-center justify-center text-gray-600 hover:text-gray-800 p-1 sm:p-1.5 rounded-lg font-medium border border-gray-300 hover:border-gray-400 bg-white hover:bg-gray-50 transition-all duration-300 hover:scale-105"
                title="Vazgeç"
              >
                <ArrowLeft className="w-3.5 sm:w-4 h-3.5 sm:h-4" />
              </button>
              <button
                onClick={handleSave}
                disabled={!newChatbox.name}
                className="flex items-center space-x-1 text-white px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg font-medium shadow-sm hover:shadow-md transition-all duration-300 hover:scale-105 text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                }}
              >
                <Save className="w-3 sm:w-3.5 h-3 sm:h-3.5" />
                <span>Kaydet</span>
              </button>
            </div>

          </div>
        </div>

        {/* Sağ Taraf - Önizleme */}
        <div className="w-full xl:w-1/2">
          <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-fit">
            <h3 className="text-base sm:text-lg font-bold mb-3 sm:mb-4">
              <span
                className="bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Canlı Önizleme
              </span>
            </h3>

            {/* Chatbox Önizleme */}
            <div className="relative" style={{ minHeight: '850px', width: '100%' }}>
              <div className="absolute bottom-0 right-0">
                <ChatboxElements
                  chatboxTitle={newChatbox.chatboxTitle}
                  initialMessage={newChatbox.initialMessage}
                  colors={newChatbox.colors}
                  isVisible={isChatboxVisible}
                  onToggle={() => setIsChatboxVisible(!isChatboxVisible)}
                />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
