'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Undo2, Copy } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import ChatboxPrivatization from './ChatboxPrivatization'
import ChatboxElements from './ChatboxElements'

// Örnek chatbox verileri - mağazalar ile eşleştirilmiş
const chatboxList = [
  {
    id: 1,
    name: 'TechMall AI Assistant',
    status: 'active',
    messages: 1247,
    storeId: 1, // TechMall Store
    colors: {
      primary: '#DCFB6D',
      aiMessage: '#F8FFF4',
      userMessage: '#DCFB6D',
      borderColor: '#DCFB6D',
      aiTextColor: '#232228',
      userTextColor: '#232228',
      buttonPrimary: '#DCFB6D',
      buttonBorderColor: '#DCFB6D',
      buttonIcon: '#232228'
    },
    dataSources: ['Teknik ürün katalogları', 'Elektronik rehberleri', 'Garanti bilgileri'],
    integration: {
      homepage: true,
      selectedProducts: ['all'],
      platform: 'İKAS'
    }
  },
  {
    id: 2,
    name: 'Digital Market Bot',
    status: 'active',
    messages: 890,
    storeId: 2, // Digital Market
    colors: {
      primary: '#6F55FF',
      aiMessage: '#F4F3FF',
      userMessage: '#6F55FF',
      borderColor: '#6F55FF',
      aiTextColor: '#232228',
      userTextColor: '#FFFFFF',
      buttonPrimary: '#6F55FF',
      buttonBorderColor: '#6F55FF',
      buttonIcon: '#FFFFFF'
    },
    dataSources: ['Dijital ürün bilgileri', 'Yazılım lisans bilgileri', 'Teknik destek'],
    integration: {
      homepage: false,
      selectedProducts: ['all'], // Tüm ürünler seçili
      platform: 'İKAS'
    }
  },
  {
    id: 3,
    name: 'Premium Support Chat',
    status: 'inactive',
    messages: 456,
    storeId: 2, // Digital Market
    colors: {
      primary: '#232228',
      aiMessage: '#F9FAFB',
      userMessage: '#232228',
      borderColor: '#E5E7EB',
      aiTextColor: '#374151',
      userTextColor: '#FFFFFF',
      buttonPrimary: '#232228',
      buttonBorderColor: '#E5E7EB',
      buttonIcon: '#FFFFFF'
    },
    dataSources: ['Genel müşteri hizmetleri', 'SSS dokümanları', 'İade politikası'],
    integration: {
      homepage: true,
      selectedProducts: [], // Hiç ürün seçilmemiş
      platform: 'Kendi Web Sitem'
    }
  }
]

