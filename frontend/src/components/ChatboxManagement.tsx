'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Undo2, Copy } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import ChatboxPrivatization from './ChatboxPrivatization'
import ChatboxElements from './ChatboxElements'
import { getUserStores, getStoreProducts, type Store, type ProductListItem } from '../lib/api'

export default function ChatboxManagement({ selectedChatbox, activeTab, themeColors, storeList, productList, isCreatingNew, onCancelCreate, chatboxData, setChatboxData }) {
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
    buttonPrimary: ''
  })
  const [tempColors, setTempColors] = useState({
    primary: '',
    aiMessage: '',
    userMessage: '',
    borderColor: '',
    aiTextColor: '',
    userTextColor: '',
    buttonPrimary: ''
  })
  const [hasColorChanges, setHasColorChanges] = useState(false)

  // Veri kaynağı metni state'leri
  const [originalText, setOriginalText] = useState("")
  const [currentText, setCurrentText] = useState("")
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

  // Mağaza seçimi state'leri
  const [selectedStores, setSelectedStores] = useState([])
  const [isStoreDropdownOpen, setIsStoreDropdownOpen] = useState(false)
  const storeDropdownRef = useRef(null)

  // Ürün seçimi state'leri
  const [selectedProducts, setSelectedProducts] = useState([])
  const [isProductDropdownOpen, setIsProductDropdownOpen] = useState(false)
  const productDropdownRef = useRef(null)

  // Backend'den çekilen veriler
  const [backendStores, setBackendStores] = useState<Store[]>([])
  const [backendProducts, setBackendProducts] = useState<ProductListItem[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingStores, setIsLoadingStores] = useState(false)
  const [isLoadingProducts, setIsLoadingProducts] = useState(false)

  // Mevcut chatbox verileri için local state
  const [localChatboxData, setLocalChatboxData] = useState({
    name: '',
    brand_id: '',
    chatbox_title: '',
    initial_message: '',
    placeholder_text: 'Mesajınızı yazın...',
    primary_color: '#FF6925',
    ai_message_color: '#E5E7EB',
    user_message_color: '#FF6925',
    ai_text_color: '#1F2937',
    user_text_color: '#FFFFFF',
    button_primary_color: '#FF6925',
    button_border_color: '#B794F6',
    button_icon_color: '#FFFFFF',
    avatar_url: null,
    animation_style: 'fade',
    language: 'tr',
    status: 'draft'
  })

  // Mağazaları backend'den yükle
  useEffect(() => {
    const loadStores = async () => {
      if (activeTab === 'Entegrasyonlar' && isCreatingNew) {
        setIsLoadingStores(true)
        try {
          const stores = await getUserStores()
          setBackendStores(stores)
        } catch (error) {
          console.error('Mağazalar yüklenirken hata:', error)
        } finally {
          setIsLoadingStores(false)
        }
      }
    }

    loadStores()
  }, [activeTab, isCreatingNew])

  // Mağaza seçildiğinde ürünleri yükle
  useEffect(() => {
    const loadProducts = async () => {
      if (selectedStores.length > 0 && !selectedStores.includes('all')) {
        setIsLoadingProducts(true)
        try {
          const allProducts: ProductListItem[] = []

          for (const storeId of selectedStores) {
            const response = await getStoreProducts(storeId, 1, 100)
            allProducts.push(...response.items)

            // İlk seçilen mağazanın brand_id'sini kaydet
            if (backendStores.length > 0 && !selectedBrandId) {
              const store = backendStores.find(s => s.id === storeId)
              if (store) {
                setSelectedBrandId(store.brand_id)
              }
            }
          }

          setBackendProducts(allProducts)
        } catch (error) {
          console.error('Ürünler yüklenirken hata:', error)
        } finally {
          setIsLoadingProducts(false)
        }
      } else {
        setBackendProducts([])
        setSelectedBrandId(null)
      }
    }

    loadProducts()
  }, [selectedStores, backendStores, selectedBrandId])

  // brand_id'yi parent state'e gönder
  useEffect(() => {
    if (selectedBrandId && setChatboxData) {
      setChatboxData(prev => ({
        ...prev,
        brand_id: selectedBrandId
      }))
    }
  }, [selectedBrandId, setChatboxData])

  // Seçilen mağaza ve ürünleri parent state'e gönder
  useEffect(() => {
    if (setChatboxData) {
      setChatboxData(prev => ({
        ...prev,
        selectedStores: selectedStores,
        selectedProducts: selectedProducts
      }))
    }
  }, [selectedStores, selectedProducts, setChatboxData])

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
            console.log('✅ Chatbox detayları yüklendi:', chatbox)

            // Renkleri güncelle
            setColors({
              primary: chatbox.primary_color || '#7B4DFA',
              aiMessage: chatbox.ai_message_color || '#E5E7EB',
              userMessage: chatbox.user_message_color || '#7B4DFA',
              borderColor: chatbox.button_border_color || '#B794F6',
              aiTextColor: chatbox.ai_text_color || '#1F2937',
              userTextColor: chatbox.user_text_color || '#FFFFFF',
              buttonPrimary: chatbox.button_primary_color || '#7B4DFA'
            })

            // Temp colors'ı da güncelle
            setTempColors({
              primary: chatbox.primary_color || '#7B4DFA',
              aiMessage: chatbox.ai_message_color || '#E5E7EB',
              userMessage: chatbox.user_message_color || '#7B4DFA',
              borderColor: chatbox.button_border_color || '#B794F6',
              aiTextColor: chatbox.ai_text_color || '#1F2937',
              userTextColor: chatbox.user_text_color || '#FFFFFF',
              buttonPrimary: chatbox.button_primary_color || '#7B4DFA'
            })

            // Metni güncelle
            setCurrentText(chatbox.initial_message || '')
            setOriginalText(chatbox.initial_message || '')

            // Local chatbox data'yı güncelle (mevcut chatbox için)
            setLocalChatboxData({
              name: chatbox.name,
              brand_id: chatbox.brand_id,
              chatbox_title: chatbox.chatbox_title,
              initial_message: chatbox.initial_message,
              placeholder_text: chatbox.placeholder_text,
              primary_color: chatbox.primary_color,
              ai_message_color: chatbox.ai_message_color,
              user_message_color: chatbox.user_message_color,
              ai_text_color: chatbox.ai_text_color,
              user_text_color: chatbox.user_text_color,
              button_primary_color: chatbox.button_primary_color,
              button_border_color: chatbox.button_border_color,
              button_icon_color: chatbox.button_icon_color,
              avatar_url: chatbox.avatar_url,
              animation_style: chatbox.animation_style,
              language: chatbox.language,
              status: chatbox.status
            })

            // Parent component'e bilgileri aktar (sadece yeni chatbox oluşturma modunda)
            if (setChatboxData && isCreatingNew) {
              setChatboxData({
                name: chatbox.name,
                brand_id: chatbox.brand_id,
                chatbox_title: chatbox.chatbox_title,
                initial_message: chatbox.initial_message,
                placeholder_text: chatbox.placeholder_text,
                primary_color: chatbox.primary_color,
                ai_message_color: chatbox.ai_message_color,
                user_message_color: chatbox.user_message_color,
                ai_text_color: chatbox.ai_text_color,
                user_text_color: chatbox.user_text_color,
                button_primary_color: chatbox.button_primary_color,
                button_border_color: chatbox.button_border_color,
                button_icon_color: chatbox.button_icon_color,
                avatar_url: chatbox.avatar_url,
                animation_style: chatbox.animation_style,
                language: chatbox.language,
                status: chatbox.status,
                selectedStores: [],
                selectedProducts: []
              })
            }
          } else {
            console.error('❌ Chatbox detayları yüklenemedi:', response.status)
          }
        } catch (error) {
          console.error('❌ Chatbox detayları yüklenirken hata:', error)
        } finally {
          setIsLoadingChatboxData(false)
        }
      } else if (isCreatingNew) {
        // Yeni chatbox oluşturma modunda loading'i false yap
        setIsLoadingChatboxData(false)
      }
    }

    loadChatboxDetails()
  }, [selectedChatbox?.id, isCreatingNew, setChatboxData])

  // Yeni chatbox oluşturma modunda default renkleri yükle
  useEffect(() => {
    if (isCreatingNew && chatboxData) {
      // Parent'tan gelen default renkleri colors state'ine yükle
      const defaultColors = {
        primary: chatboxData.primary_color || '#FF6925',
        aiMessage: chatboxData.ai_message_color || '#E5E7EB',
        userMessage: chatboxData.user_message_color || '#FF6925',
        borderColor: chatboxData.button_border_color || '#FFB380',
        aiTextColor: chatboxData.ai_text_color || '#1F2937',
        userTextColor: chatboxData.user_text_color || '#FFFFFF',
        buttonPrimary: chatboxData.button_primary_color || '#FF6925'
      }

      setColors(defaultColors)
      setTempColors(defaultColors)

      // Initial message'ı da güncelle
      if (chatboxData.initial_message) {
        setCurrentText(chatboxData.initial_message)
        setOriginalText(chatboxData.initial_message)
      }
    }
  }, [isCreatingNew, chatboxData])

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

  // Mağaza seçimi fonksiyonları
  const handleStoreSelection = (storeId) => {
    if (storeId === 'all') {
      // Tüm mağazalar seçildi
      if (selectedStores.includes('all')) {
        setSelectedStores([]) // Tüm seçimi kaldır
      } else {
        setSelectedStores(['all']) // Sadece tüm mağazalar seç
      }
    } else {
      // Tekil mağaza seçimi
      if (selectedStores.includes('all')) {
        // Eğer "tüm mağazalar" seçiliyse, onu kaldır ve bu mağazayı ekle
        setSelectedStores([storeId])
      } else {
        // Normal çoklu seçim
        setSelectedStores(prev =>
          prev.includes(storeId)
            ? prev.filter(id => id !== storeId)
            : [...prev, storeId]
        )
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

  // Seçilen mağazalara göre mevcut ürünleri getir (backend'den)
  const getAvailableProducts = () => {
    // Backend ürünlerini kullan
    return backendProducts
  }

  // Ürün seçimi fonksiyonları
  const handleProductSelection = (productId) => {
    if (productId === 'all') {
      const availableProducts = getAvailableProducts()
      if (selectedProducts.includes('all')) {
        setSelectedProducts([]) // Tüm seçimi kaldır
      } else {
        setSelectedProducts(['all']) // Sadece tüm ürünler seç
      }
    } else {
      // Tekil ürün seçimi
      if (selectedProducts.includes('all')) {
        // Eğer "tüm ürünler" seçiliyse, onu kaldır ve bu ürünü ekle
        setSelectedProducts([productId])
      } else {
        // Normal çoklu seçim
        setSelectedProducts(prev =>
          prev.includes(productId)
            ? prev.filter(id => id !== productId)
            : [...prev, productId]
        )
      }
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


  // Yeni Chatbox Oluşturma Modu
  if (isCreatingNew) {
    // Yeni chatbox oluşturma modunda, activeTab'a göre içerik göster
    if (activeTab === 'Özelleştirme') {
      return <ChatboxPrivatization selectedChatbox={selectedChatbox} themeColors={themeColors} isCreatingNew={true} onCancelCreate={onCancelCreate} chatboxData={chatboxData} setChatboxData={setChatboxData} />
    }
    // Veri Kaynakları ve Entegrasyonlar tab'ları için normal içeriği göster
    // (aşağıdaki kodlar çalışacak)
  }

  // Sekme kontrolü
  if (activeTab === 'Özelleştirme' && !isCreatingNew) {
    return <ChatboxPrivatization selectedChatbox={selectedChatbox} themeColors={themeColors} chatboxData={chatboxData} setChatboxData={setChatboxData} />
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

        {/* İkinci Kutu - Aynı Özellikler */}
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2" style={{ borderColor: '#E5E7EB', animationDelay: '300ms' }}>
          <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
            <h3 className="text-xl sm:text-2xl lg:text-3xl">
              <span
                className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                Mağaza&Ürün
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
                      {isLoadingStores ? (
                        <div className="flex items-center justify-center p-8">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                        </div>
                      ) : backendStores.length > 0 ? (
                        backendStores.map((store) => (
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
                              {store.logo_url && (
                                <img
                                  src={store.logo_url}
                                  alt={store.name}
                                  className="w-8 h-8 rounded-full mr-3 object-cover border border-gray-200"
                                />
                              )}
                              <div>
                                <p className="text-sm font-medium text-gray-900">{store.name}</p>
                                <p className="text-xs text-gray-500">{store.platform} • {store.status === 'active' ? 'Aktif' : 'Pasif'}</p>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="p-4 text-center text-sm text-gray-500">
                          Mağaza bulunamadı
                        </div>
                      )}
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
                          Tüm Mağazalar ({backendStores?.length || 0})
                        </span>
                      ) : (
                        selectedStores.map((storeId) => {
                          const store = backendStores?.find(s => s.id === storeId)
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
                    {isProductDropdownOpen && (
                      <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {isLoadingProducts ? (
                          <div className="flex items-center justify-center p-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                          </div>
                        ) : getAvailableProducts().length > 0 ? (
                          <>
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
                              // Backend'den gelen ürün için store bilgisini bul
                              const store = backendStores?.find(s => s.id === product.store_id)

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
                                    {/* Placeholder image - backend'de image field yok */}
                                    <div className="w-10 h-10 rounded-lg mr-3 bg-gray-100 border border-gray-200 flex items-center justify-center">
                                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                      </svg>
                                    </div>
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
                          </>
                        ) : (
                          <div className="p-4 text-center text-sm text-gray-500">
                            Ürün bulunamadı
                          </div>
                        )}
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

  // Kullanılacak chatbox verisini belirle
  const activeChatboxData = isCreatingNew ? chatboxData : localChatboxData

  return (
    <div className="relative">

      {/* Ana Container - Chatbox ve Özellikler responsive layout */}
      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 mx-2 sm:mx-4 lg:mx-6 xl:mx-12 mt-4 lg:mt-8">

        {/* Chatbox Elements */}
        <ChatboxElements
          chatboxTitle={activeChatboxData?.chatbox_title || selectedChatbox?.name || 'Chatbox'}
          initialMessage={activeChatboxData?.initial_message || currentText || 'Merhaba!'}
          colors={{
            primary: colors.primary || '#7B4DFA',
            aiMessage: colors.aiMessage || '#E5E7EB',
            userMessage: colors.userMessage || '#7B4DFA',
            borderColor: colors.borderColor || '#B794F6',
            aiTextColor: colors.aiTextColor || '#1F2937',
            userTextColor: colors.userTextColor || '#FFFFFF',
            buttonPrimary: colors.buttonPrimary || '#7B4DFA'
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
                <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox Başlık İsmi: <span className="font-semibold">{activeChatboxData?.chatbox_title || selectedChatbox?.name || 'Chatbox'}</span></p>
                <p className="text-xs sm:text-sm lg:text-base text-gray-700">Chatbox İlk Mesaj: <span className="font-semibold">{activeChatboxData?.initial_message || currentText || 'Merhaba!'}</span></p>
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
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: colors.primary }}></div>
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
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: colors.aiMessage }}></div>
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
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: colors.userMessage }}></div>
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
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: colors.buttonPrimary }}></div>
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
                      <div className="w-full h-full rounded-md border border-gray-400 shadow-inner" style={{ backgroundColor: colors.borderColor }}></div>
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