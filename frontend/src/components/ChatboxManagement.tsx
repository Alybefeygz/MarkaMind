'use client'

import { ChevronDown, Plus, MessageSquare, Settings, Trash2, Eye, ArrowLeft, Send, User, Home, Bot, Zap, Palette, Undo2, Copy, Upload, Save, Download, X } from 'lucide-react'
import { useState, useEffect, useRef, useMemo } from 'react'
import ChatboxPrivatization from './ChatboxPrivatization'
import ChatboxElements from './ChatboxElements'
import { getUserStores, getStoreProducts, getChatboxKnowledgeSources, uploadKnowledgeSource, toggleKnowledgeSourceStatus, deleteKnowledgeSource, createEditedPDF, getChatboxStores, getChatboxProducts, getProductImages, createChatbox, getUserChatboxes, updateChatboxIntegrations, deleteChatbox, getAllChatboxIntegrations, type Store, type ProductListItem, type KnowledgeSourceResponse, type ChatboxStoreRelation, type ChatboxProductRelation, type ChatboxCreate } from '../lib/api'

export default function ChatboxManagement({ selectedChatbox, activeTab, themeColors, storeList, productList, chatboxList, isCreatingNew, onCancelCreate, chatboxData, setChatboxData }) {
  // DEBUG: Component mount kontrolü
  console.log('🔄 ChatboxManagement MOUNT/RE-RENDER:', {
    chatboxId: selectedChatbox?.id,
    chatboxName: selectedChatbox?.name
  })

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
  const [isSavingPreview, setIsSavingPreview] = useState(false)

  // PDF/Knowledge Sources state'leri
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSourceResponse[]>([])
  const [isLoadingPDFs, setIsLoadingPDFs] = useState(false)
  const [isUploadingPDF, setIsUploadingPDF] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [openDropdowns, setOpenDropdowns] = useState({})
  const [createdChatboxId, setCreatedChatboxId] = useState<string | null>(null) // Yeni oluşturulan chatbox ID'si

  // PDF silme modal state'leri
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [pdfToDelete, setPdfToDelete] = useState<{ id: string; name: string } | null>(null)

  // PDF indirme modal state'leri
  const [downloadModalOpen, setDownloadModalOpen] = useState(false)
  const [pdfToDownload, setPdfToDownload] = useState<KnowledgeSourceResponse | null>(null)

  // PDF durum değiştirme modal state'leri
  const [statusChangeModalOpen, setStatusChangeModalOpen] = useState(false)
  const [pdfToChangeStatus, setPdfToChangeStatus] = useState<{ id: string; name: string; currentStatus: boolean } | null>(null)

  // PDF status dropdown state
  const [statusDropdownOpen, setStatusDropdownOpen] = useState<string | null>(null)
  
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
  const [isLoadingIntegrations, setIsLoadingIntegrations] = useState(false)

  // Ürün görselleri için cache
  const [productImages, setProductImages] = useState<Record<string, string>>({})

  // Integration change tracking
  const [originalStores, setOriginalStores] = useState<string[]>([])
  const [originalProducts, setOriginalProducts] = useState<string[]>([])
  const [hasIntegrationChanges, setHasIntegrationChanges] = useState(false)
  const [isSavingIntegrations, setIsSavingIntegrations] = useState(false)

  // Çakışma kontrolü için tüm chatbox entegrasyonları
  const [allIntegrations, setAllIntegrations] = useState<Record<string, {
    chatbox_name: string
    stores: string[]
    products: string[]
    stores_only: string[]
  }>>({})
  const [conflictingStores, setConflictingStores] = useState<Record<string, string>>({}) // store_id -> chatbox_name
  const [conflictingProducts, setConflictingProducts] = useState<Record<string, string>>({}) // product_id -> chatbox_name

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

  // PDF'leri backend'den yükle
  useEffect(() => {
    const loadKnowledgeSources = async () => {
      console.log('🔍 [DEBUG] loadKnowledgeSources çalıştı:', {
        activeTab,
        isCreatingNew,
        selectedChatboxId: selectedChatbox?.id,
        createdChatboxId
      })

      if (activeTab === 'Veri Kaynakları' && selectedChatbox?.id && !isCreatingNew) {
        setIsLoadingPDFs(true)
        try {
          const sources = await getChatboxKnowledgeSources(selectedChatbox.id)
          setKnowledgeSources(sources)
          console.log('✅ [ChatboxManagement] PDF\'ler yüklendi:', sources)

          // Aktif PDF'lerin içeriklerini textarea'ya formatla
          const activeContents = sources
            .filter(source => source.is_active && source.content)
            .map(source => {
              const uploadDate = new Date(source.created_at).toLocaleDateString('tr-TR')
              return `[${source.source_name}]-[${uploadDate}]:\n\n${source.content}\n----------------`
            })
            .join('\n\n')

          setCurrentText(activeContents)
          setOriginalText(activeContents)
        } catch (error) {
          console.error('❌ [ChatboxManagement] PDF\'ler yüklenirken hata:', error)
          setKnowledgeSources([])
        } finally {
          setIsLoadingPDFs(false)
        }
      } else if (isCreatingNew || !selectedChatbox?.id) {
        console.log('🧹 [DEBUG] PDF\'ler temizleniyor - Yeni chatbox modu')
        setKnowledgeSources([])
        setCurrentText('')
        setOriginalText('')
      } else {
        console.log('⏭️ [DEBUG] PDF yükleme atlandı - Koşullar sağlanmadı')
      }
    }

    loadKnowledgeSources()
  }, [activeTab, selectedChatbox?.id, createdChatboxId, isCreatingNew])

  // Tüm chatbox entegrasyonlarını yükle (çakışma kontrolü için)
  useEffect(() => {
    const loadAllIntegrations = async () => {
      if (activeTab === 'Entegrasyonlar') {
        // ADIM 1: Loading'i başlat (State temizlemeye gerek yok - component key ile yeniden mount oluyor)
        setIsLoadingIntegrations(true)

        try {
          // ADIM 2: Yeni entegrasyonları yükle
          const integrations = await getAllChatboxIntegrations()
          setAllIntegrations(integrations)

          // Çakışan mağaza ve ürünleri tespit et
          const conflictStores: Record<string, string> = {}
          const conflictProducts: Record<string, string> = {}

          Object.entries(integrations).forEach(([chatboxId, data]) => {
            // Debug log
            console.log('🔍 Çakışma kontrolü:', {
              chatboxId,
              selectedChatboxId: selectedChatbox?.id,
              isEqual: chatboxId === selectedChatbox?.id,
              chatboxName: data.chatbox_name
            })

            // Mevcut chatbox'u dahil etme
            if (chatboxId === selectedChatbox?.id) {
              console.log('✅ Mevcut chatbox, atlanıyor:', chatboxId)
              return
            }

            // Mağazaları kontrol et
            data.stores.forEach(storeId => {
              conflictStores[storeId] = data.chatbox_name
            })

            // Ürünleri kontrol et (stores_only olanlar hariç)
            data.products.forEach(productId => {
              conflictProducts[productId] = data.chatbox_name
            })

            // Stores_only olanları conflict stores'dan çıkar (ürünleri seçilebilir olsun)
            // Ama mağazanın kendisi hala seçilemez
          })

          setConflictingStores(conflictStores)
          setConflictingProducts(conflictProducts)
        } catch (error) {
          console.error('Entegrasyonlar yüklenirken hata:', error)
        } finally {
          // ADIM 3: Loading'i bitir
          setIsLoadingIntegrations(false)
        }
      }
    }

    loadAllIntegrations()
  }, [activeTab, selectedChatbox?.id])

  // Mağazaları backend'den yükle
  useEffect(() => {
    const loadStores = async () => {
      if (activeTab === 'Entegrasyonlar') {
        setIsLoadingStores(true)
        try {
          const stores = await getUserStores()
          setBackendStores(stores)

          // TÜM mağazaların TÜM ürünlerini yükle (mağaza seçiminden bağımsız)
          setIsLoadingProducts(true)
          try {
            const allProducts: ProductListItem[] = []

            // Tüm mağazaların ürünlerini yükle
            for (const store of stores) {
              const response = await getStoreProducts(store.id, 1, 100)
              allProducts.push(...response.items)
            }

            setBackendProducts(allProducts)

            // İlk mağazanın brand_id'sini kaydet (chatbox oluşturma için)
            if (stores.length > 0 && !selectedBrandId) {
              setSelectedBrandId(stores[0].brand_id)
            }
          } catch (error) {
            console.error('Ürünler yüklenirken hata:', error)
          } finally {
            setIsLoadingProducts(false)
          }

          // Mevcut chatbox için entegrasyon verilerini yükle
          if (selectedChatbox?.id && !isCreatingNew) {
            try {
              console.log('📦 Chatbox entegrasyonları yükleniyor...', selectedChatbox.id)

              // Chatbox'a bağlı mağazaları yükle
              const chatboxStores = await getChatboxStores(selectedChatbox.id)
              console.log('🏪 Yüklenen mağazalar:', chatboxStores)
              const integratedStoreIds = chatboxStores.map(rel => rel.store.id)
              console.log('🏪 Mağaza ID\'leri:', integratedStoreIds)
              setSelectedStores(integratedStoreIds)
              setOriginalStores(integratedStoreIds) // Orijinal değeri kaydet

              // Chatbox'a bağlı ürünleri yükle
              const chatboxProducts = await getChatboxProducts(selectedChatbox.id)
              console.log('📦 Yüklenen ürünler:', chatboxProducts)
              const integratedProductIds = chatboxProducts.map(rel => rel.product.id)
              console.log('📦 Ürün ID\'leri:', integratedProductIds)
              setSelectedProducts(integratedProductIds)
              setOriginalProducts(integratedProductIds) // Orijinal değeri kaydet
            } catch (error) {
              console.error('❌ Chatbox entegrasyonları yüklenirken hata:', error)
              // Hata durumunda orijinal değerleri de temizle
              setOriginalStores([])
              setOriginalProducts([])
            }
          } else if (isCreatingNew) {
            // Yeni chatbox oluşturuluyorsa seçimleri ve orijinal değerleri temizle
            setSelectedStores([])
            setSelectedProducts([])
            setOriginalStores([])
            setOriginalProducts([])
          } else {
            // Hiçbir koşul sağlanmadığında orijinal değerleri temizle
            setOriginalStores([])
            setOriginalProducts([])
          }
        } catch (error) {
          console.error('Mağazalar yüklenirken hata:', error)
        } finally {
          setIsLoadingStores(false)
        }
      }
    }

    loadStores()
  }, [activeTab, selectedChatbox?.id, isCreatingNew])

  // Ürün seçimlerini normalize et: "Tüm Ürünler" ile tek tek tüm ürünleri seçmek aynı kabul edilir
  const normalizeProductSelection = useMemo(() => {
    return (products: string[]) => {
      const allProductIds = backendProducts.map(product => product.id)
      
      // Eğer tüm ürünler seçiliyse (hem 'all' hem de tüm ID'ler, ya da sadece tüm ID'ler)
      const productIdsOnly = products.filter(id => id !== 'all')
      const allSelected = allProductIds.length > 0 && 
        allProductIds.every(id => productIdsOnly.includes(id)) && 
        productIdsOnly.length === allProductIds.length
      
      if (allSelected) {
        // Normalize edilmiş hali: 'all' ve tüm ID'ler
        return ['all', ...allProductIds].sort()
      }
      
      // Normalize edilmemiş hali: sadece ID'ler (veya boş)
      return products.sort()
    }
  }, [backendProducts])

  // Entegrasyon değişikliklerini izle
  useEffect(() => {
    if (isCreatingNew || !selectedChatbox?.id) {
      setHasIntegrationChanges(false)
      return
    }

    // Mağaza değişikliği kontrolü
    const storesChanged = JSON.stringify([...selectedStores].sort()) !== JSON.stringify([...originalStores].sort())

    // Ürün değişikliği kontrolü - normalize edilmiş haliyle karşılaştır
    const normalizedSelected = normalizeProductSelection(selectedProducts)
    const normalizedOriginal = normalizeProductSelection(originalProducts)
    const productsChanged = JSON.stringify(normalizedSelected) !== JSON.stringify(normalizedOriginal)

    setHasIntegrationChanges(storesChanged || productsChanged)
  }, [selectedStores, selectedProducts, originalStores, originalProducts, isCreatingNew, selectedChatbox?.id, normalizeProductSelection])

  // Ürün ID'lerini memoize et (dependency için)
  const productIds = useMemo(() => backendProducts.map(p => p.id).join(','), [backendProducts])

  // Ürün görsellerini yükle (primary image'ları)
  useEffect(() => {
    const loadProductImages = async () => {
      if (backendProducts.length > 0) {
        const imagePromises = backendProducts.map(async (product) => {
          // Eğer görsel zaten yüklenmişse atla
          if (productImages[product.id]) {
            return
          }

          try {
            const images = await getProductImages(product.id)
            // Primary image'ı bul veya ilk görseli al
            const primaryImage = images.find(img => img.is_primary) || images[0]
            if (primaryImage) {
              setProductImages(prev => ({
                ...prev,
                [product.id]: primaryImage.image_url
              }))
            }
          } catch (error) {
            // Görsel yüklenemezse sessizce devam et
            console.debug(`Ürün ${product.id} için görsel yüklenemedi:`, error)
          }
        })

        await Promise.all(imagePromises)
      }
    }

    loadProductImages()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productIds])

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

  // Düzenlenmiş içeriği parse et
  const parseEditedPreviewContent = (content: string) => {
    const sections = content.split('----------------').filter(s => s.trim())
    const edited: Array<{ sourceId: string; originalFilename: string; content: string }> = []

    sections.forEach(section => {
      // [Belge34.pdf]-[10.11.2025]: formatını parse et
      const match = section.match(/\[(.+?)\]-\[(.+?)\]:\s*\n\n([\s\S]+)/)
      if (match) {
        const [_, filename, date, pdfContent] = match

        // Orijinal PDF'i knowledgeSources'dan bul
        const originalSource = knowledgeSources.find(s =>
          s.source_name === filename && s.is_active
        )

        if (originalSource && originalSource.content !== pdfContent.trim()) {
          // İçerik değişmiş
          edited.push({
            sourceId: originalSource.id,
            originalFilename: filename,
            content: pdfContent.trim()
          })
        }
      }
    })

    return edited
  }

  // Değişiklikleri kaydet - düzenlenmiş PDF'leri oluştur
  const saveTextChanges = async () => {
    const chatboxId = getActiveChatboxId()
    if (!chatboxId) return

    setIsSavingPreview(true)
    try {
      // İçeriği parse et (her PDF'i ayır)
      const editedSources = parseEditedPreviewContent(currentText)

      if (editedSources.length === 0) {
        alert('Hiçbir değişiklik tespit edilmedi.')
        return
      }

      // Her düzenlenmiş PDF için backend'e istek at
      for (const edited of editedSources) {
        await createEditedPDF(chatboxId, {
          original_source_id: edited.sourceId,
          edited_content: edited.content
        })
      }

      // PDF listesini yenile
      const updatedSources = await getChatboxKnowledgeSources(chatboxId)
      setKnowledgeSources(updatedSources)

      // Aktif PDF'lerin içeriklerini textarea'ya formatla
      const activeContents = updatedSources
        .filter(source => source.is_active && source.content)
        .map(source => {
          const uploadDate = new Date(source.created_at).toLocaleDateString('tr-TR')
          return `[${source.source_name}]-[${uploadDate}]:\n\n${source.content}\n----------------`
        })
        .join('\n\n')

      setCurrentText(activeContents)
      setOriginalText(activeContents)
      setHasTextChanges(false)

      alert(`${editedSources.length} PDF başarıyla düzenlendi!`)
    } catch (error) {
      console.error('❌ PDF düzenlenirken hata:', error)
      alert('PDF düzenlenirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    } finally {
      setIsSavingPreview(false)
    }
  }

  const undoTextChanges = () => {
    setCurrentText(originalText)
    setHasTextChanges(false)
  }

  // Entegrasyon kaydetme fonksiyonu
  const handleSaveIntegrations = async () => {
    if (!selectedChatbox?.id) {
      alert('Entegrasyonları kaydetmek için önce bir chatbox seçin.')
      return
    }

    setIsSavingIntegrations(true)
    try {
      // Store integrations hazırla - Sadece mağaza ana sayfasında göster
      const storeIntegrations = selectedStores
        .filter(id => id !== 'all')
        .map(storeId => ({
          store_id: storeId,
          show_on_homepage: true,
          show_on_products: false, // Mağaza seçimi = sadece mağaza ana sayfasında
          position: 'bottom-right',
          is_active: true
        }))

      // Product integrations hazırla - SADECE ürün detay sayfasında göster
      const productIntegrations = selectedProducts
        .filter(id => id !== 'all')
        .map(productId => ({
          product_id: productId,
          show_on_product_page: true,
          show_on_store_homepage: false, // Ürün seçimi = SADECE ürün detay sayfasında
          is_active: true
        }))

      // Backend'e gönder
      const result = await updateChatboxIntegrations(selectedChatbox.id, {
        stores: storeIntegrations,
        products: productIntegrations,
        stores_only: [] // Artık kullanılmıyor
      })

      // Başarılı olursa orijinal değerleri güncelle (normalize edilmiş haliyle)
      setOriginalStores([...selectedStores])
      // Ürün seçimlerini normalize et: "Tüm Ürünler" ile tek tek tüm ürünleri seçmek aynı kabul edilir
      const normalizedProducts = normalizeProductSelection(selectedProducts)
      setOriginalProducts(normalizedProducts)
      setHasIntegrationChanges(false)

      alert(`Entegrasyonlar başarıyla kaydedildi!\n${result.stores_added} mağaza, ${result.products_added} ürün eklendi.`)
    } catch (error) {
      console.error('❌ Entegrasyonlar kaydedilirken hata:', error)
      alert('Entegrasyonlar kaydedilirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    } finally {
      setIsSavingIntegrations(false)
    }
  }

  // Entegrasyon değişikliklerini geri al
  const handleCancelIntegrations = () => {
    setSelectedStores([...originalStores])
    setSelectedProducts([...originalProducts])
    setHasIntegrationChanges(false)
  }

  // Helper fonksiyon: Aktif chatbox ID'sini al
  const getActiveChatboxId = () => {
    return selectedChatbox?.id || createdChatboxId
  }

  // PDF yönetim fonksiyonları
  const handleUploadPDF = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // PDF kontrolü
    if (file.type !== 'application/pdf') {
      alert('Lütfen sadece PDF dosyası yükleyin.')
      return
    }

    // Dosya boyutu kontrolü (10MB)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      alert('Dosya boyutu 10MB\'dan küçük olmalıdır.')
      return
    }

    setIsUploadingPDF(true)
    try {
      let chatboxId = getActiveChatboxId()

      // Eğer yeni chatbox oluşturuluyorsa ve henüz ID yoksa, önce chatbox'ı kaydet
      if (isCreatingNew && !chatboxId) {
        // Chatbox bilgilerini kontrol et
        if (!chatboxData.name || !chatboxData.chatbox_title || !chatboxData.initial_message) {
          alert('PDF yüklemeden önce lütfen Özelleştirme sekmesinde chatbox bilgilerini doldurun (İsim, Başlık, Başlangıç Mesajı)')
          setIsUploadingPDF(false)
          if (fileInputRef.current) {
            fileInputRef.current.value = ''
          }
          return
        }

        // Chatbox'ı kaydet
        const chatboxPayload: ChatboxCreate = {
          name: chatboxData.name,
          chatbox_title: chatboxData.chatbox_title,
          initial_message: chatboxData.initial_message,
          placeholder_text: chatboxData.placeholder_text,
          primary_color: chatboxData.primary_color,
          ai_message_color: chatboxData.ai_message_color,
          user_message_color: chatboxData.user_message_color,
          ai_text_color: chatboxData.ai_text_color,
          user_text_color: chatboxData.user_text_color,
          button_primary_color: chatboxData.button_primary_color,
          button_border_color: chatboxData.button_border_color,
          button_icon_color: chatboxData.button_icon_color,
          avatar_url: chatboxData.avatar_url,
          animation_style: chatboxData.animation_style,
          language: chatboxData.language,
          status: 'draft'
        }

        const createdChatbox = await createChatbox(chatboxPayload)
        chatboxId = createdChatbox.id
        setCreatedChatboxId(chatboxId) // ID'yi state'e kaydet

        console.log('✅ Chatbox oluşturuldu, ID:', chatboxId)

        // Kullanıcıya bildir - PDF yüklemeden önce
        alert('Chatbox başarıyla oluşturuldu! PDF yüklemesi devam ediyor...')
      }

      if (!chatboxId) {
        alert('Chatbox ID bulunamadı. Lütfen önce chatbox\'ı kaydedin.')
        setIsUploadingPDF(false)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        return
      }

      const newSource = await uploadKnowledgeSource(chatboxId, file)
      console.log('✅ PDF başarıyla yüklendi:', newSource)

      // Listeyi güncelle
      const updatedSources = [newSource, ...knowledgeSources]
      setKnowledgeSources(updatedSources)

      // Aktif PDF'lerin içeriklerini textarea'ya formatla
      const activeContents = updatedSources
        .filter(source => source.is_active && source.content)
        .map(source => {
          const uploadDate = new Date(source.created_at).toLocaleDateString('tr-TR')
          return `[${source.source_name}]-[${uploadDate}]:\n\n${source.content}\n----------------`
        })
        .join('\n\n')

      setCurrentText(activeContents)
      setOriginalText(activeContents)

      // Eğer chatbox yeni oluşturulduysa, kullanıcıyı bilgilendir ve sayfayı yenile
      if (isCreatingNew && createdChatboxId) {
        alert('Chatbox ve PDF başarıyla kaydedildi! Sayfa yenileniyor...')
        // Sayfayı yenile ki yeni chatbox dropdown'da görünsün
        window.location.reload()
      } else {
        alert('PDF başarıyla yüklendi!')
      }
    } catch (error) {
      console.error('❌ PDF yüklenirken hata:', error)
      alert('PDF yüklenirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    } finally {
      setIsUploadingPDF(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const openDeleteModal = (sourceId: string, sourceName: string) => {
    setPdfToDelete({ id: sourceId, name: sourceName })
    setDeleteModalOpen(true)
  }

  const closeDeleteModal = () => {
    setDeleteModalOpen(false)
    setPdfToDelete(null)
  }

  const openDownloadModal = (source: KnowledgeSourceResponse) => {
    setPdfToDownload(source)
    setDownloadModalOpen(true)
  }

  const closeDownloadModal = () => {
    setDownloadModalOpen(false)
    setPdfToDownload(null)
  }

  const openStatusChangeModal = (sourceId: string, sourceName: string, currentStatus: boolean) => {
    setPdfToChangeStatus({ id: sourceId, name: sourceName, currentStatus })
    setStatusChangeModalOpen(true)
    setStatusDropdownOpen(null) // Dropdown'u kapat
  }

  const closeStatusChangeModal = () => {
    setStatusChangeModalOpen(false)
    setPdfToChangeStatus(null)
  }

  const confirmDeletePDF = async () => {
    const chatboxId = getActiveChatboxId()
    if (!pdfToDelete || !chatboxId) return

    try {
      await deleteKnowledgeSource(chatboxId, pdfToDelete.id)
      console.log('✅ PDF başarıyla silindi')

      // Listeyi güncelle
      const updatedSources = knowledgeSources.filter(source => source.id !== pdfToDelete.id)
      setKnowledgeSources(updatedSources)

      // Aktif PDF'lerin içeriklerini textarea'ya formatla ve güncelle
      const activeContents = updatedSources
        .filter(source => source.is_active && source.content)
        .map(source => {
          const uploadDate = new Date(source.created_at).toLocaleDateString('tr-TR')
          return `[${source.source_name}]-[${uploadDate}]:\n\n${source.content}\n----------------`
        })
        .join('\n\n')

      setCurrentText(activeContents)
      setOriginalText(activeContents)

      // Modal'ı kapat
      closeDeleteModal()

      alert('PDF başarıyla silindi!')
    } catch (error) {
      console.error('❌ PDF silinirken hata:', error)
      alert('PDF silinirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    }
  }

  // Utility fonksiyonları
  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  const getTimeAgo = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) return `${diffInSeconds} sn önce`
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} dk önce`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} sa önce`
    return `${Math.floor(diffInSeconds / 86400)} gün önce`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
      case 'ready':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'processed':
      case 'ready':
        return 'İşlendi'
      case 'processing':
        return 'İşleniyor'
      case 'failed':
        return 'Hatalı'
      default:
        return 'Beklemede'
    }
  }

  const confirmStatusChange = async () => {
    const chatboxId = getActiveChatboxId()
    if (!pdfToChangeStatus || !chatboxId) return

    try {
      const updatedSource = await toggleKnowledgeSourceStatus(chatboxId, pdfToChangeStatus.id)
      console.log('✅ PDF durumu değiştirildi:', updatedSource)

      // Listeyi güncelle
      const updatedSources = knowledgeSources.map(source =>
        source.id === pdfToChangeStatus.id ? updatedSource : source
      )
      setKnowledgeSources(updatedSources)

      // Aktif PDF'lerin içeriklerini textarea'ya formatla
      const activeContents = updatedSources
        .filter(source => source.is_active && source.content)
        .map(source => {
          const uploadDate = new Date(source.created_at).toLocaleDateString('tr-TR')
          return `[${source.source_name}]-[${uploadDate}]:\n\n${source.content}\n----------------`
        })
        .join('\n\n')

      setCurrentText(activeContents)
      setOriginalText(activeContents)

      // Modal'ı kapat
      closeStatusChangeModal()
    } catch (error) {
      console.error('❌ PDF durumu değiştirilirken hata:', error)
      alert('PDF durumu değiştirilirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    }
  }

  const togglePDFStatus = (sourceId: string) => {
    const source = knowledgeSources.find(s => s.id === sourceId)
    if (source) {
      openStatusChangeModal(sourceId, source.source_name, source.is_active)
    }
  }

  const confirmDownloadPDF = async () => {
    const chatboxId = getActiveChatboxId()
    if (!pdfToDownload || !chatboxId || !pdfToDownload.storage_path) return

    try {
      // Get Supabase URL from environment or construct it
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://your-project.supabase.co'
      const token = localStorage.getItem('access_token')

      if (!token) {
        alert('Oturum süresi dolmuş. Lütfen tekrar giriş yapın.')
        return
      }

      // Construct download URL
      const downloadUrl = `${supabaseUrl}/storage/v1/object/chatbox-knowledge/${pdfToDownload.storage_path}`

      // Fetch the file with authorization
      const response = await fetch(downloadUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('PDF indirilemedi')
      }

      // Get blob and create download link
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = pdfToDownload.source_name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log('✅ PDF indirildi:', pdfToDownload.source_name)
      
      // Modal'ı kapat
      closeDownloadModal()
    } catch (error) {
      console.error('❌ PDF indirilirken hata:', error)
      alert('PDF indirilirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
    }
  }

  const handleDownloadPDF = (source: KnowledgeSourceResponse) => {
    openDownloadModal(source)
  }

  // Mağaza seçimi fonksiyonları
  const handleStoreSelection = (storeId) => {
    // Çakışma kontrolü (sadece seçilmeye çalışıldığında)
    if (storeId !== 'all' && !selectedStores.includes(storeId) && conflictingStores[storeId]) {
      alert(`Bu mağaza "${conflictingStores[storeId]}" isimli chatbox'ta zaten seçili.\n\nBir mağaza aynı anda sadece bir chatbox'ta seçilebilir.`)
      return
    }

    if (storeId === 'all') {
      // Tüm mağazalar seçildi
      if (selectedStores.includes('all')) {
        setSelectedStores([]) // Tüm seçimi kaldır
      } else {
        // Tüm mağazaları seç (hem 'all' hem de tüm mağaza ID'leri)
        const allStoreIds = backendStores.map(store => store.id)
        setSelectedStores(['all', ...allStoreIds])
      }
      // Dropdown'u kapat
      setIsStoreDropdownOpen(false)
    } else {
      // Tekil mağaza seçimi
      if (selectedStores.includes('all')) {
        // Eğer "tüm mağazalar" seçiliyse, onu kaldır ve bu mağazayı ekle
        setSelectedStores([storeId])
      } else {
        // Normal çoklu seçim
        setSelectedStores(prev => {
          const newSelection = prev.includes(storeId)
            ? prev.filter(id => id !== storeId)
            : [...prev, storeId]
          
          // Eğer tüm mağazalar seçiliyse 'all' ekle
          const allStoreIds = backendStores.map(store => store.id)
          const allSelected = allStoreIds.every(id => newSelection.includes(id))
          
          if (allSelected && newSelection.length === allStoreIds.length) {
            return ['all', ...newSelection]
          } else {
            // 'all' varsa kaldır
            return newSelection.filter(id => id !== 'all')
          }
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
      const store = backendStores.find(store => store.id === selectedStores[0])
      return store ? store.name : 'Mağaza seçin'
    }
    return `${selectedStores.length} mağaza seçildi`
  }

  // Seçilen mağazalara göre mevcut ürünleri getir (backend'den)
  const getAvailableProducts = () => {
    // Backend ürünlerini kullan
    return backendProducts
  }

  // Ürün seçimi fonksiyonları
  const handleProductSelection = (productId) => {
    // Çakışma kontrolü (sadece seçilmeye çalışıldığında)
    if (productId !== 'all' && !selectedProducts.includes(productId) && conflictingProducts[productId]) {
      alert(`Bu ürün "${conflictingProducts[productId]}" isimli chatbox'ta zaten seçili.\n\nBir ürün aynı anda sadece bir chatbox'ta seçilebilir.`)
      return
    }

    if (productId === 'all') {
      const availableProducts = getAvailableProducts()
      if (selectedProducts.includes('all')) {
        setSelectedProducts([]) // Tüm seçimi kaldır
      } else {
        // Tüm ürünleri seç (hem 'all' hem de tüm ürün ID'leri)
        const allProductIds = availableProducts.map(product => product.id)
        setSelectedProducts(['all', ...allProductIds])
      }
      // Dropdown'u kapat
      setIsProductDropdownOpen(false)
    } else {
      // Tekil ürün seçimi
      if (selectedProducts.includes('all')) {
        // Eğer "tüm ürünler" seçiliyse, onu kaldır ve bu ürünü ekle
        setSelectedProducts([productId])
      } else {
        // Normal çoklu seçim
        setSelectedProducts(prev => {
          const newSelection = prev.includes(productId)
            ? prev.filter(id => id !== productId)
            : [...prev, productId]
          
          // Eğer tüm ürünler seçiliyse 'all' ekle
          const availableProducts = getAvailableProducts()
          const allProductIds = availableProducts.map(product => product.id)
          const allSelected = allProductIds.every(id => newSelection.includes(id))
          
          if (allSelected && newSelection.length === allProductIds.length) {
            return ['all', ...newSelection]
          } else {
            // 'all' varsa kaldır
            return newSelection.filter(id => id !== 'all')
          }
        })
      }
    }
  }

  const getProductSelectionText = () => {
    const availableProducts = getAvailableProducts()
    if (availableProducts.length === 0) {
      return 'Ürün bulunamadı'
    }

    if (selectedProducts.length === 0) {
      return 'Ürün seçin'
    }
    
    // Eğer tüm ürünler seçiliyse (normalize edilmiş haliyle)
    const normalizedSelected = normalizeProductSelection(selectedProducts)
    const normalizedOriginal = normalizeProductSelection(originalProducts)
    const isAllSelected = normalizedSelected.includes('all')
    const isSaved = JSON.stringify(normalizedSelected.sort()) === JSON.stringify(normalizedOriginal.sort())
    
    // Eğer tüm ürünler seçiliyse ve kaydedilmişse, "Tüm Ürünler" göster (sayı olmadan)
    if (isAllSelected && isSaved) {
      return 'Tüm Ürünler'
    }
    
    // Eğer tüm ürünler seçiliyse ama henüz kaydedilmemişse, "Tüm Ürünler (X)" göster
    if (isAllSelected && !isSaved) {
      return `Tüm Ürünler (${availableProducts.length})`
    }
    
    // Eğer sadece 'all' string'i varsa (normalize edilmemiş durum)
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
    return <ChatboxPrivatization selectedChatbox={selectedChatbox} themeColors={themeColors} isCreatingNew={false} chatboxData={chatboxData} setChatboxData={setChatboxData} />
  }
  
  if (activeTab === 'Veri Kaynakları') {
    return (
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 mx-2 sm:mx-4 lg:mx-12 xl:mx-20 mt-4 lg:mt-8">
        {/* İlk Kutu - Veri Kaynağı Önizleme */}
        <div className="bg-white border-2 rounded-2xl flex flex-col flex-1 transition-all duration-700 ease-out translate-y-0 scale-100 h-[500px] sm:h-[600px] md:h-[700px] lg:h-[850px]" style={{ borderColor: '#E5E7EB', animationDelay: '0ms' }}>
          <div className="flex items-center justify-between p-4 sm:p-6 lg:p-8 border-b border-gray-200">
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

            {/* Kaydet/Vazgeç Butonları (sadece değişiklik varsa göster) */}
            {hasTextChanges && (
              <div className="flex items-center space-x-2 sm:space-x-3">
                {/* Vazgeç Butonu */}
                <button
                  onClick={undoTextChanges}
                  disabled={isSavingPreview}
                  className="flex items-center justify-center text-gray-600 hover:text-gray-800 p-1 sm:p-1.5 rounded-lg font-medium border border-gray-300 hover:border-gray-400 bg-white hover:bg-gray-50 transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Vazgeç"
                >
                  <ArrowLeft className="w-3.5 sm:w-4 h-3.5 sm:h-4" />
                </button>

                {/* Kaydet Butonu */}
                <button
                  onClick={saveTextChanges}
                  disabled={isSavingPreview}
                  className="flex items-center space-x-1 text-white px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg font-medium shadow-sm hover:shadow-md transition-all duration-300 hover:scale-105 text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                  }}
                >
                  <Save className="w-3 sm:w-3.5 h-3 sm:h-3.5" />
                  <span>{isSavingPreview ? 'Kaydediliyor...' : 'Kaydet'}</span>
                </button>
              </div>
            )}
          </div>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-4 lg:space-y-6">
            <div className="h-full flex flex-col overflow-hidden">
              <textarea
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 sm:p-4 flex-1 text-sm sm:text-base text-gray-700 leading-relaxed resize-none focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors w-full overflow-y-auto"
                placeholder="Aktif PDF'lerin içerikleri buraya otomatik yüklenecek..."
                value={currentText}
                onChange={handleTextChange}
              />
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mt-2 gap-2">
                <div className="text-xs text-gray-500">
                  {hasTextChanges ? (
                    <span className="text-orange-600 font-medium">⚠️ Değişiklikler kaydedilmedi</span>
                  ) : (
                    'PDF içeriklerini düzenleyebilirsiniz'
                  )}
                </div>
                <span className="text-sm text-gray-500 font-medium">{currentText.length} karakter</span>
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
                onClick={() => fileInputRef.current?.click()}
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
                    className="mt-3 px-4 py-2 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                    }}
                    disabled={isUploadingPDF}
                    onMouseEnter={(e) => {
                      if (!isUploadingPDF) {
                        e.currentTarget.style.transform = 'scale(1.05)';
                        e.currentTarget.style.boxShadow = `0 4px 12px ${themeColors.primary}40`;
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    {isUploadingPDF ? 'Yükleniyor...' : 'Dosya Seç'}
                  </button>
                </div>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleUploadPDF}
                className="hidden"
              />
            </div>

            {/* Yüklenen PDF'ler Listesi */}
            <div>
              <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">Yüklenen Dosyalar</h4>
              <div className="space-y-2">
                {isLoadingPDFs ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2" style={{ borderColor: themeColors.primary }}></div>
                    <p className="text-xs text-gray-500">PDF'ler yükleniyor...</p>
                  </div>
                ) : knowledgeSources.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
                    <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm text-gray-600">Henüz PDF yüklenmemiş</p>
                    <p className="text-xs text-gray-500 mt-1">Chatbox'ınıza bilgi kaynağı eklemek için PDF yükleyin</p>
                  </div>
                ) : (
                  knowledgeSources.map((source) => (
                    <div
                      key={source.id}
                      className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg border border-gray-200 transition-colors gap-2 sm:gap-0 bg-gray-50 hover:bg-gray-100"
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = themeColors.primary;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                    >
                      <div className="flex items-center space-x-3 flex-1">
                        <svg className="w-6 sm:w-8 h-6 sm:h-8 flex-shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                        <div className="min-w-0">
                          <p className="text-xs sm:text-sm font-medium truncate text-gray-900">{source.source_name}</p>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(source.file_size)} • Yüklendi: {getTimeAgo(source.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 flex-shrink-0">
                        {/* Aktif/Pasif Dropdown */}
                        <div className="relative">
                          <button
                            onClick={() => setStatusDropdownOpen(statusDropdownOpen === source.id ? null : source.id)}
                            className="text-xs px-2 py-1 rounded-full cursor-pointer hover:scale-105 transition-all flex items-center space-x-1 whitespace-nowrap"
                            style={{
                              backgroundColor: source.is_active ? `${themeColors.primary}15` : '#F3F4F6',
                              color: source.is_active ? themeColors.primary : '#6B7280'
                            }}
                          >
                            <span>{source.is_active ? 'Aktif' : 'Pasif'}</span>
                            <ChevronDown className="w-3 h-3" />
                          </button>

                          {statusDropdownOpen === source.id && (
                            <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[80px]">
                              <button
                                onClick={() => togglePDFStatus(source.id)}
                                className="w-full px-3 py-2 text-left text-xs hover:bg-gray-50 flex items-center space-x-2"
                              >
                                <div
                                  className="w-2 h-2 rounded-full"
                                  style={{ backgroundColor: source.is_active ? '#6B7280' : themeColors.primary }}
                                ></div>
                                <span
                                  className="font-medium"
                                  style={{ color: source.is_active ? '#6B7280' : themeColors.primary }}
                                >
                                  {source.is_active ? 'Pasif' : 'Aktif'}
                                </span>
                              </button>
                            </div>
                          )}
                        </div>

                        {/* İndirme Butonu */}
                        <button
                          onClick={() => handleDownloadPDF(source)}
                          className="p-1 transition-all hover:scale-110"
                          style={{ color: '#6B7280' }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.color = themeColors.primary
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.color = '#6B7280'
                          }}
                          title="PDF'i İndir"
                        >
                          <Download className="w-4 h-4" />
                        </button>

                        {/* Silme Butonu */}
                        <button
                          onClick={() => openDeleteModal(source.id, source.source_name)}
                          className="p-1 transition-all hover:scale-110"
                          style={{ color: themeColors.primary }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.color = '#DC2626'
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.color = themeColors.primary
                          }}
                          title="PDF'i Sil"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>

        {/* PDF Silme Onay Modal'ı */}
        {deleteModalOpen && (
          <div className="fixed inset-0 flex items-end justify-end p-4 sm:p-6 z-50 pointer-events-none">
            <div
              className="bg-white rounded-2xl shadow-2xl border-2 pointer-events-auto w-full max-w-sm transition-all duration-300 ease-out transform"
              style={{
                borderColor: themeColors.primary,
                animation: 'slideUp 0.3s ease-out'
              }}
            >
              {/* Modal İçeriği */}
              <div className="p-6">
                {/* İkon */}
                <div className="flex justify-center mb-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center"
                    style={{
                      backgroundColor: `${themeColors.primary}15`
                    }}
                  >
                    <Trash2
                      className="w-8 h-8"
                      style={{ color: themeColors.primary }}
                    />
                  </div>
                </div>

                {/* Başlık */}
                <h3 className="text-xl font-bold text-center text-gray-900 mb-2">
                  Veri Kaynağı Silinsin mi?
                </h3>

                {/* Açıklama */}
                <p className="text-sm text-center text-gray-600 mb-6">
                  <span className="font-semibold">{pdfToDelete?.name}</span> dosyasını silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
                </p>

                {/* Butonlar */}
                <div className="flex space-x-3">
                  <button
                    onClick={closeDeleteModal}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                  >
                    Vazgeç
                  </button>
                  <button
                    onClick={confirmDeletePDF}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-white transition-all hover:shadow-lg"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                    }}
                  >
                    Evet, Sil
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PDF İndirme Onay Modal'ı */}
        {downloadModalOpen && (
          <div className="fixed inset-0 flex items-end justify-end p-4 sm:p-6 z-50 pointer-events-none">
            <div
              className="bg-white rounded-2xl shadow-2xl border-2 pointer-events-auto w-full max-w-sm transition-all duration-300 ease-out transform"
              style={{
                borderColor: themeColors.primary,
                animation: 'slideUp 0.3s ease-out'
              }}
            >
              {/* Modal İçeriği */}
              <div className="p-6">
                {/* İkon */}
                <div className="flex justify-center mb-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center"
                    style={{
                      backgroundColor: `${themeColors.primary}15`
                    }}
                  >
                    <Download
                      className="w-8 h-8"
                      style={{ color: themeColors.primary }}
                    />
                  </div>
                </div>

                {/* Başlık */}
                <h3 className="text-xl font-bold text-center text-gray-900 mb-2">
                  PDF İndirilsin mi?
                </h3>

                {/* Açıklama */}
                <p className="text-sm text-center text-gray-600 mb-6">
                  <span className="font-semibold">{pdfToDownload?.source_name}</span> dosyasını indirmek istediğinize emin misiniz?
                </p>

                {/* Butonlar */}
                <div className="flex space-x-3">
                  <button
                    onClick={closeDownloadModal}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                  >
                    Vazgeç
                  </button>
                  <button
                    onClick={confirmDownloadPDF}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-white transition-all hover:shadow-lg"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                    }}
                  >
                    Evet, İndir
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PDF Durum Değiştirme Onay Modal'ı */}
        {statusChangeModalOpen && (
          <div className="fixed inset-0 flex items-end justify-end p-4 sm:p-6 z-50 pointer-events-none">
            <div
              className="bg-white rounded-2xl shadow-2xl border-2 pointer-events-auto w-full max-w-sm transition-all duration-300 ease-out transform"
              style={{
                borderColor: themeColors.primary,
                animation: 'slideUp 0.3s ease-out'
              }}
            >
              {/* Modal İçeriği */}
              <div className="p-6">
                {/* İkon */}
                <div className="flex justify-center mb-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center"
                    style={{
                      backgroundColor: `${themeColors.primary}15`
                    }}
                  >
                    <Settings
                      className="w-8 h-8"
                      style={{ color: themeColors.primary }}
                    />
                  </div>
                </div>

                {/* Başlık */}
                <h3 className="text-xl font-bold text-center text-gray-900 mb-2">
                  Durum Değiştirilsin mi?
                </h3>

                {/* Açıklama */}
                <p className="text-sm text-center text-gray-600 mb-6">
                  <span className="font-semibold">{pdfToChangeStatus?.name}</span> dosyasının durumunu <span className="font-semibold">{pdfToChangeStatus?.currentStatus ? 'Pasif' : 'Aktif'}</span> olarak değiştirmek istediğinize emin misiniz?
                </p>

                {/* Butonlar */}
                <div className="flex space-x-3">
                  <button
                    onClick={closeStatusChangeModal}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                  >
                    Vazgeç
                  </button>
                  <button
                    onClick={confirmStatusChange}
                    className="flex-1 px-4 py-2.5 rounded-lg font-medium text-white transition-all hover:shadow-lg"
                    style={{
                      background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                    }}
                  >
                    Evet, Değiştir
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  if (activeTab === 'Entegrasyonlar') {
    return (
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 mx-2 sm:mx-4 lg:mx-12 xl:mx-20 mt-4 lg:mt-8 items-start">
        <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 self-start" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
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
          <div className="p-4 sm:p-6 lg:p-8 flex flex-col">
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
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-base sm:text-lg font-semibold text-gray-900">Mağaza Seçimi</h4>

                  {/* Kaydet ve Vazgeç Butonları */}
                  {hasIntegrationChanges && (
                    <div className="flex gap-2">
                      <button
                        onClick={handleCancelIntegrations}
                        disabled={isSavingIntegrations}
                        className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                      >
                        <ArrowLeft className="w-3.5 sm:w-4 h-3.5 sm:h-4" />
                      </button>
                      <button
                        onClick={handleSaveIntegrations}
                        disabled={isSavingIntegrations}
                        className="px-3 py-1.5 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{
                          backgroundColor: themeColors.primary,
                          opacity: isSavingIntegrations ? 0.5 : 1
                        }}
                      >
                        {isSavingIntegrations ? 'Kaydediliyor...' : 'Kaydet'}
                      </button>
                    </div>
                  )}
                </div>
                <div className="relative" ref={storeDropdownRef}>
                  <button
                    onClick={() => setIsStoreDropdownOpen(!isStoreDropdownOpen)}
                    className="w-full p-3 sm:p-4 border border-gray-200 rounded-lg focus:outline-none focus:border-[#FF6925] focus:ring-1 focus:ring-[#FF6925] transition-colors bg-white hover:bg-gray-50 text-left flex items-center justify-between"
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
                            <svg className="w-4 h-4 text-[#FF6925]" fill="currentColor" viewBox="0 0 20 20">
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
                                <svg className="w-4 h-4 text-[#FF6925]" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            <div className="flex items-center flex-1">
                              {store.logo ? (
                                <img
                                  src={store.logo}
                                  alt={store.name}
                                  className="w-8 h-8 rounded-full mr-3 object-cover border border-gray-200 flex-shrink-0"
                                  onError={(e) => {
                                    // Logo yüklenemezse placeholder göster
                                    e.currentTarget.style.display = 'none'
                                    const placeholder = e.currentTarget.nextElementSibling as HTMLElement
                                    if (placeholder) placeholder.style.display = 'flex'
                                  }}
                                />
                              ) : null}
                              <div 
                                className={`w-8 h-8 rounded-full mr-3 bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0 ${store.logo ? 'hidden' : ''}`}
                              >
                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                              </div>
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{store.name}</p>
                                <p className="text-xs text-gray-500">
                                  {store.description
                                    ? store.description.length > 30
                                      ? store.description.substring(0, 30) + '...'
                                      : store.description
                                    : 'Açıklama yok'}
                                </p>
                              </div>
                              {/* Hangi chatbox'ta entegre olduğunu göster */}
                              {(() => {
                                const integratedChatbox = Object.entries(allIntegrations).find(([chatboxId, data]) =>
                                  data.stores.includes(store.id) || data.stores_only?.includes(store.id)
                                )

                                if (!integratedChatbox || integratedChatbox[0] === selectedChatbox?.id) {
                                  return null
                                }

                                // chatboxList'ten o chatbox'ın renklerini bul
                                const chatbox = chatboxList?.find(cb => cb.id === integratedChatbox[0])
                                const bgColor = chatbox?.button_primary_color || chatbox?.primary_color || '#3B82F6'
                                const borderColor = chatbox?.button_border_color || chatbox?.primary_color || '#3B82F6'
                                const textColor = chatbox?.button_icon_color || '#FFFFFF'

                                return (
                                  <div
                                    className="flex items-center px-3 py-1.5 rounded-lg shadow-md border backdrop-blur-sm flex-shrink-0"
                                    style={{
                                      background: `linear-gradient(135deg, ${bgColor} 0%, ${borderColor} 100%)`,
                                      borderColor: borderColor
                                    }}
                                  >
                                    <span className="text-xs font-semibold truncate max-w-[100px]" style={{ color: textColor }}>
                                      {integratedChatbox[1].chatbox_name}
                                    </span>
                                  </div>
                                )
                              })()}
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
                {isLoadingIntegrations ? (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-2">Entegrasyonlar yükleniyor...</p>
                    <div className="space-y-2">
                      {[1, 2].map((i) => (
                        <div key={i} className="flex items-center p-2 bg-white rounded-lg border border-gray-200 animate-pulse">
                          <div className="w-8 h-8 rounded-full mr-3 bg-gray-200"></div>
                          <div className="flex-1">
                            <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : selectedStores.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-2">Seçilen mağazalar:</p>
                    <div className="space-y-2 max-h-[150px] overflow-y-auto pr-1">
                      {selectedStores
                        .filter(id => id !== 'all') // 'all' ID'sini filtrele
                        .map((storeId) => {
                          const store = backendStores?.find(s => s.id === storeId)
                          return store ? (
                            <div key={storeId} className="flex items-center p-2 bg-white rounded-lg border border-gray-200">
                              {/* Kaldır Butonu */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  // 'all' seçiliyse önce onu kaldır, sonra mağazayı kaldır
                                  const newSelected = selectedStores.filter(id => id !== 'all' && id !== storeId)
                                  setSelectedStores(newSelected)
                                }}
                                className="mr-2 p-1 hover:bg-gray-100 rounded-full transition-colors group"
                                title="Seçimi kaldır"
                              >
                                <X className="w-4 h-4 text-gray-400 group-hover:text-[#FF6925]" />
                              </button>
                              {/* Logo */}
                              {store.logo ? (
                                <img
                                  src={store.logo}
                                  alt={store.name}
                                  className="w-8 h-8 rounded-full mr-3 object-cover border border-gray-200 flex-shrink-0"
                                  onError={(e) => {
                                    e.currentTarget.style.display = 'none'
                                    const placeholder = e.currentTarget.nextElementSibling as HTMLElement
                                    if (placeholder) placeholder.style.display = 'flex'
                                  }}
                                />
                              ) : null}
                              <div
                                className={`w-8 h-8 rounded-full mr-3 bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0 ${store.logo ? 'hidden' : ''}`}
                              >
                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                              </div>
                              {/* İsim ve Bilgiler */}
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">{store.name}</p>
                                <p className="text-xs text-gray-500">
                                  {store.description
                                    ? store.description.length > 30
                                      ? store.description.substring(0, 30) + '...'
                                      : store.description
                                    : 'Açıklama yok'}
                                </p>
                              </div>
                              {/* Chatbox Badge */}
                              {(() => {
                                if (!selectedChatbox) {
                                  console.log('❌ selectedChatbox yok!')
                                  return null
                                }

                                // Fallback: Eğer button renkleri yoksa primary_color kullan
                                const bgColor = selectedChatbox.button_primary_color || selectedChatbox.primary_color || '#3B82F6'
                                const borderColor = selectedChatbox.button_border_color || selectedChatbox.primary_color || '#3B82F6'
                                const iconColor = selectedChatbox.button_icon_color || '#FFFFFF'

                                console.log('🎨 Chatbox Badge Debug:', {
                                  chatboxName: selectedChatbox.name,
                                  button_primary_color: selectedChatbox.button_primary_color,
                                  button_border_color: selectedChatbox.button_border_color,
                                  button_icon_color: selectedChatbox.button_icon_color,
                                  fallback_bgColor: bgColor,
                                  fallback_borderColor: borderColor,
                                  fallback_iconColor: iconColor
                                })

                                return (
                                  <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                                    <div
                                      className="flex items-center px-3 py-1.5 rounded-lg shadow-md border backdrop-blur-sm"
                                      style={{
                                        background: `linear-gradient(135deg, ${bgColor} 0%, ${borderColor} 100%)`,
                                        borderColor: borderColor
                                      }}
                                    >
                                    <span
                                      className="text-xs font-semibold truncate max-w-[100px]"
                                      style={{ color: iconColor }}
                                    >
                                      {selectedChatbox.name}
                                    </span>
                                  </div>
                                </div>
                                )
                              })()}
                            </div>
                          ) : null
                        })}
                    </div>
                  </div>
                )}
              </div>

              {/* Ürün Seçimi */}
              <div>
                <h4 className="text-base sm:text-lg font-semibold text-gray-900 mb-3">Ürün Seçimi</h4>
                <div className="relative" ref={productDropdownRef}>
                  <button
                    onClick={() => setIsProductDropdownOpen(!isProductDropdownOpen)}
                    className="w-full p-3 sm:p-4 border border-gray-200 rounded-lg focus:outline-none focus:border-[#FF6925] focus:ring-1 focus:ring-[#FF6925] transition-colors bg-white hover:bg-gray-50 text-left flex items-center justify-between"
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
                                <svg className="w-4 h-4 text-[#FF6925]" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900">Tüm Ürünler</p>
                              <p className="text-xs text-gray-500">Tüm ürünleri entegre edin ({getAvailableProducts().length} ürün)</p>
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
                                    <svg className="w-4 h-4 text-[#FF6925]" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  )}
                                </div>
                                {/* Ürün görseli */}
                                {productImages[product.id] ? (
                                  <img
                                    src={productImages[product.id]}
                                    alt={product.name}
                                    className="w-10 h-10 rounded-lg mr-3 object-cover border border-gray-200"
                                    onError={(e) => {
                                      // Görsel yüklenemezse placeholder göster
                                      e.currentTarget.style.display = 'none'
                                      const placeholder = e.currentTarget.nextElementSibling as HTMLElement
                                      if (placeholder) placeholder.style.display = 'flex'
                                    }}
                                  />
                                ) : null}
                                <div
                                  className={`w-10 h-10 rounded-lg mr-3 bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0 ${productImages[product.id] ? 'hidden' : ''}`}
                                >
                                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                  </svg>
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-0.5">
                                    <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                                    <p className="text-xs text-gray-500">{product.category} • {product.price} TL</p>
                                  </div>
                                  {store && (
                                    <span
                                      className="text-xs px-2 py-0.5 rounded-full font-medium bg-gradient-to-r bg-clip-text text-transparent flex-shrink-0 text-left -ml-2"
                                      style={{
                                        backgroundImage: 'linear-gradient(135deg, rgb(255, 105, 37), rgb(255, 191, 49))'
                                      }}
                                    >
                                      Mağaza: {store.name}
                                    </span>
                                  )}
                                </div>
                                {/* Hangi chatbox'ta entegre olduğunu göster */}
                                {(() => {
                                  const integratedChatbox = Object.entries(allIntegrations).find(([chatboxId, data]) =>
                                    data.products.includes(product.id)
                                  )

                                  if (!integratedChatbox || integratedChatbox[0] === selectedChatbox?.id) {
                                    return null
                                  }

                                  // chatboxList'ten o chatbox'ın renklerini bul
                                  const chatbox = chatboxList?.find(cb => cb.id === integratedChatbox[0])
                                  const bgColor = chatbox?.button_primary_color || chatbox?.primary_color || '#3B82F6'
                                  const borderColor = chatbox?.button_border_color || chatbox?.primary_color || '#3B82F6'
                                  const textColor = chatbox?.button_icon_color || '#FFFFFF'

                                  return (
                                    <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                                      <div
                                        className="flex items-center px-3 py-1.5 rounded-lg shadow-md border backdrop-blur-sm"
                                        style={{
                                          background: `linear-gradient(135deg, ${bgColor} 0%, ${borderColor} 100%)`,
                                          borderColor: borderColor
                                        }}
                                      >
                                        <span className="text-xs font-semibold truncate max-w-[100px]" style={{ color: textColor }}>
                                          {integratedChatbox[1].chatbox_name}
                                        </span>
                                      </div>
                                    </div>
                                  )
                                })()}
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

                  {/* Seçilen Ürünler Özeti */}
                  {isLoadingIntegrations ? (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-600 mb-2">Entegrasyonlar yükleniyor...</p>
                      <div className="space-y-2">
                        {[1, 2].map((i) => (
                          <div key={i} className="flex items-center p-2 bg-white rounded-lg border border-gray-200 animate-pulse">
                            <div className="w-8 h-8 rounded-lg mr-3 bg-gray-200"></div>
                            <div className="flex-1">
                              <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : selectedProducts.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-600 mb-2">Seçilen ürünler:</p>
                      <div className="space-y-2 max-h-[150px] overflow-y-auto pr-1">
                        {selectedProducts
                          .filter(id => id !== 'all') // 'all' ID'sini filtrele
                          .map((productId) => {
                            const product = getAvailableProducts().find(p => p.id === productId)
                            const store = backendStores?.find(s => s.id === product?.store_id)
                            return product ? (
                              <div key={productId} className="flex items-center p-2 bg-white rounded-lg border border-gray-200">
                                {/* Kaldır Butonu */}
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    // 'all' seçiliyse önce onu kaldır, sonra ürünü kaldır
                                    const newSelected = selectedProducts.filter(id => id !== 'all' && id !== productId)
                                    setSelectedProducts(newSelected)
                                  }}
                                  className="mr-2 p-1 hover:bg-gray-100 rounded-full transition-colors group"
                                  title="Seçimi kaldır"
                                >
                                  <X className="w-4 h-4 text-gray-400 group-hover:text-[#FF6925]" />
                                </button>
                                {/* Ürün Görseli */}
                                {productImages[product.id] ? (
                                  <img
                                    src={productImages[product.id]}
                                    alt={product.name}
                                    className="w-8 h-8 rounded-lg mr-3 object-cover border border-gray-200 flex-shrink-0"
                                    onError={(e) => {
                                      e.currentTarget.style.display = 'none'
                                      const placeholder = e.currentTarget.nextElementSibling as HTMLElement
                                      if (placeholder) placeholder.style.display = 'flex'
                                    }}
                                  />
                                ) : null}
                                <div
                                  className={`w-8 h-8 rounded-lg mr-3 bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0 ${productImages[product.id] ? 'hidden' : ''}`}
                                >
                                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                  </svg>
                                </div>
                                {/* İsim ve Bilgiler */}
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-0.5">
                                    <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                                    <p className="text-xs text-gray-500">{product.category} • {product.price} TL</p>
                                  </div>
                                  {store && (
                                    <span
                                      className="text-xs px-2 py-0.5 rounded-full font-medium bg-gradient-to-r bg-clip-text text-transparent flex-shrink-0 text-left -ml-2"
                                      style={{
                                        backgroundImage: 'linear-gradient(135deg, rgb(255, 105, 37), rgb(255, 191, 49))'
                                      }}
                                    >
                                      Mağaza: {store.name}
                                    </span>
                                  )}
                                </div>
                                {/* Chatbox Badge */}
                                {(() => {
                                  if (!selectedChatbox) {
                                    console.log('❌ Product: selectedChatbox yok!')
                                    return null
                                  }

                                  // Fallback: Eğer button renkleri yoksa primary_color kullan
                                  const bgColor = selectedChatbox.button_primary_color || selectedChatbox.primary_color || '#3B82F6'
                                  const borderColor = selectedChatbox.button_border_color || selectedChatbox.primary_color || '#3B82F6'
                                  const iconColor = selectedChatbox.button_icon_color || '#FFFFFF'

                                  console.log('🎨 Product Chatbox Badge Debug:', {
                                    productName: product.name,
                                    chatboxName: selectedChatbox.name,
                                    button_primary_color: selectedChatbox.button_primary_color,
                                    button_border_color: selectedChatbox.button_border_color,
                                    button_icon_color: selectedChatbox.button_icon_color,
                                    fallback_bgColor: bgColor,
                                    fallback_borderColor: borderColor,
                                    fallback_iconColor: iconColor
                                  })

                                  return (
                                    <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                                      <div
                                        className="flex items-center px-3 py-1.5 rounded-lg shadow-md border backdrop-blur-sm"
                                        style={{
                                          background: `linear-gradient(135deg, ${bgColor} 0%, ${borderColor} 100%)`,
                                          borderColor: borderColor
                                        }}
                                      >
                                      <span
                                        className="text-xs font-semibold truncate max-w-[100px]"
                                        style={{ color: iconColor }}
                                      >
                                        {selectedChatbox.name}
                                      </span>
                                    </div>
                                  </div>
                                  )
                                })()}
                              </div>
                            ) : null
                          })}
                      </div>
                    </div>
                  )}
                </div>
              </div>

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