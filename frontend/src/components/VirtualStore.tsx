'use client'

import { Store, MoreHorizontal, ArrowLeft, Star, Plus, X, Upload } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { SketchPicker } from 'react-color'
import ChatboxElements from './ChatboxElements'

// Mağaza verileri artık prop olarak geliyor

// Pazar yeri seçenekleri
const platformOptions = [
  'İKAS',
  'Kendi Web Sitem'
]

// Platform renkleri
const platformColors = {
  'İKAS': { primaryColor: '#232228', secondaryColor: '#DCFB6D', textColor: '#FFFFFF' },
  'Kendi Web Sitem': { primaryColor: '#6434F8', secondaryColor: '#7D56F9', textColor: '#FFFFFF' }
}

// Örnek ürün verileri - Bu normalde props olarak gelir veya state'te tutulur
export const productList = {
  1: [ // TechMall Store ürünleri
    { 
      id: 1, 
      name: 'iPhone 15 Pro', 
      price: '₺45.999', 
      image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300&h=300&fit=crop', 
      category: 'Telefon',
      description: 'iPhone 15 Pro, Titanium tasarımı ve A17 Pro çipi ile güçlü performans sunar. 48 MP ana kamera, Action Button ve USB-C bağlantısı ile teknolojinin zirvesinde.',
      rating: 4.8,
      images: [
        'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=500&h=500&fit=crop'
      ]
    },
    { 
      id: 2, 
      name: 'MacBook Air M2', 
      price: '₺32.999', 
      image: 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=300&h=300&fit=crop', 
      category: 'Laptop',
      description: 'M2 çipli MacBook Air, ince tasarımı ve güçlü performansı ile mükemmel taşınabilirlik sunar. 13.6 inç Liquid Retina ekran ve 18 saate kadar pil ömrü.',
      rating: 4.9,
      images: [
        'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop'
      ]
    },
    { 
      id: 3, 
      name: 'AirPods Pro', 
      price: '₺8.999', 
      image: 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=300&h=300&fit=crop', 
      category: 'Aksesuar',
      description: 'AirPods Pro, aktif gürültü önleme teknolojisi ve şeffaflık modu ile üstün ses deneyimi sunar. Özel tasarım ve uzun pil ömrü.',
      rating: 4.7,
      images: [
        'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1588423771073-b8903fbb85b5?w=500&h=500&fit=crop',
        'https://images.unsplash.com/photo-1590658165737-15a047b7972f?w=500&h=500&fit=crop'
      ]
    },
    { id: 4, name: 'iPad Air', price: '₺19.999', image: 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=300&h=300&fit=crop', category: 'Tablet', description: 'iPad Air, M1 çipi ile güçlü performans ve çok yönlü kullanım imkanı sunar.', rating: 4.6, images: ['https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500&h=500&fit=crop'] },
    { id: 5, name: 'Apple Watch', price: '₺12.999', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop', category: 'Aksesuar', description: 'Apple Watch, sağlık takibi ve akıllı özelliklerle günlük yaşamınızı kolaylaştırır.', rating: 4.5, images: ['https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop'] },
    { id: 6, name: 'Magic Mouse', price: '₺2.999', image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop', category: 'Aksesuar', description: 'Magic Mouse, çok dokunmatik yüzeyi ile hassas kontrol sağlar.', rating: 4.2, images: ['https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&h=500&fit=crop'] }
  ],
  2: [ // Digital Market ürünleri
    { id: 7, name: 'Samsung Galaxy S24', price: '₺28.999', image: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=300&h=300&fit=crop', category: 'Telefon', description: 'Galaxy S24, AI destekli özellikler ve güçlü kamera sistemi ile öne çıkar.', rating: 4.4, images: ['https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&h=500&fit=crop'] },
    { id: 8, name: 'Dell XPS 13', price: '₺35.999', image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop', category: 'Laptop', description: 'Dell XPS 13, premium tasarım ve yüksek performans bir arada sunar.', rating: 4.3, images: ['https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop'] },
    { id: 9, name: 'Sony WH-1000XM5', price: '₺9.999', image: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop', category: 'Aksesuar', description: 'Sony WH-1000XM5, endüstri lideri gürültü önleme teknolojisi sunar.', rating: 4.8, images: ['https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&h=500&fit=crop'] },
    { id: 10, name: 'Microsoft Surface', price: '₺25.999', image: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=300&h=300&fit=crop', category: 'Tablet', description: 'Microsoft Surface, laptop ve tablet deneyimini bir arada sunar.', rating: 4.1, images: ['https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&h=500&fit=crop'] }
  ]
}

// Hazır yorum şablonları
const sampleReviews = [
  { user: 'Ahmet K.', rating: 5, comment: 'Harika bir ürün! Kalitesi gerçekten çok iyi.', date: '2024-01-15' },
  { user: 'Zeynep Y.', rating: 4, comment: 'Performans çok iyi ama fiyat biraz yüksek.', date: '2024-01-14' },
  { user: 'Mehmet A.', rating: 5, comment: 'Mükemmel kalite, herkese tavsiye ederim.', date: '2024-01-13' },
  { user: 'Fatma B.', rating: 4, comment: 'Çok başarılı bir ürün, beğendim.', date: '2024-01-12' },
  { user: 'Can S.', rating: 3, comment: 'İdare eder ama beklentimi tam karşılamadı.', date: '2024-01-11' },
  { user: 'Ayşe D.', rating: 5, comment: 'Harika! Tam aradığım özelliklerde.', date: '2024-01-10' },
  { user: 'Burak T.', rating: 4, comment: 'Güzel bir ürün, kaliteli malzeme.', date: '2024-01-09' },
  { user: 'Elif M.', rating: 5, comment: 'Çok memnun kaldım, hızlı teslimat da güzeldi.', date: '2024-01-08' }
]

// Örnek yorumlar
const reviewsList = {
  1: [
    { id: 1, user: 'Ahmet K.', rating: 5, comment: 'Harika bir telefon! Kamera kalitesi gerçekten muhteşem.', date: '2024-01-15' },
    { id: 2, user: 'Zeynep Y.', rating: 4, comment: 'Performans çok iyi ama fiyat biraz yüksek.', date: '2024-01-10' },
    { id: 3, user: 'Mehmet A.', rating: 5, comment: 'Apple kalitesi her zamanki gibi mükemmel.', date: '2024-01-05' }
  ],
  2: [
    { id: 4, user: 'Fatma B.', rating: 5, comment: 'MacBook Air M2 gerçekten çok hızlı ve sessiz.', date: '2024-01-12' },
    { id: 5, user: 'Can S.', rating: 4, comment: 'Tasarım harika, pil ömrü uzun ama biraz pahalı.', date: '2024-01-08' }
  ],
  3: [
    { id: 6, user: 'Ayşe D.', rating: 5, comment: 'AirPods Pro ses kalitesi müthiş!', date: '2024-01-14' },
    { id: 7, user: 'Burak T.', rating: 4, comment: 'Gürültü önleme özelliği çok başarılı.', date: '2024-01-11' }
  ]
}

export default function VirtualStore({ themeColors, storeList, setStoreList, chatboxList }) {
  const [isVisible, setIsVisible] = useState(false)
  const [selectedStore, setSelectedStore] = useState(null)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [selectedImageIndex, setSelectedImageIndex] = useState(0)
  
  // Ürün listesi state'i
  const [products, setProducts] = useState(productList)
  
  // Mağaza ekleme sayfası state'leri
  const [showAddStorePage, setShowAddStorePage] = useState(false)
  const [showEditStorePage, setShowEditStorePage] = useState(false)
  const [editingStore, setEditingStore] = useState(null)

  // Ürün düzenleme state'leri
  const [showEditProductPage, setShowEditProductPage] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [newStore, setNewStore] = useState({
    name: '',
    description: '',
    platform: '',
    logo: '',
    logoPreview: '',
    primaryColor: '#6434F8',
    secondaryColor: '#7D56F9',
    textColor: '#FFFFFF'
  })

  // Ürün ekleme sayfası state'leri
  const [showAddProductPage, setShowAddProductPage] = useState(false)
  const [newProduct, setNewProduct] = useState({
    name: '',
    price: '',
    category: '',
    description: '',
    images: [],
    imagePreviews: [],
    reviewCount: 0
  })

  // Color picker modal states
  const [activeColorPicker, setActiveColorPicker] = useState(null)

  // Platform dropdown state
  const [isPlatformDropdownOpen, setIsPlatformDropdownOpen] = useState(false)

  // Store card dropdown state
  const [openStoreDropdown, setOpenStoreDropdown] = useState(null)

  // Delete confirmation card state (sağ alt köşe için)
  const [showDeleteCard, setShowDeleteCard] = useState(false)

  // Chatbox states
  const [isChatboxOpen, setIsChatboxOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isClient, setIsClient] = useState(false)

  // Chatbox entegrasyon logic
  const getChatboxForCurrentPage = () => {
    const boxList = chatboxList || []
    if (!boxList || !Array.isArray(boxList)) {
      return null
    }

    // Store sayfasında mıyız?
    if (selectedStore && !selectedProduct) {
      // Store sayfasında uygun chatbox'ları bul
      const eligibleChatboxes = boxList.filter(cb => {
        return cb.storeId === selectedStore.id &&
               cb.integration?.homepage &&
               cb.status === 'active'
      })

      // Eğer birden fazla uygun chatbox varsa, öncelik sırasına göre seç
      if (eligibleChatboxes.length > 0) {
        // En yüksek mesaj sayısına sahip chatbox'ı seç
        const selectedChatbox = eligibleChatboxes.reduce((prev, current) =>
          (current.messages || 0) > (prev.messages || 0) ? current : prev
        )
        return selectedChatbox
      }

      return null
    }

    // Product sayfasında mıyız?
    if (selectedProduct && selectedStore) {
      // Bu ürün için uygun chatbox'ları bul
      const eligibleChatboxes = boxList.filter(cb => {
        if (cb.storeId !== selectedStore.id || cb.status !== 'active') return false

        // Tüm ürünler seçilmişse
        if (cb.integration?.selectedProducts?.includes('all')) return true

        // Bu ürün spesifik olarak seçilmişse
        if (cb.integration?.selectedProducts?.includes(selectedProduct.id)) return true

        return false
      })

      // Eğer birden fazla uygun chatbox varsa, öncelik sırasına göre seç
      if (eligibleChatboxes.length > 0) {
        // En yüksek mesaj sayısına sahip chatbox'ı seç
        const selectedChatbox = eligibleChatboxes.reduce((prev, current) =>
          (current.messages || 0) > (prev.messages || 0) ? current : prev
        )
        return selectedChatbox
      }

      return null
    }

    return null
  }

  const activeChatbox = getChatboxForCurrentPage()


  // SSR hydration fix
  useEffect(() => {
    setIsClient(true)
  }, [])

  const [storeToDelete, setStoreToDelete] = useState(null)
  const [isCardClosing, setIsCardClosing] = useState(false)

  // Product card dropdown state
  const [openProductDropdown, setOpenProductDropdown] = useState(null)

  // Product delete confirmation card state
  const [showProductDeleteCard, setShowProductDeleteCard] = useState(false)
  const [productToDelete, setProductToDelete] = useState(null)
  const [isProductCardClosing, setIsProductCardClosing] = useState(false)

  // Click outside handler için refs
  const colorPickerRefs = useRef({})
  const platformDropdownRef = useRef(null)
  const storeDropdownRef = useRef(null)
  const productDropdownRef = useRef(null)

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

      // Platform dropdown click outside
      if (isPlatformDropdownOpen) {
        if (platformDropdownRef.current && !platformDropdownRef.current.contains(event.target)) {
          setIsPlatformDropdownOpen(false)
        }
      }

      // Store dropdown click outside
      if (openStoreDropdown) {
        if (storeDropdownRef.current && !storeDropdownRef.current.contains(event.target)) {
          setOpenStoreDropdown(null)
        }
      }

      // Product dropdown click outside
      if (openProductDropdown) {
        if (productDropdownRef.current && !productDropdownRef.current.contains(event.target)) {
          setOpenProductDropdown(null)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [activeColorPicker, isPlatformDropdownOpen, openStoreDropdown, openProductDropdown])

  // Platform değiştiğinde color picker'ları kapat
  useEffect(() => {
    if (newStore.platform && newStore.platform !== 'Kendi Web Sitem') {
      setActiveColorPicker(null)
    }
  }, [newStore.platform])

  // Animasyon fonksiyonları
  const getCardAnimation = (index) => {
    const baseClasses = "transition-all duration-700 ease-out"
    if (isVisible) {
      return `${baseClasses} opacity-100 translate-y-0 scale-100`
    }
    return `${baseClasses} opacity-0 translate-y-12 scale-90`
  }

  const getAnimationDelay = (index) => {
    return `${index * 150}ms`
  }

  // Mağaza detayına geri dön
  const handleBackToStores = () => {
    setSelectedStore(null)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Mağaza seçme
  const handleStoreClick = (store) => {
    setSelectedStore(store)
    setSelectedProduct(null)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Ürün seçme
  const handleProductClick = (product) => {
    setSelectedProduct(product)
    setSelectedImageIndex(0)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Ürün detayından geri dön
  const handleBackToProducts = () => {
    setSelectedProduct(null)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Mağaza ekleme sayfasını aç
  const handleAddStoreClick = () => {
    setShowAddStorePage(true)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Mağaza ekleme sayfasını kapat
  const handleBackToStoreList = () => {
    setShowAddStorePage(false)
    setShowEditStorePage(false)
    setEditingStore(null)
    setIsPlatformDropdownOpen(false)
    setOpenStoreDropdown(null)
    setNewStore({
      name: '',
      description: '',
      platform: '',
      logo: '',
      logoPreview: '',
      primaryColor: '#6434F8',
      secondaryColor: '#7D56F9',
      textColor: '#FFFFFF'
    })
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Ürün ekleme sayfasını aç
  const handleAddProductClick = () => {
    setShowAddProductPage(true)
    setSelectedProduct(null)
    // selectedStore'u null yapmıyoruz çünkü hangi mağazaya ürün eklediğimizi bilmek gerekiyor
  }

  // Ürün ekleme/düzenleme sayfasını kapat ve mağaza detayına dön
  const handleBackToProductList = () => {
    setShowAddProductPage(false)
    setShowEditProductPage(false)
    setEditingProduct(null)
    setNewProduct({
      name: '',
      price: '',
      category: '',
      description: '',
      images: [],
      imagePreviews: [],
      reviewCount: 0
    })
    // selectedStore korunacak çünkü mağaza detay sayfasına dönüyoruz
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Logo dosyası yükleme
  const handleLogoUpload = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setNewStore({
          ...newStore,
          logo: file,
          logoPreview: e.target.result
        })
      }
      reader.readAsDataURL(file)
    }
  }

  // Color picker fonksiyonları
  const toggleColorPicker = (colorType) => {
    setActiveColorPicker(activeColorPicker === colorType ? null : colorType)
  }

  const handleColorPickerChange = (colorType, colorResult) => {
    setNewStore(prev => ({
      ...prev,
      [colorType]: colorResult.hex
    }))
  }

  // Mağazayı ilk sıraya taşı (tema renkleri değişsin)
  const moveStoreToFirst = (storeId) => {
    const storeIndex = storeList.findIndex(store => store.id === storeId)
    if (storeIndex > 0) { // Zaten ilk sıradaysa bir şey yapma
      const store = storeList[storeIndex]
      const newList = [store, ...storeList.filter(s => s.id !== storeId)]
      setStoreList(newList)
    }
  }

  // Mağaza düzenleme sayfasını aç
  const handleEditStore = (store) => {
    setEditingStore(store)
    setNewStore({
      name: store.name,
      description: store.description || '',
      platform: store.platform,
      logo: store.logo,
      logoPreview: store.logo,
      primaryColor: store.primaryColor,
      secondaryColor: store.secondaryColor,
      textColor: store.textColor
    })
    setShowEditStorePage(true)
    setIsVisible(false)
    setTimeout(() => setIsVisible(true), 100)
  }

  // Yeni mağaza oluştur - İLK SIRAYA EKLE (tema renkleri değişsin)
  const handleCreateStore = () => {
    if (newStore.name && newStore.description && newStore.platform && newStore.logoPreview) {
      const newStoreData = {
        id: Date.now(), // Unique ID için timestamp kullan
        name: newStore.name,
        description: newStore.description,
        platform: newStore.platform,
        logo: newStore.logoPreview, // Base64 önizleme kullanıyoruz
        status: 'active',
        primaryColor: newStore.primaryColor,
        secondaryColor: newStore.secondaryColor,
        textColor: newStore.textColor
      }

      // YENİ MAĞAZAYI LİSTENİN BAŞINA EKLE - Bu tema renklerini değiştirecek!
      setStoreList([newStoreData, ...storeList])
      handleBackToStoreList()
    }
  }

  // Mağaza güncelleme işlevi
  const handleUpdateStore = () => {
    if (editingStore && newStore.name && newStore.platform && newStore.logoPreview) {
      const updatedStore = {
        ...editingStore,
        name: newStore.name,
        description: newStore.description,
        platform: newStore.platform,
        logo: newStore.logoPreview,
        primaryColor: newStore.primaryColor,
        secondaryColor: newStore.secondaryColor,
        textColor: newStore.textColor
      }

      // Mağaza listesinde güncelle
      const updatedStoreList = storeList.map(store =>
        store.id === editingStore.id ? updatedStore : store
      )
      setStoreList(updatedStoreList)

      // Güncellenen mağaza seçili mağaza ise selectedStore'u da güncelle
      if (selectedStore && selectedStore.id === editingStore.id) {
        setSelectedStore(updatedStore)
      }

      handleBackToStoreList()
    }
  }

  // Mağaza silme onay kartını aç
  const handleDeleteStore = (store) => {
    setStoreToDelete(store)
    setShowDeleteCard(true)
    setOpenStoreDropdown(null)
  }

  // Mağaza silme işlemini onayla
  const confirmDeleteStore = () => {
    if (storeToDelete) {
      // Çıkış animasyonunu başlat
      setIsCardClosing(true)

      // Animasyon bitene kadar bekle, sonra silme işlemini yap
      setTimeout(() => {
        // Mağaza listesinden sil
        const updatedStoreList = storeList.filter(store => store.id !== storeToDelete.id)
        setStoreList(updatedStoreList)

        // Eğer silinen mağaza şu an seçili mağaza ise, seçimi temizle
        if (selectedStore && selectedStore.id === storeToDelete.id) {
          setSelectedStore(null)
          setSelectedProduct(null)
        }

        // Silinen mağazanın ürünlerini de temizle
        setProducts(prev => {
          const newProducts = { ...prev }
          delete newProducts[storeToDelete.id]
          return newProducts
        })

        // Kartı kapat
        setShowDeleteCard(false)
        setStoreToDelete(null)
        setIsCardClosing(false)
      }, 300) // Animasyon süresi kadar bekle
    }
  }

  // Mağaza silme işlemini iptal et
  const cancelDeleteStore = () => {
    // Çıkış animasyonunu başlat
    setIsCardClosing(true)

    // Animasyon bitene kadar bekle, sonra kartı kapat
    setTimeout(() => {
      setShowDeleteCard(false)
      setStoreToDelete(null)
      setIsCardClosing(false)
    }, 300) // Animasyon süresi kadar bekle
  }

  // Ürün düzenleme sayfasını aç
  const handleEditProduct = (product) => {
    setEditingProduct(product)
    setNewProduct({
      name: product.name,
      price: product.price,
      category: product.category,
      description: product.description,
      reviewCount: product.reviewCount || 0, // Mevcut yorum sayısını al, yoksa 0
      images: [],
      imagePreviews: product.images || [product.image] // Mevcut görselleri yükle
    })
    setShowEditProductPage(true)
    setOpenProductDropdown(null)
  }

  // Ürün silme onay kartını aç
  const handleDeleteProduct = (product) => {
    setProductToDelete(product)
    setShowProductDeleteCard(true)
    setOpenProductDropdown(null)
  }

  // Ürün silme işlemini onayla
  const confirmDeleteProduct = () => {
    if (productToDelete && selectedStore) {
      // Çıkış animasyonunu başlat
      setIsProductCardClosing(true)

      // Animasyon bitene kadar bekle, sonra silme işlemini yap
      setTimeout(() => {
        // Ürünü ilgili mağazanın ürün listesinden sil
        setProducts(prev => {
          const newProducts = { ...prev }
          if (newProducts[selectedStore.id]) {
            newProducts[selectedStore.id] = newProducts[selectedStore.id].filter(
              product => product.id !== productToDelete.id
            )
          }
          return newProducts
        })

        // Eğer silinen ürün şu an seçili ürün ise, seçimi temizle
        if (selectedProduct && selectedProduct.id === productToDelete.id) {
          setSelectedProduct(null)
        }

        // Kartı kapat
        setShowProductDeleteCard(false)
        setProductToDelete(null)
        setIsProductCardClosing(false)
      }, 300) // Animasyon süresi kadar bekle
    }
  }

  // Ürün silme işlemini iptal et
  const cancelDeleteProduct = () => {
    // Çıkış animasyonunu başlat
    setIsProductCardClosing(true)

    // Animasyon bitene kadar bekle, sonra kartı kapat
    setTimeout(() => {
      setShowProductDeleteCard(false)
      setProductToDelete(null)
      setIsProductCardClosing(false)
    }, 300) // Animasyon süresi kadar bekle
  }

  // Eğer bir ürün seçildiyse ürün detayını göster
  if (selectedProduct && selectedStore) {
    const reviews = reviewsList[selectedProduct.id] || []
    
    return (
      <div className="relative">
        
        {/* Mağaza Banner */}
        <div 
          className="rounded-xl p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 mb-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5" 
          style={{ 
            background: `linear-gradient(135deg, ${selectedStore.primaryColor}, ${selectedStore.secondaryColor})`
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Geri Dön Butonu */}
              <button
                onClick={handleBackToProducts}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 sm:w-5 h-4 sm:h-5 text-white/70" />
              </button>
              
              {/* Mağaza Logo */}
              <div className="w-8 sm:w-10 lg:w-12 h-8 sm:h-10 lg:h-12 rounded-full flex items-center justify-center border border-white/30 overflow-hidden bg-white/20 backdrop-blur-sm">
                <img 
                  src={selectedStore.logo} 
                  alt={selectedStore.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Mağaza Bilgileri */}
              <div>
                <h2 className="text-base sm:text-lg lg:text-xl font-bold" style={{ color: selectedStore.textColor || '#FFFFFF' }}>{selectedStore.name}</h2>
                <p className="text-xs sm:text-sm" style={{ color: `${selectedStore.textColor || '#FFFFFF'}80` }}>Ürün Detayı</p>
              </div>
            </div>
          </div>
        </div>

        {/* Ürün Detay İçeriği */}
        <div className="flex flex-col lg:flex-row gap-4 sm:gap-6 lg:gap-8 mx-3 sm:mx-6 lg:mx-12 xl:mx-20">
          
          {/* Sol Taraf - Ürün Görselleri */}
          <div className="lg:w-1/2">
            <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-fit">
              {/* Ana Görsel */}
              <div className="mb-3 sm:mb-4">
                <img 
                  src={selectedProduct.images[selectedImageIndex]} 
                  alt={selectedProduct.name}
                  className="w-full aspect-square object-cover rounded-lg border border-gray-200"
                />
              </div>
              
              {/* Küçük Görseller */}
              {selectedProduct.images.length > 1 && (
                <div className="flex space-x-2 sm:space-x-3 overflow-x-auto">
                  {selectedProduct.images.map((image, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`flex-shrink-0 w-16 sm:w-20 h-16 sm:h-20 rounded-lg border-2 overflow-hidden ${
                        selectedImageIndex === index ? 'border-[#6434F8]' : 'border-gray-200'
                      }`}
                    >
                      <img 
                        src={image} 
                        alt={`${selectedProduct.name} ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sağ Taraf - Ürün Bilgileri */}
          <div className="lg:w-1/2">
            <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-fit">
              
              {/* Ürün Başlık ve Fiyat */}
              <div className="mb-6">
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#1F1F1F] mb-2">{selectedProduct.name}</h1>
                <p className="text-sm sm:text-base lg:text-lg text-[#666] mb-3 sm:mb-4">{selectedProduct.category}</p>
                <div 
                  className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-3 sm:mb-4"
                  style={{ color: selectedStore.primaryColor }}
                >
                  {selectedProduct.price}
                </div>
                
                {/* Rating */}
                <div className="flex items-center space-x-2 mb-4 sm:mb-6">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star 
                        key={i} 
                        className={`w-4 sm:w-5 h-4 sm:h-5 ${i < Math.floor(selectedProduct.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                      />
                    ))}
                  </div>
                  <span className="text-xs sm:text-sm text-[#666]">({selectedProduct.rating})</span>
                </div>
              </div>

              {/* Ürün Açıklaması */}
              <div className="mb-6 sm:mb-8">
                <h3 className="text-lg sm:text-xl font-bold text-[#1F1F1F] mb-2 sm:mb-3">Ürün Açıklaması</h3>
                <p className="text-sm sm:text-base text-[#666] leading-relaxed">{selectedProduct.description}</p>
              </div>

              {/* Yorumlar Bölümü */}
              {reviews.length > 0 && (
                <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
                  <h3 className="text-lg sm:text-xl font-bold text-[#1F1F1F] mb-3 sm:mb-4">Müşteri Yorumları</h3>
                  
                  <div className="space-y-3 sm:space-y-4">
                    {reviews.map((review) => (
                      <div key={review.id} className="border-b border-gray-100 pb-3 sm:pb-4 last:border-b-0">
                        <div className="flex items-start justify-between mb-1.5 sm:mb-2">
                          <div className="flex items-center space-x-2 sm:space-x-3">
                            <div 
                              className="w-6 sm:w-8 h-6 sm:h-8 rounded-full flex items-center justify-center"
                              style={{
                                background: `linear-gradient(to bottom right, ${selectedStore.primaryColor}10, ${selectedStore.secondaryColor}10)`
                              }}
                            >
                              <span 
                                className="text-xs font-medium"
                                style={{ color: selectedStore.primaryColor }}
                              >
                                {review.user.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <h4 className="text-xs sm:text-sm font-medium text-[#1F1F1F]">{review.user}</h4>
                              <p className="text-xs text-[#666]">{review.date}</p>
                            </div>
                          </div>
                          <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`w-2.5 sm:w-3 h-2.5 sm:h-3 ${i < review.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                              />
                            ))}
                          </div>
                        </div>
                        <p className="text-xs sm:text-sm text-[#666] leading-relaxed">{review.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sepete Ekle Butonu */}
              <button 
                className="w-full text-white py-3 sm:py-4 rounded-lg font-medium text-base sm:text-lg transition-all duration-300 mt-4 sm:mt-6"
                style={{
                  background: `linear-gradient(135deg, ${selectedStore.primaryColor}, ${selectedStore.secondaryColor})`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
                  e.currentTarget.style.boxShadow = `0 4px 12px ${selectedStore.primaryColor}40`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Sepete Ekle
              </button>
            </div>
          </div>
        </div>

        {/* Floating ChatboxElements - Ürün Detay Sayfası için (Küçük Boyut) */}
        {isClient && activeChatbox && (
          <div className="fixed bottom-4 right-8 z-1">
            <div style={{transform: 'scale(0.7)', transformOrigin: 'bottom right'}}>
              <ChatboxElements
                chatboxTitle={activeChatbox.name}
                initialMessage="Hello! It's Orbina here!"
                colors={{
                  primary: activeChatbox.colors?.primary,
                  aiMessage: activeChatbox.colors?.aiMessage,
                  userMessage: activeChatbox.colors?.userMessage,
                  borderColor: activeChatbox.colors?.borderColor,
                  aiTextColor: activeChatbox.colors?.aiTextColor,
                  userTextColor: activeChatbox.colors?.userTextColor,
                  buttonPrimary: activeChatbox.colors?.buttonPrimary,
                  buttonBorderColor: activeChatbox.colors?.buttonBorderColor,
                  buttonIcon: activeChatbox.colors?.buttonIcon
                }}
                isVisible={isChatboxOpen}
                onToggle={() => setIsChatboxOpen(!isChatboxOpen)}
                panelZIndex={1}
                buttonZIndex={50}
                className=""
                style={{}}
              />
            </div>
          </div>
        )}

      </div>
    )
  }

  // Eğer mağaza ekleme veya düzenleme sayfası açıksa göster
  if (showAddStorePage || showEditStorePage) {
    return (
      <div className="relative">
        
        {/* Mağaza Banner */}
        <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 mb-4 sm:mb-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
              {/* Geri Dön Butonu */}
              <button
                onClick={handleBackToStoreList}
                className="p-1.5 sm:p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 sm:w-5 h-4 sm:h-5 text-[#666]" />
              </button>
              
              {/* İkon */}
              <div 
                className="w-8 sm:w-10 lg:w-12 h-8 sm:h-10 lg:h-12 rounded-full flex items-center justify-center border"
                style={{
                  background: `linear-gradient(to bottom right, ${themeColors.primary}10, ${themeColors.secondary}10)`,
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
                  {showEditStorePage ? 'Mağaza Düzenle' : 'Yeni Mağaza Ekle'}
                </h2>
                <p className="text-xs sm:text-sm text-[#666]">
                  {showEditStorePage ? 'Mağaza bilgilerini düzenleyin' : 'Mağaza bilgilerini girin'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Mağaza Ekleme Formu */}
        <div className="flex flex-col xl:flex-row gap-4 sm:gap-6 xl:gap-8 mx-3 sm:mx-6 lg:mx-12 xl:mx-20">
          
          {/* Sol Taraf - Form */}
          <div className="w-full xl:w-1/2">
            <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-fit space-y-3 sm:space-y-4 lg:space-y-6">
              
              {/* Mağaza İsmi */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Mağaza İsmi
                </label>
                <input
                  type="text"
                  value={newStore.name}
                  onChange={(e) => setNewStore({...newStore, name: e.target.value})}
                  placeholder="Mağaza ismini girin"
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Mağaza Açıklaması */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Mağaza Açıklaması
                </label>
                <textarea
                  value={newStore.description}
                  onChange={(e) => setNewStore({...newStore, description: e.target.value})}
                  placeholder="Mağazanızın açıklamasını yazın"
                  rows={4}
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors resize-none text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Satış Platformu */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Satış Platformu
                </label>
                <div className="relative" ref={platformDropdownRef}>
                  <button
                    type="button"
                    onClick={() => setIsPlatformDropdownOpen(!isPlatformDropdownOpen)}
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 bg-white text-left flex items-center justify-between text-sm sm:text-base"
                  >
                    <span className={newStore.platform ? 'text-gray-900' : 'text-gray-500'}>
                      {newStore.platform || 'Satış platformunu seçin'}
                    </span>
                    <svg
                      className={`w-4 sm:w-5 h-4 sm:h-5 text-gray-400 transition-transform ${isPlatformDropdownOpen ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isPlatformDropdownOpen && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                      {platformOptions.map((platform) => (
                        <button
                          key={platform}
                          type="button"
                          onClick={() => {
                            const colors = platformColors[platform]
                            setNewStore({
                              ...newStore, 
                              platform: platform,
                              primaryColor: colors.primaryColor,
                              secondaryColor: colors.secondaryColor,
                              textColor: colors.textColor
                            })
                            setIsPlatformDropdownOpen(false)
                          }}
                          className="w-full px-3 sm:px-4 py-2 sm:py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors text-gray-900 border-b border-gray-100 last:border-b-0 text-sm sm:text-base"
                        >
                          {platform}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <p className="text-xs text-[#666] mt-1">Mağazanızın satış yaptığı platformu seçin</p>
              </div>

              {/* Logo Yükleme */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Mağaza Logosu
                </label>
                <div className="space-y-3">
                  <div 
                    className="w-full h-24 sm:h-28 lg:h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer transition-colors"
                    onClick={() => document.getElementById('logoInput').click()}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = themeColors.primary;
                      e.currentTarget.style.backgroundColor = `${themeColors.primary}08`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#d1d5db';
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    {newStore.logoPreview ? (
                      <img 
                        src={newStore.logoPreview} 
                        alt="Logo Preview"
                        className="max-w-full max-h-full object-contain rounded-lg"
                      />
                    ) : (
                      <div className="text-center">
                        <Upload 
                          className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8 mx-auto mb-1 sm:mb-2" 
                          style={{ color: themeColors.primary }}
                        />
                        <p className="text-xs sm:text-sm text-gray-600">Logo yüklemek için tıklayın</p>
                        <p className="text-xs text-gray-400 mt-0.5 sm:mt-1 hidden sm:block">JPG, PNG, SVG (Max 5MB)</p>
                      </div>
                    )}
                  </div>
                  <input
                    id="logoInput"
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                  />
                  {newStore.logoPreview && (
                    <button
                      onClick={() => setNewStore({...newStore, logo: '', logoPreview: ''})}
                      className="text-sm text-red-500 hover:text-red-700 transition-colors"
                    >
                      Logoyu kaldır
                    </button>
                  )}
                </div>
              </div>

              {/* Renk Seçimi */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-2 sm:mb-3">
                  Mağaza Renkleri
                </label>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                  {/* Ana Renk */}
                  <div className="flex flex-col space-y-1.5 sm:space-y-2 relative flex-1">
                    <label className="block text-xs text-[#666] mb-1 sm:mb-2">Ana Renk</label>
                    <div 
                      className="flex items-center space-x-2 bg-white rounded-lg sm:rounded-xl shadow-sm p-2 sm:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => newStore.platform === 'Kendi Web Sitem' && toggleColorPicker('primaryColor')}
                      data-color-button={newStore.platform === 'Kendi Web Sitem' ? true : undefined}
                    >
                      <div className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md sm:rounded-lg flex items-center justify-center text-xs sm:text-sm border border-gray-200">
                        🎨
                      </div>
                      <div className="relative flex-1 h-6 sm:h-7 lg:h-8">
                        <div 
                          className="w-full h-full rounded-md sm:rounded-lg border border-gray-400 sm:border-[#555] shadow-inner" 
                          style={{ backgroundColor: newStore.primaryColor }}
                        ></div>
                      </div>
                    </div>
                    {activeColorPicker === 'primaryColor' && newStore.platform === 'Kendi Web Sitem' && (
                      <div ref={(el) => colorPickerRefs.current['primaryColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                        <SketchPicker
                          color={newStore.primaryColor}
                          onChange={(color) => handleColorPickerChange('primaryColor', color)}
                        />
                      </div>
                    )}
                  </div>

                  {/* İkincil Renk */}
                  <div className="flex flex-col space-y-1.5 sm:space-y-2 relative flex-1">
                    <label className="block text-xs text-[#666] mb-1 sm:mb-2">İkincil Renk</label>
                    <div 
                      className="flex items-center space-x-2 bg-white rounded-lg sm:rounded-xl shadow-sm p-2 sm:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => newStore.platform === 'Kendi Web Sitem' && toggleColorPicker('secondaryColor')}
                      data-color-button={newStore.platform === 'Kendi Web Sitem' ? true : undefined}
                    >
                      <div className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md sm:rounded-lg flex items-center justify-center text-xs sm:text-sm border border-gray-200">
                        🎨
                      </div>
                      <div className="relative flex-1 h-6 sm:h-7 lg:h-8">
                        <div 
                          className="w-full h-full rounded-md sm:rounded-lg border border-gray-400 sm:border-[#555] shadow-inner" 
                          style={{ backgroundColor: newStore.secondaryColor }}
                        ></div>
                      </div>
                    </div>
                    {activeColorPicker === 'secondaryColor' && newStore.platform === 'Kendi Web Sitem' && (
                      <div ref={(el) => colorPickerRefs.current['secondaryColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                        <SketchPicker
                          color={newStore.secondaryColor}
                          onChange={(color) => handleColorPickerChange('secondaryColor', color)}
                        />
                      </div>
                    )}
                  </div>

                  {/* Yazı Rengi */}
                  <div className="flex flex-col space-y-1.5 sm:space-y-2 relative flex-1">
                    <label className="block text-xs text-[#666] mb-1 sm:mb-2">Yazı Rengi</label>
                    <div 
                      className="flex items-center space-x-2 bg-white rounded-lg sm:rounded-xl shadow-sm p-2 sm:p-3 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => newStore.platform === 'Kendi Web Sitem' && toggleColorPicker('textColor')}
                      data-color-button={newStore.platform === 'Kendi Web Sitem' ? true : undefined}
                    >
                      <div className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md sm:rounded-lg flex items-center justify-center text-xs sm:text-sm border border-gray-200">
                        🎨
                      </div>
                      <div className="relative flex-1 h-6 sm:h-7 lg:h-8">
                        <div 
                          className="w-full h-full rounded-md sm:rounded-lg border border-gray-400 sm:border-[#555] shadow-inner" 
                          style={{ backgroundColor: newStore.textColor }}
                        ></div>
                      </div>
                    </div>
                    {activeColorPicker === 'textColor' && newStore.platform === 'Kendi Web Sitem' && (
                      <div ref={(el) => colorPickerRefs.current['textColor'] = el} className="absolute top-full left-0 z-50 mt-2">
                        <SketchPicker
                          color={newStore.textColor}
                          onChange={(color) => handleColorPickerChange('textColor', color)}
                        />
                      </div>
                    )}
                  </div>

                </div>
              </div>

              {/* Butonlar */}
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-3 sm:pt-4">
                <button
                  onClick={handleBackToStoreList}
                  className="flex-1 px-4 sm:px-6 py-2 sm:py-3 border border-gray-200 text-[#666] rounded-lg hover:bg-gray-50 transition-colors text-sm sm:text-base"
                >
                  İptal
                </button>
                <button
                  onClick={showEditStorePage ? handleUpdateStore : handleCreateStore}
                  disabled={showEditStorePage
                    ? (!newStore.name || !newStore.platform || !newStore.logoPreview ||
                       (editingStore &&
                        newStore.name === editingStore.name &&
                        newStore.description === (editingStore.description || '') &&
                        newStore.platform === editingStore.platform &&
                        newStore.logoPreview === editingStore.logo &&
                        newStore.primaryColor === editingStore.primaryColor &&
                        newStore.secondaryColor === editingStore.secondaryColor &&
                        newStore.textColor === editingStore.textColor))
                    : (!newStore.name || !newStore.description || !newStore.platform || !newStore.logoPreview)
                  }
                  className="flex-1 px-4 sm:px-6 py-2 sm:py-3 text-white rounded-lg font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                  style={{
                    background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                  }}
                  onMouseEnter={(e) => {
                    if (!e.currentTarget.disabled) {
                      e.currentTarget.style.transform = 'scale(1.02)';
                      e.currentTarget.style.boxShadow = `0 4px 12px ${themeColors.primary}40`;
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {showEditStorePage ? 'Değişiklikleri Kaydet' : 'Mağazayı Oluştur'}
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
                  Önizleme
                </span>
              </h3>
              
              {/* Mağaza Kartı Önizleme */}
              <div 
                className="rounded-lg sm:rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100"
                style={{ 
                  height: '160px',
                  background: `linear-gradient(135deg, ${newStore.primaryColor}, ${newStore.secondaryColor})`
                }}
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-2 sm:mb-3 lg:mb-4">
                  <div className="flex items-center space-x-1 sm:space-x-1.5">
                    <div className="w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full bg-white"></div>
                    <div className="bg-white/20 backdrop-blur-sm px-2 sm:px-3 py-0.5 rounded-full min-w-fit whitespace-nowrap">
                      <span className="text-xs font-bold text-white hidden sm:inline">ÖNIZLEME</span>
                      <span className="text-xs font-bold text-white sm:hidden">ÖN</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-0.5 sm:space-x-1">
                    <MoreHorizontal className="w-3 sm:w-4 h-3 sm:h-4 text-white/70" />
                  </div>
                </div>

                {/* Mağaza Bilgileri */}
                <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
                  {/* Logo */}
                  <div className="w-14 sm:w-16 lg:w-18 h-14 sm:h-16 lg:h-18 rounded-full flex items-center justify-center border border-white/30 flex-shrink-0 overflow-hidden bg-white/20 backdrop-blur-sm">
                    {newStore.logoPreview ? (
                      <img 
                        src={newStore.logoPreview} 
                        alt="Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-white/10 flex items-center justify-center text-white/60">
                        <Upload className="w-5 sm:w-6 lg:w-7 h-5 sm:h-6 lg:h-7" />
                      </div>
                    )}
                  </div>

                  {/* Bilgiler */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xs sm:text-sm lg:text-base font-bold mb-0.5 sm:mb-1 truncate" style={{ color: newStore.textColor }}>
                      {newStore.name || 'Mağaza İsmi'}
                    </h3>
                    <p className="text-xs sm:text-xs mb-1 sm:mb-1.5 lg:mb-2 truncate" style={{ color: `${newStore.textColor}80` }}>{newStore.platform || 'Platform'} Platform</p>
                    <div className="inline-flex px-1.5 sm:px-2 py-0.5 rounded-full text-xs font-medium bg-white/20 backdrop-blur-sm" style={{ color: newStore.textColor }}>
                      <span className="hidden sm:inline">Aktif Çalışıyor</span>
                      <span className="sm:hidden">Aktif</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Açıklama Önizleme */}
              {newStore.description && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-[#1F1F1F] mb-2">Mağaza Açıklaması:</h4>
                  <p className="text-sm text-[#666]">{newStore.description}</p>
                </div>
              )}

              {/* Renk Önizleme */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-[#1F1F1F] mb-3">Seçilen Renkler:</h4>
                <div className="flex space-x-4">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-6 h-6 rounded-full border border-gray-300"
                      style={{ backgroundColor: newStore.primaryColor }}
                    ></div>
                    <span className="text-xs text-[#666]">Ana Renk</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-6 h-6 rounded-full border border-gray-300"
                      style={{ backgroundColor: newStore.secondaryColor }}
                    ></div>
                    <span className="text-xs text-[#666]">İkincil Renk</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-6 h-6 rounded-full border border-gray-300"
                      style={{ backgroundColor: newStore.textColor }}
                    ></div>
                    <span className="text-xs text-[#666]">Yazı Rengi</span>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>
    )
  }

  // Eğer ürün ekleme veya düzenleme sayfası açıksa göster
  if (showAddProductPage || showEditProductPage) {
    return (
      <div className="relative">
        
        {/* Ürün Ekleme Banner */}
        <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 mb-4 sm:mb-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
              {/* Geri Dön Butonu */}
              <button
                onClick={handleBackToProductList}
                className="p-1.5 sm:p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 sm:w-5 h-4 sm:h-5 text-[#666]" />
              </button>
              
              {/* İkon */}
              <div 
                className="w-8 sm:w-10 lg:w-12 h-8 sm:h-10 lg:h-12 rounded-full flex items-center justify-center border"
                style={{
                  background: `linear-gradient(to bottom right, ${themeColors.primary}10, ${themeColors.secondary}10)`,
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
                  {showEditProductPage ? 'Ürün Düzenle' : 'Yeni Ürün Ekle'}
                </h2>
                <p className="text-xs sm:text-sm text-[#666]">
                  {showEditProductPage ? 'Ürün bilgilerini düzenleyin' : 'Ürün bilgilerini girin'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Ürün Ekleme Formu */}
        <div className="flex flex-col xl:flex-row gap-4 sm:gap-6 xl:gap-8 mx-3 sm:mx-6 lg:mx-12 xl:mx-20">
          
          {/* Sol Taraf - Form */}
          <div className="w-full xl:w-1/2">
            <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-full space-y-3 sm:space-y-4 lg:space-y-6">
              
              {/* Ürün Adı */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Ürün Adı
                </label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                  placeholder="Ürün adını girin"
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Fiyat */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Fiyat
                </label>
                <input
                  type="text"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                  placeholder="₺0.00 - Ürün fiyatını girin"
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Kategori */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Kategori
                </label>
                <input
                  type="text"
                  value={newProduct.category}
                  onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                  placeholder="Telefon, Laptop, Aksesuar vb. - Kategori girin"
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Açıklama */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Ürün Açıklaması
                </label>
                <textarea
                  value={newProduct.description}
                  onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                  placeholder="Ürün hakkında detaylı bilgi, özellikler, kullanım alanları... Buraya ürünün açıklamasını yazın."
                  rows="4"
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-[#6434F8] focus:ring-1 focus:ring-[#6434F8] transition-colors resize-none text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                />
              </div>

              {/* Müşteri Yorum Sayısı */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Müşteri Yorum Sayısı
                </label>
                <div className="grid grid-cols-4 gap-2 sm:gap-3">
                  {[0, 1, 2, 3].map((count) => (
                    <button
                      key={count}
                      type="button"
                      onClick={() => setNewProduct({...newProduct, reviewCount: count})}
                      className={`px-3 sm:px-4 py-2 sm:py-3 border rounded-lg font-medium transition-all duration-300 text-sm sm:text-base ${
                        newProduct.reviewCount === count
                          ? 'text-white'
                          : 'border-gray-200 bg-white text-[#666]'
                      }`}
                      style={{
                        ...(newProduct.reviewCount === count && {
                          borderColor: themeColors.primary,
                          background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                        }),
                        ...(newProduct.reviewCount !== count && {
                          borderColor: '#e5e7eb'
                        })
                      }}
                      onMouseEnter={(e) => {
                        if (newProduct.reviewCount !== count) {
                          e.currentTarget.style.borderColor = themeColors.primary;
                          e.currentTarget.style.color = themeColors.primary;
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (newProduct.reviewCount !== count) {
                          e.currentTarget.style.borderColor = '#e5e7eb';
                          e.currentTarget.style.color = '#666';
                        }
                      }}
                    >
                      {count} Yorum
                    </button>
                  ))}
                </div>
                <p className="text-xs text-[#666] mt-1 sm:mt-2">
                  Seçilen sayı kadar otomatik müşteri yorumu eklenecek
                </p>
              </div>

              {/* Ürün Görselleri */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-[#1F1F1F] mb-1 sm:mb-2">
                  Ürün Görselleri
                </label>
                <div className="space-y-3">
                  {/* Yüklenen görseller grid */}
                  {newProduct.imagePreviews.length > 0 && (
                    <div className="grid grid-cols-3 gap-2 sm:gap-3">
                      {newProduct.imagePreviews.map((preview, index) => (
                        <div key={index} className="relative group">
                          <img 
                            src={preview} 
                            alt={`Ürün görseli ${index + 1}`}
                            className="w-full aspect-square object-cover rounded-lg border border-gray-200"
                          />
                          <button
                            onClick={() => {
                              setNewProduct(prev => ({
                                ...prev,
                                images: prev.images.filter((_, i) => i !== index),
                                imagePreviews: prev.imagePreviews.filter((_, i) => i !== index)
                              }))
                            }}
                            className="absolute -top-1 -right-1 w-5 sm:w-6 h-5 sm:h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="w-3 sm:w-4 h-3 sm:h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div 
                    className="w-full h-24 sm:h-28 lg:h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer transition-colors"
                    onClick={() => document.getElementById('productImageInput').click()}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = themeColors.primary;
                      e.currentTarget.style.backgroundColor = `${themeColors.primary}08`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#d1d5db';
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <div className="text-center">
                      <Upload 
                        className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8 mx-auto mb-1 sm:mb-2" 
                        style={{ color: themeColors.primary }}
                      />
                      <p className="text-xs sm:text-sm text-gray-600">
                        {newProduct.imagePreviews.length > 0 
                          ? 'Daha fazla görsel eklemek için tıklayın' 
                          : 'Ürün görsellerini yüklemek için tıklayın'
                        }
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5 sm:mt-1 hidden sm:block">JPG, PNG (Max 5MB)</p>
                    </div>
                  </div>
                  <input
                    id="productImageInput"
                    type="file"
                    multiple
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const files = Array.from(e.target.files)
                      if (files.length > 0) {
                        const validFiles = files.filter(file => file.type.startsWith('image/'))
                        
                        const fileReaders = validFiles.map(file => {
                          return new Promise((resolve) => {
                            const reader = new FileReader()
                            reader.onload = (event) => {
                              resolve({
                                file: file,
                                preview: event.target.result
                              })
                            }
                            reader.readAsDataURL(file)
                          })
                        })

                        Promise.all(fileReaders).then(results => {
                          setNewProduct(prev => ({
                            ...prev,
                            images: [...prev.images, ...results.map(r => r.file)],
                            imagePreviews: [...prev.imagePreviews, ...results.map(r => r.preview)]
                          }))
                        })
                      }
                    }}
                  />
                </div>
              </div>

              {/* Butonlar */}
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-3 sm:pt-4">
                <button
                  onClick={handleBackToProductList}
                  className="flex-1 px-4 sm:px-6 py-2 sm:py-3 border border-gray-200 text-[#666] rounded-lg hover:bg-gray-50 transition-colors text-sm sm:text-base"
                >
                  İptal
                </button>
                <button
                  onClick={() => {
                    if (selectedStore && newProduct.name && newProduct.price && newProduct.category && newProduct.description && newProduct.imagePreviews.length > 0) {

                      if (showEditProductPage && editingProduct) {
                        // Ürün düzenleme işlemi
                        const updatedProduct = {
                          ...editingProduct,
                          name: newProduct.name,
                          price: newProduct.price,
                          category: newProduct.category,
                          description: newProduct.description,
                          image: newProduct.imagePreviews[0], // Ana görsel
                          images: newProduct.imagePreviews, // Tüm görseller
                        }

                        // Ürünü products state'inde güncelle
                        setProducts(prev => ({
                          ...prev,
                          [selectedStore.id]: prev[selectedStore.id].map(product =>
                            product.id === editingProduct.id ? updatedProduct : product
                          )
                        }))

                        console.log('Ürün güncellendi:', updatedProduct, 'Mağaza:', selectedStore.name)

                      } else {
                        // Yeni ürün ekleme işlemi
                        // Seçilen sayı kadar hazır yorum oluştur
                        const selectedReviews = newProduct.reviewCount > 0
                          ? sampleReviews.slice(0, newProduct.reviewCount).map((review, index) => ({
                              ...review,
                              id: Date.now() + index
                            }))
                          : []

                        // Ortalama rating hesapla (yorumlar varsa)
                        const averageRating = selectedReviews.length > 0
                          ? selectedReviews.reduce((sum, review) => sum + review.rating, 0) / selectedReviews.length
                          : 4.5

                        // Yeni ürün oluştur
                        const newProductData = {
                          id: Date.now(), // Unique ID için timestamp kullan
                          name: newProduct.name,
                          price: newProduct.price,
                          category: newProduct.category,
                          description: newProduct.description,
                          image: newProduct.imagePreviews[0], // Ana görsel
                          images: newProduct.imagePreviews, // Tüm görseller
                          rating: Math.round(averageRating * 10) / 10 // Rating'i yuvarla
                        }

                        // Ürünü seçili mağazanın ürün listesine ekle
                        setProducts(prev => ({
                          ...prev,
                          [selectedStore.id]: [
                            ...(prev[selectedStore.id] || []),
                            newProductData
                          ]
                        }))

                        // Eğer yorum varsa, yorumları da ekle
                        if (selectedReviews.length > 0) {
                          // reviewsList'e de ekle (ürün detay sayfasında görünmesi için)
                          const currentReviews = { ...reviewsList }
                          currentReviews[newProductData.id] = selectedReviews
                          // Bu normalde bir state olmalı ama şimdilik global değişken kullanıyoruz
                          Object.assign(reviewsList, currentReviews)
                        }

                        console.log('Yeni ürün oluşturuldu:', newProductData, 'Mağaza:', selectedStore.name, 'Yorumlar:', selectedReviews)
                      }

                      // Form'u temizle ve mağaza detay sayfasına dön
                      handleBackToProductList()
                    }
                  }}
                  disabled={showEditProductPage
                    ? (!newProduct.name || !newProduct.price || !newProduct.category || !newProduct.description || newProduct.imagePreviews.length === 0 ||
                       (editingProduct &&
                        newProduct.name === editingProduct.name &&
                        newProduct.price === editingProduct.price &&
                        newProduct.category === editingProduct.category &&
                        newProduct.description === editingProduct.description &&
                        newProduct.reviewCount === (editingProduct.reviewCount || 0) &&
                        JSON.stringify(newProduct.imagePreviews) === JSON.stringify(editingProduct.images || [editingProduct.image])))
                    : (!newProduct.name || !newProduct.price || !newProduct.category || !newProduct.description || newProduct.imagePreviews.length === 0)
                  }
                  className="flex-1 px-4 sm:px-6 py-2 sm:py-3 text-white rounded-lg font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                  style={{
                    background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
                  }}
                  onMouseEnter={(e) => {
                    if (!e.currentTarget.disabled) {
                      e.currentTarget.style.transform = 'scale(1.02)';
                      e.currentTarget.style.boxShadow = `0 4px 12px ${themeColors.primary}40`;
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {showEditProductPage ? 'Değişiklikleri Kaydet' : 'Ürünü Oluştur'}
                </button>
              </div>

            </div>
          </div>

          {/* Sağ Taraf - Önizleme */}
          <div className="w-full xl:w-1/2">
            <div className="bg-white rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 h-full flex flex-col">
              <h3 className="text-base sm:text-lg font-bold mb-3 sm:mb-4">
                <span 
                  className="bg-gradient-to-r bg-clip-text text-transparent"
                  style={{
                    backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                  }}
                >
                  Önizleme
                </span>
              </h3>
              
              {/* Ürün Kartı Önizleme */}
              <div className="bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 flex-1 flex flex-col">
                {/* Görsel Alan */}
                <div className="mb-4 sm:mb-6 flex-1 w-full flex justify-center">
                  <div className="aspect-[3/4] w-[70%] border-2 border-dashed border-gray-200 rounded-md sm:rounded-lg flex items-center justify-center overflow-hidden">
                    {newProduct.imagePreviews.length > 0 ? (
                      <img 
                        src={newProduct.imagePreviews[0]} 
                        alt="Ürün önizleme"
                        className="w-full h-full object-cover rounded-md sm:rounded-lg"
                      />
                    ) : (
                      <div className="text-center">
                        <div className="w-8 sm:w-10 h-8 sm:h-10 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                          <span className="text-gray-400 text-xs">📷</span>
                        </div>
                        <p className="text-xs text-gray-400">Ürün Görseli</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Ürün Bilgileri */}
                <div className="text-center">
                  <div className="mb-4">
                    <h3 className="text-sm sm:text-base lg:text-lg font-bold text-[#1F1F1F] mb-2">
                      {newProduct.name || 'Ürün Adı'}
                    </h3>
                    <p className="text-sm text-[#666] mb-3">
                      {newProduct.category || 'Kategori'}
                    </p>
                  </div>
                  <div 
                    className="text-lg sm:text-xl lg:text-2xl font-bold"
                    style={{ color: themeColors.primary }}
                  >
                    {newProduct.price || '₺0.00'}
                  </div>
                </div>
              </div>

              {/* Açıklama Önizleme */}
              {newProduct.description && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-[#1F1F1F] mb-2">Ürün Açıklaması:</h4>
                  <p className="text-sm text-[#666]">{newProduct.description}</p>
                </div>
              )}

              {/* Yüklenen Görseller Önizleme */}
              {newProduct.imagePreviews.length > 1 && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-[#1F1F1F] mb-3">Tüm Görseller ({newProduct.imagePreviews.length}):</h4>
                  <div className="grid grid-cols-4 gap-2">
                    {newProduct.imagePreviews.map((preview, index) => (
                      <img 
                        key={index}
                        src={preview} 
                        alt={`Görsel ${index + 1}`}
                        className="w-full aspect-square object-cover rounded border border-gray-200"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Yorum Sayısı Önizleme */}
              {newProduct.reviewCount > 0 && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-[#1F1F1F] mb-2">Müşteri Yorumları:</h4>
                  <p className="text-sm text-[#666]">
                    {newProduct.reviewCount} adet otomatik yorum eklenecek
                  </p>
                  <div className="mt-3 space-y-2">
                    {sampleReviews.slice(0, newProduct.reviewCount).map((review, index) => (
                      <div key={index} className="text-xs bg-white p-2 rounded border">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{review.user}</span>
                          <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                              <span key={i} className={`text-xs ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}>
                                ★
                              </span>
                            ))}
                          </div>
                        </div>
                        <p className="text-gray-600">{review.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    )
  }

  // Eğer bir mağaza seçildiyse detay sayfasını göster
  if (selectedStore) {
    const storeProducts = products[selectedStore.id] || []
    
    return (
      <div className="relative">
        
        {/* Mağaza Banner */}
        <div 
          className="rounded-xl p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] border border-gray-100 mb-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5" 
          style={{ 
            background: `linear-gradient(135deg, ${selectedStore.primaryColor}, ${selectedStore.secondaryColor})`
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Geri Dön Butonu */}
              <button
                onClick={handleBackToStores}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 sm:w-5 h-4 sm:h-5 text-white/70" />
              </button>
              
              {/* Mağaza Logo */}
              <div className="w-12 sm:w-14 md:w-16 h-12 sm:h-14 md:h-16 rounded-full flex items-center justify-center border border-white/30 overflow-hidden bg-white/20 backdrop-blur-sm">
                <img 
                  src={selectedStore.logo} 
                  alt={selectedStore.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Mağaza Bilgileri */}
              <div>
                <h2 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold" style={{ color: selectedStore.textColor || '#FFFFFF' }}>{selectedStore.name}</h2>
                <p className="text-xs sm:text-sm md:text-base" style={{ color: `${selectedStore.textColor || '#FFFFFF'}80` }}>{selectedStore.platform} Platform</p>
              </div>
            </div>

            {/* Durum */}
            <div className={`px-2 sm:px-3 md:px-4 py-1 sm:py-1.5 md:py-2 rounded-full text-xs sm:text-sm font-medium ${
              selectedStore.status === 'active' 
                ? 'bg-white/20 backdrop-blur-sm' 
                : 'bg-white/10 backdrop-blur-sm'
            }`} style={{ color: selectedStore.textColor || '#FFFFFF' }}>
              <span className="hidden sm:inline">{selectedStore.status === 'active' ? 'Aktif Çalışıyor' : 'Aktif Çalışmıyor'}</span>
              <span className="sm:hidden">{selectedStore.status === 'active' ? 'Aktif' : 'Pasif'}</span>
            </div>
          </div>
        </div>

        {/* Ürün Kartları Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20">
          {storeProducts.map((product, index) => (
            <div
              key={product.id}
              className={`bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 cursor-pointer aspect-[3/4] relative ${getCardAnimation(index)}`}
              style={{
                animationDelay: getAnimationDelay(index)
              }}
            >
              {/* 3 Nokta Dropdown */}
              <div className="absolute top-2 right-2 z-10">
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation() // Kartın onClick'ini engelle
                      setOpenProductDropdown(openProductDropdown === product.id ? null : product.id)
                    }}
                    className="p-1 rounded-full hover:bg-gray-100 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <MoreHorizontal className="w-4 h-4 text-gray-600" />
                  </button>

                  {/* Dropdown Menu */}
                  {openProductDropdown === product.id && (
                    <div
                      ref={productDropdownRef}
                      className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[120px] overflow-hidden"
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEditProduct(product)
                        }}
                        className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        <span>Düzenle</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteProduct(product)
                        }}
                        className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                        <span>Sil</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Ürün Görseli */}
              <div
                className="mb-2 sm:mb-3"
                onClick={() => handleProductClick(product)}
              >
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full aspect-[3/4] object-cover rounded-md sm:rounded-lg border border-gray-200"
                />
              </div>

              {/* Ürün Bilgileri */}
              <div
                className="text-center flex-1 flex flex-col justify-between"
                onClick={() => handleProductClick(product)}
              >
                <div>
                  <h3 className="text-xs sm:text-sm font-bold text-[#1F1F1F] mb-1">{product.name}</h3>
                  <p className="text-xs text-[#666] mb-1 sm:mb-2">{product.category}</p>
                </div>
                <div
                  className="text-sm sm:text-base lg:text-lg font-bold"
                  style={{ color: selectedStore.primaryColor }}
                >
                  {product.price}
                </div>
              </div>
            </div>
          ))}
          
          {/* Yeni Ürün Ekle Kartı */}
          <div 
            onClick={handleAddProductClick}
            className={`bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:scale-105 group border-2 border-dashed cursor-pointer transition-all duration-300 aspect-[3/4] ${getCardAnimation(storeProducts.length)}`}
            style={{ 
              animationDelay: getAnimationDelay(storeProducts.length),
              borderColor: `${selectedStore.primaryColor}30`,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = `${selectedStore.primaryColor}50`;
              e.currentTarget.style.boxShadow = `0px 12px 32px ${selectedStore.primaryColor}12`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = `${selectedStore.primaryColor}30`;
              e.currentTarget.style.boxShadow = '0px 4px 12px rgba(0,0,0,0.05)';
            }}
          >
            {/* Görsel Alan - Diğer kartlarla aynı oran */}
            <div 
              className="mb-2 sm:mb-3 flex items-center justify-center aspect-[3/4] border-2 border-dashed rounded-md sm:rounded-lg"
              style={{ borderColor: `${selectedStore.primaryColor}20` }}
            >
              <div 
                className="w-12 sm:w-14 lg:w-16 h-12 sm:h-14 lg:h-16 rounded-md sm:rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform border"
                style={{
                  background: `linear-gradient(to bottom right, ${selectedStore.primaryColor}10, ${selectedStore.secondaryColor}10)`,
                  borderColor: `${selectedStore.primaryColor}20`
                }}
              >
                <Plus 
                  className="w-6 sm:w-7 lg:w-8 h-6 sm:h-7 lg:h-8" 
                  style={{ color: selectedStore.primaryColor }}
                />
              </div>
            </div>

            {/* Ürün Bilgileri - Diğer kartlarla aynı düzen */}
            <div className="text-center flex-1 flex flex-col justify-between">
              <div>
                <h3 
                  className="text-xs sm:text-sm font-bold mb-0.5 sm:mb-1"
                  style={{ color: selectedStore.primaryColor }}
                >
                  <span className="hidden sm:inline">Yeni Ürün Ekle</span>
                  <span className="sm:hidden">Yeni Ürün</span>
                </h3>
                <p className="text-xs text-[#666] mb-1 sm:mb-2">
                  <span className="hidden sm:inline">Ürün eklemek için tıklayın</span>
                  <span className="sm:hidden">Eklemek için tıklayın</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Product Delete Confirmation Card - Sağ Alt Köşe */}
        {showProductDeleteCard && productToDelete && (
          <div className={`fixed bottom-6 right-6 bg-white rounded-2xl shadow-2xl border border-gray-200 p-6 max-w-sm w-full sm:w-auto z-50 transform transition-all duration-300 ease-out ${
            isProductCardClosing ? 'animate-slide-to-right' : 'animate-slide-from-right'
          }`}>
            <div className="flex items-start space-x-4">
              {/* Icon */}
              <div className="flex-shrink-0">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{
                    background: `linear-gradient(135deg, #FEF2F2, #FECACA)`
                  }}
                >
                  <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  Ürün Sil
                </h4>
                <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                  <span className="font-medium text-gray-900">{productToDelete.name}</span> ürününü silmek istediğinize emin misiniz?
                </p>

                {/* Buttons */}
                <div className="flex space-x-2">
                  <button
                    onClick={cancelDeleteProduct}
                    className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    İptal
                  </button>
                  <button
                    onClick={confirmDeleteProduct}
                    className="flex-1 px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Sil
                  </button>
                </div>
              </div>

              {/* Close Button */}
              <button
                onClick={cancelDeleteProduct}
                className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                <svg className="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        )}


      {/* Floating ChatboxElements - Birebir Aynı Chatbox (Küçük Boyut) */}
      {isClient && activeChatbox && (
        <div className="fixed bottom-4 right-8 z-1">
          <div style={{transform: 'scale(0.7)', transformOrigin: 'bottom right'}}>
            <ChatboxElements
              chatboxTitle={activeChatbox.name}
              initialMessage="Hello! It's Orbina here!"
              colors={{
                primary: activeChatbox.colors?.primary,
                aiMessage: activeChatbox.colors?.aiMessage,
                userMessage: activeChatbox.colors?.userMessage,
                borderColor: activeChatbox.colors?.borderColor,
                aiTextColor: activeChatbox.colors?.aiTextColor,
                userTextColor: activeChatbox.colors?.userTextColor,
                buttonPrimary: activeChatbox.colors?.buttonPrimary,
                buttonBorderColor: activeChatbox.colors?.buttonBorderColor,
                buttonIcon: activeChatbox.colors?.buttonIcon
              }}
              isVisible={isChatboxOpen}
              onToggle={() => setIsChatboxOpen(!isChatboxOpen)}
              panelZIndex={1}
              buttonZIndex={50}
              className=""
              style={{}}
            />
          </div>
        </div>
      )}

      </div>
    )
  }

  return (
    <div className="relative">
      
      {/* Mağaza Kartları Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mx-3 sm:mx-6 lg:mx-12 xl:mx-20 mt-3 sm:mt-4 lg:mt-5">
        {storeList.map((store, index) => (
          <div 
            key={store.id}
            onClick={() => handleStoreClick(store)}
            className={`rounded-lg sm:rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 cursor-pointer ${getCardAnimation(index)}`}
            style={{ 
              background: `linear-gradient(135deg, ${store.primaryColor}, ${store.secondaryColor})`,
              animationDelay: getAnimationDelay(index),
              height: '160px'
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-2 sm:mb-3 lg:mb-4">
              <div className="flex items-center space-x-1 sm:space-x-1.5">
                <div className={`w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full ${store.status === 'active' ? 'bg-white' : 'bg-white/50'}`}></div>
                {index === 0 && (
                  <div className="bg-white/20 backdrop-blur-sm px-1 sm:px-1.5 py-0.5 rounded-full">
                    <span className="text-xs font-bold text-white hidden sm:inline">ANA TEMA</span>
                    <span className="text-xs font-bold text-white sm:hidden">ANA</span>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-0.5 sm:space-x-1">
                {index !== 0 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation() // Kartın onClick'ini engelle
                      moveStoreToFirst(store.id)
                    }}
                    className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-0.5 sm:p-1 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                    title="Ana tema yap"
                  >
                    <Star className="w-2.5 sm:w-3 h-2.5 sm:h-3 text-white" />
                  </button>
                )}
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation() // Kartın onClick'ini engelle
                      setOpenStoreDropdown(openStoreDropdown === store.id ? null : store.id)
                    }}
                    className="p-1 rounded-full hover:bg-white/20 transition-colors"
                  >
                    <MoreHorizontal className="w-3 sm:w-4 h-3 sm:h-4 text-white/70 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>

                  {/* Dropdown Menu */}
                  {openStoreDropdown === store.id && (
                    <div
                      ref={storeDropdownRef}
                      className="absolute right-0 top-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[140px] overflow-hidden"
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setOpenStoreDropdown(null)
                          handleEditStore(store)
                        }}
                        className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        <span>Düzenle</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteStore(store)
                        }}
                        className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                        <span>Sil</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Mağaza Bilgileri - Sol Logo, Sağ Bilgiler */}
            <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
              {/* Mağaza Logo */}
              <div className="w-14 sm:w-16 lg:w-18 h-14 sm:h-16 lg:h-18 rounded-full flex items-center justify-center border border-white/30 flex-shrink-0 overflow-hidden bg-white/20 backdrop-blur-sm">
                <img 
                  src={store.logo} 
                  alt={store.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Mağaza Bilgileri */}
              <div className="flex-1 min-w-0">
                <h3 className="text-xs sm:text-sm lg:text-base font-bold mb-0.5 sm:mb-1 truncate" style={{ color: store.textColor || '#FFFFFF' }}>{store.name}</h3>
                <p className="text-xs sm:text-xs mb-1 sm:mb-1.5 lg:mb-2 truncate" style={{ color: `${store.textColor || '#FFFFFF'}80` }}>{store.platform} Platform</p>
                <div className={`inline-flex px-1.5 sm:px-2 py-0.5 rounded-full text-xs font-medium ${
                  store.status === 'active' 
                    ? 'bg-white/20 backdrop-blur-sm' 
                    : 'bg-white/10 backdrop-blur-sm'
                }`} style={{ color: store.textColor || '#FFFFFF' }}>
                  <span className="hidden sm:inline">{store.status === 'active' ? 'Aktif Çalışıyor' : 'Aktif Çalışmıyor'}</span>
                  <span className="sm:hidden">{store.status === 'active' ? 'Aktif' : 'Pasif'}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Yeni Mağaza Ekle Kartı */}
        <div 
          onClick={handleAddStoreClick}
          className={`bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 lg:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:scale-105 group border-2 border-dashed cursor-pointer transition-all duration-300 ${getCardAnimation(storeList.length)}`}
          style={{ 
            animationDelay: getAnimationDelay(storeList.length),
            height: '160px',
            borderColor: `${themeColors.primary}30`,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = `${themeColors.primary}50`;
            e.currentTarget.style.boxShadow = `0px 12px 32px ${themeColors.primary}12`;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = `${themeColors.primary}30`;
            e.currentTarget.style.boxShadow = '0px 4px 12px rgba(0,0,0,0.05)';
          }}
        >
          {/* İçerik */}
          <div className="flex flex-col items-center justify-center h-full text-center">
            {/* Plus İkonu */}
            <div 
              className="w-10 sm:w-12 lg:w-14 h-10 sm:h-12 lg:h-14 rounded-full flex items-center justify-center mb-2 sm:mb-3 lg:mb-4 group-hover:scale-110 transition-transform"
              style={{
                background: `linear-gradient(to bottom right, ${themeColors.primary}10, ${themeColors.secondary}10)`,
                borderColor: `${themeColors.primary}20`,
                border: '1px solid'
              }}
            >
              <Plus 
                className="w-5 sm:w-6 lg:w-7 h-5 sm:h-6 lg:h-7" 
                style={{ color: themeColors.primary }}
              />
            </div>

            {/* Metin */}
            <div>
              <h3 
                className="text-xs sm:text-sm lg:text-base font-bold mb-0.5 sm:mb-1"
                style={{ color: themeColors.primary }}
              >
                <span className="hidden sm:inline">Yeni Mağaza Ekle</span>
                <span className="sm:hidden">Yeni Mağaza</span>
              </h3>
              <p className="text-xs sm:text-xs text-[#666]">
                <span className="hidden sm:inline">Mağaza oluşturmak için tıklayın</span>
                <span className="sm:hidden">Eklemek için tıklayın</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Card - Sağ Alt Köşe */}
      {showDeleteCard && storeToDelete && (
        <div className={`fixed bottom-6 right-6 bg-white rounded-2xl shadow-2xl border border-gray-200 p-6 max-w-sm w-full sm:w-auto z-50 transform transition-all duration-300 ease-out ${
          isCardClosing ? 'animate-slide-to-right' : 'animate-slide-from-right'
        }`}>
          <div className="flex items-start space-x-4">
            {/* Icon */}
            <div className="flex-shrink-0">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center"
                style={{
                  background: `linear-gradient(135deg, #FEF2F2, #FECACA)`
                }}
              >
                <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-semibold text-gray-900 mb-1">
                Mağaza Sil
              </h4>
              <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                <span className="font-medium text-gray-900">{storeToDelete.name}</span> mağazasını silmek istediğinize emin misiniz?
              </p>

              {/* Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={cancelDeleteStore}
                  className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  İptal
                </button>
                <button
                  onClick={confirmDeleteStore}
                  className="flex-1 px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Sil
                </button>
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={cancelDeleteStore}
              className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
            >
              <svg className="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      )}


    </div>
  )
}