export default function ChatboxManagement({ activeTab, themeColors, storeList, productList, selectedChatbox: propSelectedChatbox, chatboxList: propChatboxList, setChatboxList }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  // Prop'tan gelen chatboxList'i kullan, yoksa local'ı kullan
  const activeChatboxList = propChatboxList || chatboxList

  // Default renk paleti - hata durumunda kullanılır
  const defaultColors = {
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA',
    buttonBorderColor: '#B794F6',
    buttonIcon: '#FFFFFF'
  }

  // PropSelectedChatbox varsa onu kullan, yoksa activeChatboxList'den ilkini kullan
  const [selectedChatbox, setSelectedChatbox] = useState(propSelectedChatbox || (activeChatboxList && activeChatboxList[0]))
  const [isChatboxVisible, setIsChatboxVisible] = useState(true)
  const [colors, setColors] = useState((propSelectedChatbox?.colors || activeChatboxList[0]?.colors || defaultColors))
  const [tempColors, setTempColors] = useState((propSelectedChatbox?.colors || activeChatboxList[0]?.colors || defaultColors))

  // PropSelectedChatbox değişirse local state'i güncelle
  useEffect(() => {
    if (propSelectedChatbox) {
      setSelectedChatbox(propSelectedChatbox)

      // Renkleri güncelle
      if (propSelectedChatbox.colors) {
        setColors(propSelectedChatbox.colors)
        setTempColors(propSelectedChatbox.colors)
        setHasColorChanges(false)
      }

      // Veri kaynağı metnini güncelle
      const newText = getDataSourceText(propSelectedChatbox)
      setOriginalText(newText)
      setCurrentText(newText)
      setHasTextChanges(false)

      // PDF durumlarını güncelle
      setPdfStatuses(getPdfStatuses(propSelectedChatbox))

      // Entegrasyon ayarlarını güncelle
      if (propSelectedChatbox.storeId) {
        setSelectedStores([propSelectedChatbox.storeId])
        setSelectedProducts(propSelectedChatbox.integration?.selectedProducts || [])
      } else {
        setSelectedStores([])
        setSelectedProducts([])
      }

      // Anasayfa ayarını güncelle
      if (propSelectedChatbox.storeId && propSelectedChatbox.integration?.homepage !== undefined) {
        setStoreHomepageSettings({
          [propSelectedChatbox.storeId]: propSelectedChatbox.integration.homepage
        })
      }
    }
  }, [propSelectedChatbox])
  const [hasColorChanges, setHasColorChanges] = useState(false)
  
  // Veri kaynağı metni state'leri - chatbox'a göre dinamik
  const getDataSourceText = (chatbox) => {
    if (!chatbox?.dataSources) {
      return 'Genel müşteri hizmetleri konularında uzmanlaşmış yapay zeka asistanıdır.'
    }
    return chatbox.dataSources.join(', ') + ' konularında uzmanlaşmış yapay zeka asistanıdır.'
  }
  const [originalText, setOriginalText] = useState(getDataSourceText(propSelectedChatbox || chatboxList[0]))
  const [currentText, setCurrentText] = useState(getDataSourceText(propSelectedChatbox || chatboxList[0]))
  const [hasTextChanges, setHasTextChanges] = useState(false)
  
  // PDF'lerin durumu ve dropdown state'leri - chatbox'a göre dinamik
  const getPdfStatuses = (chatbox) => {
    if (!chatbox?.id) {
      return {
        'urun_katalog.pdf': 'aktif',
        'sss_dokuman.pdf': 'aktif',
        'kullanim_kilavuzu.pdf': 'aktif'
      }
    }

    if (chatbox.id === 1) {
      return {
        'teknik_katalog.pdf': 'aktif',
        'elektronik_rehberi.pdf': 'aktif',
        'garanti_dokumani.pdf': 'aktif'
      }
    } else if (chatbox.id === 2) {
      return {
        'dijital_urunler.pdf': 'aktif',
        'yazilim_lisanslari.pdf': 'pasif',
        'teknik_destek.pdf': 'aktif'
      }
    } else {
      return {
        'musteri_hizmetleri.pdf': 'aktif',
        'sss_dokumanlari.pdf': 'aktif',
        'iade_politikasi.pdf': 'pasif'
      }
    }
  }
  const [pdfStatuses, setPdfStatuses] = useState(getPdfStatuses(propSelectedChatbox || chatboxList[0]))
  const [openDropdowns, setOpenDropdowns] = useState({})
  
  // Animasyon state'leri
  const [isVisible, setIsVisible] = useState(false)

  // Mağaza seçimi state'leri - chatbox'a göre initialize
  const getInitialStoreSelection = (chatbox) => {
    if (!chatbox?.storeId) return []
    return [chatbox.storeId]
  }
  const [selectedStores, setSelectedStores] = useState(getInitialStoreSelection(propSelectedChatbox || chatboxList[0]))
  const [isStoreDropdownOpen, setIsStoreDropdownOpen] = useState(false)
  const storeDropdownRef = useRef(null)

  const getInitialHomepageSettings = (chatbox) => {
    if (!chatbox?.storeId || !chatbox?.integration) return {}
    return { [chatbox.storeId]: chatbox.integration.homepage || false }
  }
  const [storeHomepageSettings, setStoreHomepageSettings] = useState(getInitialHomepageSettings(propSelectedChatbox || chatboxList[0]))

  // Ürün seçimi state'leri - chatbox'a göre initialize
  const getInitialProductSelection = (chatbox) => {
    if (!chatbox?.integration) return []
    return chatbox.integration.selectedProducts || []
  }
  const [selectedProducts, setSelectedProducts] = useState(getInitialProductSelection(propSelectedChatbox || chatboxList[0]))
  const [isProductDropdownOpen, setIsProductDropdownOpen] = useState(false)
  const productDropdownRef = useRef(null)

  // Chatbox entegrasyon ayarlarını güncelleme fonksiyonu
  const updateChatboxIntegration = (chatboxId, updates) => {
    if (setChatboxList && activeChatboxList) {
      const updatedList = activeChatboxList.map(chatbox => {
        if (chatbox.id === chatboxId) {
          return {
            ...chatbox,
            integration: {
              ...chatbox.integration,
              ...updates
            }
          }
        }
        return chatbox
      })
      setChatboxList(updatedList)

      // Çakışma kontrolü - aynı mağaza için birden fazla chatbox aynı ayarlara sahipse uyarı göster
      const currentChatbox = updatedList.find(cb => cb.id === chatboxId)
      if (currentChatbox) {
        const conflictingChatboxes = updatedList.filter(cb =>
          cb.id !== chatboxId &&
          cb.storeId === currentChatbox.storeId &&
          cb.status === 'active' &&
          cb.integration?.homepage === currentChatbox.integration?.homepage &&
          JSON.stringify(cb.integration?.selectedProducts) === JSON.stringify(currentChatbox.integration?.selectedProducts)
        )

        if (conflictingChatboxes.length > 0) {
          console.warn('Çakışma tespit edildi: Aynı mağaza için birden fazla chatbox aynı sayfalarda görüntülenecek. En yüksek mesaj sayısına sahip chatbox öncelikli olacak.')
        }
      }
    }
  }

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

  // Click-outside handler for dropdowns
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (storeDropdownRef.current && !storeDropdownRef.current.contains(event.target)) {
        setIsStoreDropdownOpen(false)
      }
      if (productDropdownRef.current && !productDropdownRef.current.contains(event.target)) {
        setIsProductDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
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
    if (!chatbox) return

    setSelectedChatbox(chatbox)
    setIsDropdownOpen(false)

    // Seçilen chatbox'ın renklerini uygula
    if (chatbox.colors) {
      setColors(chatbox.colors)
      setTempColors(chatbox.colors)
      setHasColorChanges(false)
    }

    // Entegrasyon ayarlarını güncelle
    if (chatbox.storeId) {
      setSelectedStores([chatbox.storeId])
      setSelectedProducts(chatbox.integration?.selectedProducts || [])
    } else {
      setSelectedStores([])
      setSelectedProducts([])
    }

    // Anasayfa ayarını güncelle
    if (chatbox.storeId && chatbox.integration?.homepage !== undefined) {
      setStoreHomepageSettings({
        [chatbox.storeId]: chatbox.integration.homepage
      })
    }

    // Veri kaynağı metnini güncelle
    const newText = getDataSourceText(chatbox)
    setOriginalText(newText)
    setCurrentText(newText)
    setHasTextChanges(false)

    // PDF durumlarını güncelle
    setPdfStatuses(getPdfStatuses(chatbox))
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

  // Mağaza anasayfa görünürlük ayarları fonksiyonu
  const handleStoreHomepageToggle = (storeId) => {
    const newHomepageValue = !storeHomepageSettings[storeId]
    setStoreHomepageSettings(prev => ({
      ...prev,
      [storeId]: newHomepageValue
    }))

    // Chatbox entegrasyonunu güncelle
    if (selectedChatbox && selectedChatbox.storeId === storeId) {
      updateChatboxIntegration(selectedChatbox.id, {
        homepage: newHomepageValue
      })
    }
  }

  // Mağaza seçimi fonksiyonları
  const handleStoreSelection = (storeId) => {
    if (storeId === 'all') {
      // Tüm mağazalar seçildi
      if (selectedStores.includes('all')) {
        setSelectedStores([]) // Tüm seçimi kaldır
        setStoreHomepageSettings({}) // Anasayfa ayarlarını temizle
      } else {
        setSelectedStores(['all']) // Sadece tüm mağazalar seç
        // Tüm mağazalar için anasayfa ayarını false yap
        const allStoreSettings = {}
        storeList?.forEach(store => {
          allStoreSettings[store.id] = false
        })
        setStoreHomepageSettings(allStoreSettings)
      }
    } else {
      // Tekil mağaza seçimi
      if (selectedStores.includes('all')) {
        // Eğer "tüm mağazalar" seçiliyse, onu kaldır ve bu mağazayı ekle
        setSelectedStores([storeId])
        setStoreHomepageSettings({ [storeId]: false })
      } else {
        // Normal çoklu seçim
        setSelectedStores(prev => {
          const newSelection = prev.includes(storeId)
            ? prev.filter(id => id !== storeId)
            : [...prev, storeId]

          // Mağaza seçimi kaldırıldıysa ayarını da kaldır
          if (prev.includes(storeId)) {
            setStoreHomepageSettings(prevSettings => {
              const newSettings = { ...prevSettings }
              delete newSettings[storeId]
              return newSettings
            })
          } else {
            // Yeni mağaza eklendiyse default false ayarı ekle
            setStoreHomepageSettings(prevSettings => ({
              ...prevSettings,
              [storeId]: false
            }))
          }

          return newSelection
        })
      }
    }
  }

  const getStoreSelectionText = () => {
    if (selectedStores.length === 0) {
      return 'Mağaza seçin'
    }
    if (selectedStores.includes('all')) {
      return 'Tüm Mağazalar'
    }
    if (selectedStores.length === 1) {
      const store = storeList.find(store => store.id === selectedStores[0])
      return store ? store.name : 'Mağaza seçin'
    }
    return `${selectedStores.length} mağaza seçildi`
  }

  // Seçilen mağazalar değiştiğinde ürün seçimini resetle
  useEffect(() => {
    setSelectedProducts([])
  }, [selectedStores])

  // Seçilen mağazalara göre mevcut ürünleri getir
  const getAvailableProducts = () => {
    if (selectedStores.includes('all')) {
      // Tüm mağazalar seçiliyse, tüm ürünleri döndür
      return Object.values(productList || {}).flat()
    }

    // Seçilen mağazaların ürünlerini döndür
    return selectedStores.reduce((allProducts, storeId) => {
      const storeProducts = productList?.[storeId] || []
      return [...allProducts, ...storeProducts]
    }, [])
  }

  // Ürün seçimi fonksiyonları
  const handleProductSelection = (productId) => {
    let newSelectedProducts = []

    if (productId === 'all') {
      const availableProducts = getAvailableProducts()
      if (selectedProducts.includes('all')) {
        newSelectedProducts = [] // Tüm seçimi kaldır
      } else {
        newSelectedProducts = ['all'] // Sadece tüm ürünler seç
      }
    } else {
      // Tekil ürün seçimi
      if (selectedProducts.includes('all')) {
        // Eğer "tüm ürünler" seçiliyse, onu kaldır ve bu ürünü ekle
        newSelectedProducts = [productId]
      } else {
        // Normal çoklu seçim
        newSelectedProducts = selectedProducts.includes(productId)
          ? selectedProducts.filter(id => id !== productId) // Zaten seçiliyse kaldır
          : [...selectedProducts, productId] // Seçilmemişse ekle
      }
    }

    setSelectedProducts(newSelectedProducts)

    // Chatbox entegrasyonunu güncelle
    if (selectedChatbox) {
      updateChatboxIntegration(selectedChatbox.id, {
        selectedProducts: newSelectedProducts
      })
    }
  }

  const getProductSelectionText = () => {
    if (selectedStores.length === 0) {
      return 'Önce mağaza seçin'
    }

    const availableProducts = getAvailableProducts()
    if (availableProducts.length === 0) {
      return 'Ürün bulunamadı'
    }

    if (selectedProducts.length === 0) {
      return 'Ürün seçin'
    }
    if (selectedProducts.includes('all')) {
      return `Tüm Ürünler (${availableProducts.length})`
    }
    if (selectedProducts.length === 1) {
      const product = availableProducts.find(product => product.id === selectedProducts[0])
      return product ? product.name : 'Ürün seçin'
    }
    return `${selectedProducts.length} ürün seçildi`
  }


  // Sekme kontrolü
  if (activeTab === 'Özelleştirme') {
    return <ChatboxPrivatization
      themeColors={colors}
      selectedChatbox={selectedChatbox}
      colors={colors}
      setColors={setColors}
      tempColors={tempColors}
      setTempColors={setTempColors}
      hasColorChanges={hasColorChanges}
      setHasColorChanges={setHasColorChanges}
      handleColorChange={(colorType, newColor) => {
        setTempColors(prev => ({
          ...prev,
          [colorType]: newColor
        }))
        setHasColorChanges(true)
      }}
    />
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
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
                }}
              >
                Veri Kaynağı
              </span>
              <span
                className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
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
                  '--hover-border': colors.primary,
                  '--hover-bg': `${colors.primary}08`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = colors.primary;
                  e.currentTarget.style.backgroundColor = `${colors.primary}08`;
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
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
                }}
              >
                Chatbox
              </span>
              <span
                className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
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

        {/* İkinci Kutu - Aynı Özellikler */}
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2" style={{ borderColor: '#E5E7EB', animationDelay: '300ms' }}>
          <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
            <h3 className="text-xl sm:text-2xl lg:text-3xl">
              <span
                className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
                }}
              >
                Mağaza&Ürün
              </span>
              <span
                className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${colors.primary}, ${colors.userMessage})`
                }}
              >
                Entegrasyonu
              </span>
            </h3>
          </div>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col">
            <div className="space-y-4 lg:space-y-6">

              {/* Mağaza Seçimi */}
              <div>
                <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">Mağaza Seçimi</h4>
                <div className="relative" ref={storeDropdownRef}>
                  <button
                    onClick={() => setIsStoreDropdownOpen(!isStoreDropdownOpen)}
                    className="w-full p-3 sm:p-4 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors bg-white hover:bg-gray-50 text-left flex items-center justify-between"
                  >
                    <span className="text-sm sm:text-base text-gray-700">
                      {getStoreSelectionText()}
                    </span>
                    <svg
                      className={`w-4 h-4 text-gray-500 transform transition-transform duration-200 ${
                        isStoreDropdownOpen ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </button>

                  {/* Dropdown Menü */}
                  {isStoreDropdownOpen && (
                    <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">

                      {/* Tüm Mağazalar Seçeneği */}
                      <div
                        onClick={() => handleStoreSelection('all')}
                        className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
                      >
                        <div className="flex items-center justify-center w-4 h-4 mr-3">
                          {selectedStores.includes('all') && (
                            <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">Tüm Mağazalar</p>
                          <p className="text-xs text-gray-500">Tüm mağazalarınızı entegre edin</p>
                        </div>
                      </div>

                      {/* Tekil Mağaza Seçenekleri */}
                      {storeList?.map((store) => (
                        <div
                          key={store.id}
                          onClick={() => handleStoreSelection(store.id)}
                          className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
                        >
                          <div className="flex items-center justify-center w-4 h-4 mr-3">
                            {selectedStores.includes(store.id) && (
                              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                          <div className="flex items-center flex-1">
                            <img
                              src={store.logo}
                              alt={store.name}
                              className="w-8 h-8 rounded-full mr-3 object-cover border border-gray-200"
                            />
                            <div>
                              <p className="text-sm font-medium text-gray-900">{store.name}</p>
                              <p className="text-xs text-gray-500">{store.platform} • {store.status === 'active' ? 'Aktif' : 'Pasif'}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Seçilen Mağazalar Özeti */}
                {selectedStores.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-2">Seçilen mağazalar:</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedStores.includes('all') ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Tüm Mağazalar ({storeList?.length || 0})
                        </span>
                      ) : (
                        selectedStores.map((storeId) => {
                          const store = storeList?.find(s => s.id === storeId)
                          return store ? (
                            <span key={storeId} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {store.name}
                            </span>
                          ) : null
                        })
                      )}
                    </div>
                  </div>
                )}

                {/* Mağaza Anasayfa Görünürlük Ayarları */}
                {selectedStores.length > 0 && !selectedStores.includes('all') && (
                  <div className="mt-4">
                    <h5 className="text-sm font-semibold text-gray-900 mb-3">Mağaza Anasayfa Görünürlük Ayarları</h5>
                    <p className="text-xs text-gray-500 mb-3">Chatbox'ın hangi mağazaların anasayfasında görüneceğini belirleyin</p>

                    <div className="space-y-3">
                      {selectedStores.map((storeId) => {
                        const store = storeList?.find(s => s.id === storeId)
                        if (!store) return null

                        return (
                          <div key={storeId} className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="flex items-center flex-1">
                              <img
                                src={store.logo}
                                alt={store.name}
                                className="w-8 h-8 rounded-full mr-3 object-cover border border-gray-200"
                              />
                              <div>
                                <p className="text-sm font-medium text-gray-900">{store.name}</p>
                                <p className="text-xs text-gray-500">{store.platform}</p>
                              </div>
                            </div>

                            <div className="flex items-center space-x-3">
                              <span className="text-xs text-gray-600">
                                {storeHomepageSettings[storeId] ? 'Anasayfada Görünür' : 'Sadece Ürün Sayfalarında'}
                              </span>

                              <button
                                onClick={() => handleStoreHomepageToggle(storeId)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                                  storeHomepageSettings[storeId]
                                    ? `focus:ring-[${themeColors.primary}]`
                                    : 'focus:ring-gray-500'
                                }`}
                                style={{
                                  backgroundColor: storeHomepageSettings[storeId]
                                    ? themeColors.primary
                                    : '#D1D5DB'
                                }}
                              >
                                <span
                                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                    storeHomepageSettings[storeId] ? 'translate-x-6' : 'translate-x-1'
                                  }`}
                                />
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* Açıklama Metni */}
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <svg className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <p className="text-xs text-blue-700 font-medium mb-1">Görünürlük Ayarları</p>
                          <p className="text-xs text-blue-600">
                            <strong>Açık:</strong> Chatbox hem mağaza anasayfasında hem de seçilen ürün sayfalarında görünür<br/>
                            <strong>Kapalı:</strong> Chatbox sadece seçilen ürün sayfalarında görünür
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tüm Mağazalar Seçiliyse Genel Anasayfa Ayarı */}
                {selectedStores.includes('all') && (
                  <div className="mt-4">
                    <h5 className="text-sm font-semibold text-gray-900 mb-3">Genel Anasayfa Görünürlük Ayarı</h5>

                    <div className="p-4 bg-white border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">Tüm Mağaza Anasayfalarında Görünür</p>
                          <p className="text-xs text-gray-500 mt-1">Chatbox tüm mağazaların anasayfasında ve ürün sayfalarında görünür</p>
                        </div>

                        <button
                          onClick={() => {
                            const newValue = !Object.values(storeHomepageSettings).every(val => val)
                            const allStoreSettings = {}
                            storeList?.forEach(store => {
                              allStoreSettings[store.id] = newValue
                            })
                            setStoreHomepageSettings(allStoreSettings)
                          }}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                            Object.values(storeHomepageSettings).every(val => val)
                              ? `focus:ring-[${themeColors.primary}]`
                              : 'focus:ring-gray-500'
                          }`}
                          style={{
                            backgroundColor: Object.values(storeHomepageSettings).every(val => val)
                              ? themeColors.primary
                              : '#D1D5DB'
                          }}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              Object.values(storeHomepageSettings).every(val => val) ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Ürün Seçimi - Sadece mağaza seçildiyse göster */}
              {selectedStores.length > 0 && (
                <div>
                  <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">Ürün Seçimi</h4>
                  <div className="relative" ref={productDropdownRef}>
                    <button
                      onClick={() => setIsProductDropdownOpen(!isProductDropdownOpen)}
                      className={`w-full p-3 sm:p-4 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors bg-white hover:bg-gray-50 text-left flex items-center justify-between ${
                        selectedStores.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                      disabled={selectedStores.length === 0}
                    >
                      <span className="text-sm sm:text-base text-gray-700">
                        {getProductSelectionText()}
                      </span>
                      <svg
                        className={`w-4 h-4 text-gray-500 transform transition-transform duration-200 ${
                          isProductDropdownOpen ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </button>

                    {/* Ürün Dropdown Menü */}
                    {isProductDropdownOpen && getAvailableProducts().length > 0 && (
                      <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">

                        {/* Tüm Ürünler Seçeneği */}
                        <div
                          onClick={() => handleProductSelection('all')}
                          className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
                        >
                          <div className="flex items-center justify-center w-4 h-4 mr-3">
                            {selectedProducts.includes('all') && (
                              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">Tüm Ürünler</p>
                            <p className="text-xs text-gray-500">Seçilen mağazaların tüm ürünlerini entegre edin ({getAvailableProducts().length} ürün)</p>
                          </div>
                        </div>

                        {/* Tekil Ürün Seçenekleri */}
                        {getAvailableProducts().map((product) => {
                          // Bu ürünün hangi mağazaya ait olduğunu bul
                          const storeId = Object.keys(productList || {}).find(id =>
                            productList[id]?.some(p => p.id === product.id)
                          )
                          const store = storeList?.find(s => s.id === parseInt(storeId))

                          return (
                            <div
                              key={product.id}
                              onClick={() => handleProductSelection(product.id)}
                              className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
                            >
                              <div className="flex items-center justify-center w-4 h-4 mr-3">
                                {selectedProducts.includes(product.id) && (
                                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                              </div>
                              <div className="flex items-center flex-1">
                                <img
                                  src={product.image}
                                  alt={product.name}
                                  className="w-10 h-10 rounded-lg mr-3 object-cover border border-gray-200"
                                />
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900">{product.name}</p>
                                  <div className="flex items-center justify-between">
                                    <p className="text-xs text-gray-500">{product.category} • {product.price}</p>
                                    {store && (
                                      <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                                        {store.name}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>

                  {/* Seçilen Ürünler Özeti */}
                  {selectedProducts.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-600 mb-2">Seçilen ürünler:</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedProducts.includes('all') ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Tüm Ürünler ({getAvailableProducts().length})
                          </span>
                        ) : (
                          selectedProducts.map((productId) => {
                            const product = getAvailableProducts().find(p => p.id === productId)
                            return product ? (
                              <span key={productId} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                {product.name}
                              </span>
                            ) : null
                          })
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

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
              <div className="grid grid-cols-3 gap-2 sm:gap-3 lg:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700 truncate">Ana Renk:</p>
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
                  <p className="text-xs sm:text-sm text-gray-700 truncate">AI Mesaj:</p>
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
                  <p className="text-xs sm:text-sm text-gray-700 truncate">Kullanıcı:</p>
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
                    {currentText.length > 150 ? `${currentText.substring(0, 150)}...` : currentText}
                  </p>
                  <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-gray-50 to-transparent pointer-events-none"></div>
                </div>
                <div className="text-right mt-1.5">
                  <span className="text-xs text-green-500 font-medium">{currentText.length}/1000 karakter</span>
                </div>
              </div>
            </div>

            {/* Chatbox Butonu */}
            <div>
              <h4 className="text-base sm:text-lg font-bold text-gray-900 mb-2 sm:mb-3">Chatbox Butonu</h4>
              <div className="grid grid-cols-3 gap-2 sm:gap-3 lg:gap-4">
                {/* Ana Renk */}
                <div className="flex flex-col space-y-1.5">
                  <p className="text-xs sm:text-sm text-gray-700 truncate">Ana Renk:</p>
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
                  <p className="text-xs sm:text-sm text-gray-700 truncate">Çerçeve:</p>
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
                  <p className="text-xs sm:text-sm text-gray-700 truncate">İcon:</p>
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