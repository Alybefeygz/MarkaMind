'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Undo2, Copy } from 'lucide-react'
import { useState, useEffect } from 'react'
import ChatboxPrivatization from './ChatboxPrivatization'
import ChatboxElements from './ChatboxElements'

// Örnek chatbox verileri
const chatboxList = [
  { id: 1, name: 'Zzen Chatbox', status: 'active', messages: 1247 },
  { id: 2, name: 'Imuntus Kids Chatbox', status: 'active', messages: 890 },
  { id: 3, name: 'Mag4ever Chatbox', status: 'inactive', messages: 456 }
]

export default function ChatboxManagement({ activeTab, themeColors }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState(chatboxList[0])
  const [isChatboxVisible, setIsChatboxVisible] = useState(true)
  const [colors, setColors] = useState({
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA'
  })
  const [tempColors, setTempColors] = useState({
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA'
  })
  const [hasColorChanges, setHasColorChanges] = useState(false)
  
  // Veri kaynağı metni state'leri
  const [originalText, setOriginalText] = useState("Bu chatbox, yapay zeka destekli müşteri hizmetleri sağlar ve kullanıcı sorularını otomatik olarak yanıtlar. Modern teknoloji ile donatılmış bu")
  const [currentText, setCurrentText] = useState("Bu chatbox, yapay zeka destekli müşteri hizmetleri sağlar ve kullanıcı sorularını otomatik olarak yanıtlar. Modern teknoloji ile donatılmış bu")
  const [hasTextChanges, setHasTextChanges] = useState(false)
  
  // PDF'lerin durumu ve dropdown state'leri
  const [pdfStatuses, setPdfStatuses] = useState({
    'urun_katalog.pdf': 'aktif',
    'sss_dokuman.pdf': 'aktif', 
    'kullanim_kilavuzu.pdf': 'aktif'
  })
  const [openDropdowns, setOpenDropdowns] = useState({})
  
  // Animasyon state'leri
  const [isVisible, setIsVisible] = useState(false)

  // Sayfa yüklendiğinde ve sekme değiştiğinde animasyonu başlat
  useEffect(() => {
    if (activeTab === 'Önizleme') {
      setIsVisible(false)
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      setIsVisible(false)
    }
  }, [activeTab])

  // İlk yüklemede animasyonu başlat
  useEffect(() => {
    if (activeTab === 'Önizleme') {
      setIsVisible(false)
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [])

  // Animasyon fonksiyonları
  const getCardAnimation = (index) => {
    const baseClasses = "transition-all duration-700 ease-out"
    if (isVisible && activeTab === 'Önizleme') {
      return `${baseClasses} translate-y-0 scale-100`
    }
    return `${baseClasses} translate-y-12 scale-90`
  }

  // Chatbox özel animasyon fonksiyonu  
  const getChatboxAnimation = () => {
    if (isVisible && activeTab === 'Önizleme') {
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
    setHasColorChanges(true)
  }

  const applyColors = () => {
    setColors(tempColors)
    setHasColorChanges(false)
  }

  const undoColorChanges = () => {
    setTempColors(colors)
    setHasColorChanges(false)
  }

  // Metin değişiklik fonksiyonları
  const handleTextChange = (e) => {
    const newText = e.target.value
    setCurrentText(newText)
    setHasTextChanges(newText !== originalText)
  }

  const saveTextChanges = () => {
    setOriginalText(currentText)
    setHasTextChanges(false)
  }

  const undoTextChanges = () => {
    setCurrentText(originalText)
    setHasTextChanges(false)
  }

  // PDF durum değiştirme fonksiyonları
  const toggleDropdown = (pdfName) => {
    setOpenDropdowns(prev => ({
      ...prev,
      [pdfName]: !prev[pdfName]
    }))
  }

  const changePdfStatus = (pdfName, newStatus) => {
    setPdfStatuses(prev => ({
      ...prev,
      [pdfName]: newStatus
    }))
    setOpenDropdowns(prev => ({
      ...prev,
      [pdfName]: false
    }))
  }


  // Sekme kontrolü
  if (activeTab === 'Özelleştirme') {
    return <ChatboxPrivatization themeColors={themeColors} />
  }
  
  if (activeTab === 'Veri Kaynakları') {
    return (
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 mx-2 sm:mx-4 lg:mx-12 xl:mx-20 mt-4 lg:mt-8">
        {/* İlk Kutu - Veri Kaynağı Önizleme */}
        <div className="bg-white border-2 rounded-2xl flex flex-col flex-1 transition-all duration-700 ease-out translate-y-0 scale-100 h-[500px] sm:h-[600px] md:h-[700px] lg:h-[850px]" style={{ borderColor: '#E5E7EB', animationDelay: '0ms' }}>
          <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
            <h3 className="text-xl sm:text-2xl lg:text-3xl">
              <span 
                className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Veri Kaynağı
              </span> 
              <span 
                className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Önizleme
              </span>
            </h3>
          </div>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-4 lg:space-y-6">
            <div className="h-full flex flex-col">
              <textarea
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 sm:p-4 flex-1 text-sm sm:text-base text-gray-700 leading-relaxed resize-none focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors w-full"
                placeholder="Veri kaynağı içeriğinizi buraya yazın..."
                value={currentText}
                onChange={handleTextChange}
                maxLength={1000}
              />
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mt-2 gap-2">
                <div>
                  {hasTextChanges && (
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={undoTextChanges}
                        className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors border border-gray-300"
                        title="Geri Al"
                      >
                        <Undo2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={saveTextChanges}
                        className="px-3 py-1.5 bg-[#6434F8] hover:bg-[#5429d4] text-white rounded-lg text-sm font-medium transition-colors"
                      >
                        Kaydet
                      </button>
                    </div>
                  )}
                </div>
                <span className="text-sm text-green-500 font-medium">{currentText.length}/1000 karakter</span>
              </div>
            </div>
          </div>
        </div>

        {/* İkinci Kutu - Veri Kaynağı Ayarları */}
        <div className="bg-white border-2 rounded-2xl flex flex-col flex-1 transition-all duration-700 ease-out translate-y-0 scale-100 min-h-[400px] lg:h-[850px]" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
          <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
            <h3 className="text-xl sm:text-2xl lg:text-3xl text-gray-900">
              <span className="font-bold">Veri</span> <span className="font-normal">Kaynağı</span>
            </h3>
          </div>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-4 lg:space-y-6 flex flex-col">
            {/* PDF Yükleme Alanı */}
            <div>
              <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">PDF Dosyası Yükle</h4>
              <div 
                className="border-2 border-dashed border-gray-300 rounded-lg p-4 sm:p-6 text-center transition-all duration-300 cursor-pointer"
                style={{
                  '--hover-border': themeColors.primary,
                  '--hover-bg': `${themeColors.primary}08`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = themeColors.primary;
                  e.currentTarget.style.backgroundColor = `${themeColors.primary}08`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#d1d5db';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <div className="flex flex-col items-center">
                  <svg className="w-8 sm:w-12 h-8 sm:h-12 text-gray-400 mb-2 sm:mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  <p className="text-sm sm:text-base text-gray-600 mb-2">PDF dosyasını buraya sürükleyin veya tıklayın</p>
                  <p className="text-xs sm:text-sm text-gray-400">Maksimum dosya boyutu: 10MB</p>
                  <button 
                    className="mt-3 px-4 py-2 text-white rounded-lg transition-colors"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.05)';
                      e.currentTarget.style.boxShadow = `0 4px 12px ${themeColors.primary}40`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    Dosya Seç
                  </button>
                </div>
              </div>
            </div>

            {/* Yüklenen PDF'ler Listesi */}
            <div>
              <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">Yüklenen Dosyalar</h4>
              <div className="space-y-2">
                {/* Örnek PDF dosyaları */}
                <div 
                  className={`flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg border border-gray-200 transition-colors gap-2 sm:gap-0 ${pdfStatuses['urun_katalog.pdf'] === 'pasif' ? 'bg-gray-100' : 'bg-gray-50'}`}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = themeColors.primary;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }}
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <svg className={`w-6 sm:w-8 h-6 sm:h-8 flex-shrink-0 ${pdfStatuses['urun_katalog.pdf'] === 'pasif' ? 'text-gray-400' : 'text-red-500'}`} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    <div className="min-w-0">
                      <p className={`text-xs sm:text-sm font-medium truncate ${pdfStatuses['urun_katalog.pdf'] === 'pasif' ? 'text-gray-500' : 'text-gray-900'}`}>urun_katalog.pdf</p>
                      <p className={`text-xs ${pdfStatuses['urun_katalog.pdf'] === 'pasif' ? 'text-gray-400' : 'text-gray-500'}`}>2.4 MB • Yüklendi: 2 dk önce</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <div className="relative">
                      <button
                        onClick={() => toggleDropdown('urun_katalog.pdf')}
                        className={`text-xs px-2 py-1 rounded-full cursor-pointer hover:scale-105 transition-all flex items-center space-x-1 whitespace-nowrap ${
                          pdfStatuses['urun_katalog.pdf'] === 'aktif' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        <span>{pdfStatuses['urun_katalog.pdf'] === 'aktif' ? 'Aktif' : 'Pasif'}</span>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                      </button>
                      
                      {openDropdowns['urun_katalog.pdf'] && (
                        <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[80px]">
                          <button
                            onClick={() => changePdfStatus('urun_katalog.pdf', 'aktif')}
                            className="w-full px-3 py-2 text-left text-xs hover:bg-gray-50 flex items-center space-x-2"
                          >
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span className="text-green-700 font-medium">Aktif</span>
                          </button>
                          <button
                            onClick={() => changePdfStatus('urun_katalog.pdf', 'pasif')}
                            className="w-full px-3 py-2 text-left text-xs hover:bg-gray-50 flex items-center space-x-2"
                          >
                            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                            <span className="text-red-700 font-medium">Pasif</span>
                          </button>
                        </div>
                      )}
                    </div>
                    <button className="text-red-500 hover:text-red-700 p-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    )
  }
  
  if (activeTab === 'Entegrasyonlar') {
    return (
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 mx-2 sm:mx-4 lg:mx-12 xl:mx-20 mt-4 lg:mt-8">
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
          <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
            <h3 className="text-xl sm:text-2xl lg:text-3xl">
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
                Entegrasyonu
              </span>
            </h3>
          </div>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col">
            <div 
              className="rounded-lg p-3 sm:p-4 font-mono text-xs sm:text-sm leading-relaxed relative overflow-hidden overflow-x-auto"
              style={{ backgroundColor: '#1E1E1E' }}
            >
              <div className="mb-2">
                <span style={{ color: '#569CD6' }}>&lt;script&gt;</span>
              </div>
              <div className="ml-2 mb-2">
                <span style={{ color: '#9CDCFE' }}>window</span><span style={{ color: '#D4D4D4' }}>.</span><span style={{ color: '#4FC1FF' }}>MarkaMindWidgetConfig</span> <span style={{ color: '#D4D4D4' }}>=</span> <span style={{ color: '#D4D4D4' }}>&#123;</span>
              </div>
              <div className="ml-4 mb-2">
                <span style={{ color: '#9CDCFE' }}>chatbotId</span><span style={{ color: '#D4D4D4' }}>:</span> <span style={{ color: '#CE9178' }}>&quot;19547356-af13-41a8-8&quot;</span>
              </div>
              <div className="ml-2 mb-2">
                <span style={{ color: '#D4D4D4' }}>&#125;;</span>
              </div>
              <div className="mb-2">
                <span style={{ color: '#569CD6' }}>&lt;/script&gt;</span>
              </div>
              <div className="mb-2">
                <span style={{ color: '#569CD6' }}>&lt;script</span> <span style={{ color: '#9CDCFE' }}>src</span><span style={{ color: '#D4D4D4' }}>=</span><span style={{ color: '#CE9178' }}>&quot;https://dashboard.markamind.ai/api/chatbot-widget&quot;</span><span style={{ color: '#569CD6' }}>&gt;&lt;/script&gt;</span>
              </div>
            </div>
            <div className="mt-4 flex flex-col sm:flex-row justify-end gap-2">
              <button
                onClick={() => {
                  const codeText = `<script>
  window.MarkaMindWidgetConfig = {
    chatbotId: "19547356-af13-41a8-8"
  };
</script>
<script src="https://dashboard.markamind.ai/api/chatbot-widget"></script>`;
                  navigator.clipboard.writeText(codeText);
                }}
                className="flex items-center justify-center space-x-2 px-3 sm:px-4 py-2 text-white rounded-lg font-medium transition-all duration-300 text-sm"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.boxShadow = `0 4px 12px ${themeColors.primary}40`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <Copy className="w-4 h-4" />
                <span>Panoya Kopyala</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  if (activeTab !== 'Önizleme') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center text-[#666]">
          <p>{activeTab} sekmesi henüz geliştirilmedi.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative">
      
      {/* Ana Container - Chatbox ve Özellikler responsive layout */}
      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 mx-2 sm:mx-4 lg:mx-6 xl:mx-12 mt-4 lg:mt-8">
        
        {/* Chatbox Elements */}
        <ChatboxElements
          chatboxTitle={selectedChatbox.name}
          initialMessage="Hello! It's Orbina here!"
          colors={{
            primary: colors.primary,
            aiMessage: colors.aiMessage,
            userMessage: colors.userMessage,
            borderColor: colors.borderColor,
            aiTextColor: colors.aiTextColor,
            userTextColor: colors.userTextColor,
            buttonPrimary: colors.buttonPrimary
          }}
          isVisible={isChatboxVisible}
          onToggle={handleToggleChatbox}
          className={getCardAnimation(0)}
          style={{ 
            animationDelay: getAnimationDelay(0)
          }}
        />

        {/* Chatbox Özellikleri Kartı */}
        <div 
          className={`bg-white border-2 rounded-2xl flex flex-col flex-1 order-3 ${getCardAnimation(1)}`}
          style={{ 
            minHeight: '400px',
            height: 'auto',
            borderColor: '#E5E7EB',
            animationDelay: getAnimationDelay(1)
          }}
        >
          {/* Özellikler Header */}
          <div className="flex items-center p-3 sm:p-4 lg:p-6 border-b border-gray-200">
            <h3 className="text-lg sm:text-xl lg:text-2xl text-gray-900">
              <span className="font-bold">Chatbox</span> <span className="font-normal">Özellikleri</span>
            </h3>
          </div>
          
          {/* Özellikler İçerik Alanı */}
          <div className="flex-1 p-3 sm:p-4 lg:p-6 space-y-3 sm:space-y-4 lg:space-y-5">
            
            {/* Chatbox Başlık */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox</h4>
              <div className="flex flex-col space-y-1.5 sm:space-y-2">
                <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox Başlık İsmi: <span className="font-semibold">{selectedChatbox.name}</span></p>
                <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox İlk Mesaj: <span className="font-semibold">Hello! It&apos;s Orbina here!</span></p>
              </div>
            </div>

            {/* Chatbox Tema */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox Tema</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">Ana Renk:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      🎨
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: tempColors.primary }}></div>
                    </div>
                  </div>
                </div>

                {/* AI Mesaj Rengi */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">AI Mesaj Rengi:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      🤖
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: tempColors.aiMessage }}></div>
                    </div>
                  </div>
                </div>

                {/* Kullanıcı Mesaj Rengi */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">Kullanıcı Mesaj Rengi:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      👤
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: tempColors.userMessage }}></div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Geri Alma ve Uygula Butonları */}
              {hasColorChanges && (
                <div className="flex items-center space-x-2 mt-3">
                  <button
                    onClick={undoColorChanges}
                    className="bg-gray-100 hover:bg-gray-200 p-1.5 sm:p-2 rounded-lg transition-all duration-300 hover:scale-105 border border-gray-300"
                  >
                    <Undo2 className="w-3 sm:w-4 h-3 sm:h-4 text-gray-600" />
                  </button>
                  <button
                    onClick={applyColors}
                    className="text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-medium hover:shadow-lg transition-all duration-300 hover:scale-105 text-xs sm:text-sm"
                    style={{ backgroundColor: '#6434F8' }}
                  >
                    Uygula
                  </button>
                </div>
              )}
            </div>

            {/* Chatbox Bilgi Kaynağı */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox Bilgi Kaynağı</h4>
              <div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-2.5 sm:p-3 relative overflow-hidden">
                  <p className="text-xs sm:text-sm text-gray-700 leading-relaxed">
                    Bu chatbox, yapay zeka destekli müşteri hizmetleri sağlar ve kullanıcı sorularını otomatik olarak yanıtlar. Modern teknoloji ile donatılmış bu
                  </p>
                  <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-gray-50 to-transparent pointer-events-none"></div>
                </div>
                <div className="text-right mt-1.5">
                  <span className="text-xs text-green-500 font-medium">899/1000 karakter</span>
                </div>
              </div>
            </div>

            {/* Chatbox Butonu */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox Butonu</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">Ana Renk:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      🎨
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: tempColors.primary }}></div>
                    </div>
                  </div>
                </div>

                {/* Çerçeve Rengi */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">Çerçeve Rengi:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      🔘
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: '#B794F6' }}></div>
                    </div>
                  </div>
                </div>

                {/* Kullanılan İcon */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700">Kullanılan İcon:</p>
                  <div className="flex items-center space-x-2 bg-white rounded-lg shadow-sm p-1.5 sm:p-2 border border-gray-100">
                    <div className="w-5 sm:w-6 h-5 sm:h-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md flex items-center justify-center text-xs border border-gray-200">
                      <MessageSquare className="w-2.5 sm:w-3 h-2.5 sm:h-3 text-gray-800" strokeWidth={1.2} />
                    </div>
                    <div className="relative flex-1 h-5 sm:h-6">
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner bg-gray-100"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Chatbox Entegrasyon */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox Entegrasyon</h4>
              <div 
                className="rounded-lg p-2.5 sm:p-3 font-mono text-xs leading-relaxed relative overflow-hidden overflow-x-auto"
                style={{ backgroundColor: '#1E1E1E', minHeight: '80px', height: 'auto' }}
              >
                <div className="mb-2">
                  <span style={{ color: '#569CD6' }}>&lt;script&gt;</span>
                </div>
                <div className="ml-2 mb-2">
                  <span style={{ color: '#9CDCFE' }}>window</span><span style={{ color: '#D4D4D4' }}>.</span><span style={{ color: '#4FC1FF' }}>OrbinaWidgetConfig</span> <span style={{ color: '#D4D4D4' }}>=</span> <span style={{ color: '#D4D4D4' }}>&#123;</span>
                </div>
                <div className="ml-4 mb-2">
                  <span style={{ color: '#9CDCFE' }}>chatbotId</span><span style={{ color: '#D4D4D4' }}>:</span> <span style={{ color: '#CE9178' }}>&quot;19547356-af13-41a8-832a&quot;</span>
                </div>
                <div className="ml-2">
                  <span style={{ color: '#D4D4D4' }}>&#125;;</span>
                </div>
                <div className="absolute bottom-0 left-0 w-full h-1/4 bg-gradient-to-t from-[#1E1E1E] to-transparent pointer-events-none"></div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  )
}