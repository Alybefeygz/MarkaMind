// API Configuration and Helper Functions

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Get authorization token from localStorage
 */
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token')
  }
  return null
}

/**
 * Generic API fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An error occurred'
    }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

/**
 * Upload file with multipart/form-data
 */
async function apiUpload<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = getAuthToken()

  const headers: HeadersInit = {}

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Upload failed'
    }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// ============================================================================
// Product API Functions
// ============================================================================

export interface CreateProductDTO {
  store_id: string
  name: string
  slug: string
  description: string
  price: number
  category: string
  initial_review_count: number
  status?: 'draft' | 'active' | 'archived'
  featured?: boolean
  stock_quantity?: number
}

export interface ProductResponse {
  id: string
  store_id: string
  name: string
  slug: string
  description: string
  price: string
  category: string
  status: string
  featured: boolean
  stock_quantity: number
  review_count: number
  average_rating: string
  created_at: string
  updated_at: string
}

export interface ProductListItem {
  id: string
  store_id: string
  name: string
  slug: string
  description: string | null
  price: string
  compare_at_price: string | null
  category: string
  status: string
  featured: boolean
  stock_quantity: number
  average_rating: string
  review_count: number
  sales_count: number
  created_at: string
}

export interface ProductsListResponse {
  items: ProductListItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ProductImageResponse {
  id: string
  product_id: string
  image_url: string
  alt_text: string | null
  display_order: number
  is_primary: boolean
  created_at: string
  updated_at: string
}

/**
 * Create a new product
 */
export async function createProduct(
  productData: CreateProductDTO
): Promise<ProductResponse> {
  return apiFetch<ProductResponse>('/products/', {
    method: 'POST',
    body: JSON.stringify(productData),
  })
}

/**
 * Get products by store ID
 */
export async function getStoreProducts(
  storeId: string,
  page: number = 1,
  size: number = 100
): Promise<ProductsListResponse> {
  return apiFetch<ProductsListResponse>(
    `/products/?store_id=${storeId}&page=${page}&size=${size}`
  )
}

/**
 * Get product images
 */
export async function getProductImages(
  productId: string
): Promise<ProductImageResponse[]> {
  return apiFetch<ProductImageResponse[]>(`/products/${productId}/images`)
}

/**
 * Upload single product image
 */
export async function uploadProductImage(
  productId: string,
  file: File,
  displayOrder: number = 0,
  isPrimary: boolean = false
): Promise<ProductImageResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('display_order', displayOrder.toString())
  formData.append('is_primary', isPrimary.toString())

  return apiUpload<ProductImageResponse>(`/products/${productId}/images`, formData)
}

/**
 * Upload multiple product images
 */
export async function uploadProductImages(
  productId: string,
  files: File[]
): Promise<{ success: boolean; uploaded_count: number; images: ProductImageResponse[] }> {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })

  return apiUpload(`/products/${productId}/images/batch`, formData)
}

/**
 * Generate slug from product name
 */
export function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .trim()
    // Turkish characters to English
    .replace(/ğ/g, 'g')
    .replace(/ü/g, 'u')
    .replace(/ş/g, 's')
    .replace(/ı/g, 'i')
    .replace(/ö/g, 'o')
    .replace(/ç/g, 'c')
    // Remove special characters except spaces and hyphens
    .replace(/[^\w\s-]/g, '')
    // Replace spaces with hyphens
    .replace(/\s+/g, '-')
    // Remove consecutive hyphens
    .replace(/-+/g, '-')
    // Remove leading/trailing hyphens
    .replace(/^-+|-+$/g, '')
}

// ============================================================================
// Store API Functions
// ============================================================================

export interface Store {
  id: string
  brand_id: string
  name: string
  platform: string
  logo?: string | null  // Backend'de 'logo' olarak geliyor
  description?: string | null  // Mağaza açıklaması
  status: string
  primary_color: string
  secondary_color: string
  text_color: string
  created_at: string
  updated_at: string
}

export interface StoresListResponse {
  items: Store[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * Get user stores
 * Backend maksimum 100 item döndürüyor, tüm mağazaları almak için sayfalama yapıyoruz
 */
export async function getUserStores(): Promise<Store[]> {
  const allStores: Store[] = []
  let page = 1
  const size = 100 // Backend'in maksimum limiti
  let hasMore = true

  while (hasMore) {
    const response = await apiFetch<StoresListResponse>(`/stores/?page=${page}&size=${size}`)
    allStores.push(...response.items)

    // Eğer dönen item sayısı size'dan azsa veya toplam sayfa sayısına ulaştıysak dur
    if (response.items.length < size || page >= response.pages) {
      hasMore = false
    } else {
      page++
    }
  }

  return allStores
}

/**
 * Get store by ID
 */
export async function getStoreById(storeId: string): Promise<Store> {
  return apiFetch<Store>(`/stores/${storeId}`)
}

// ============================================================================
// Review API Functions
// ============================================================================

export interface ProductReview {
  id: string
  product_id: string
  user_id: string | null
  reviewer_name: string
  reviewer_email: string | null
  rating: number
  title: string | null
  comment: string
  verified_purchase: boolean
  status: string
  helpful_count: number
  created_at: string
  updated_at: string
}

export interface ReviewsResponse {
  items: ProductReview[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * Get product reviews
 */
export async function getProductReviews(
  productId: string,
  page: number = 1,
  size: number = 10,
  statusFilter: string = 'approved'
): Promise<ReviewsResponse> {
  return apiFetch<ReviewsResponse>(
    `/products/${productId}/reviews?page=${page}&size=${size}&status_filter=${statusFilter}`
  )
}

// ============================================================================
// Chatbox API Functions
// ============================================================================

export interface ChatboxCreate {
  brand_id?: string | null  // Opsiyonel
  store_id?: string | null  // Opsiyonel
  name: string  // Zorunlu
  chatbox_title: string  // Zorunlu
  initial_message: string  // Zorunlu
  placeholder_text?: string  // Opsiyonel
  primary_color: string  // Zorunlu
  ai_message_color: string  // Zorunlu
  user_message_color: string  // Zorunlu
  ai_text_color: string  // Zorunlu
  user_text_color: string  // Zorunlu
  button_primary_color: string  // Zorunlu
  button_border_color: string  // Zorunlu
  button_icon_color: string  // Zorunlu
  avatar_url?: string | null  // Opsiyonel
  animation_style?: string  // Opsiyonel
  language?: string  // Opsiyonel
  status?: string  // Opsiyonel
}

export interface ChatboxResponse {
  id: string
  brand_id: string
  name: string
  chatbox_title: string
  initial_message: string
  placeholder_text: string
  primary_color: string
  ai_message_color: string
  user_message_color: string
  ai_text_color: string
  user_text_color: string
  button_primary_color: string
  button_border_color: string
  button_icon_color: string
  avatar_url: string | null
  animation_style: string
  language: string
  status: string
  script_token: string
  created_at: string
  updated_at: string
}

/**
 * Create a new chatbox
 */
export async function createChatbox(chatbox: ChatboxCreate): Promise<ChatboxResponse> {
  return apiFetch<ChatboxResponse>('/chatboxes/', {
    method: 'POST',
    body: JSON.stringify(chatbox),
  })
}

/**
 * Get user's chatboxes
 */
export interface ChatboxListResponse {
  items: ChatboxResponse[]
  total: number
  page: number
  size: number
  pages: number
}

export async function getUserChatboxes(
  page: number = 1,
  size: number = 100,
  brandId?: string,
  statusFilter?: string
): Promise<ChatboxListResponse> {
  let url = `/chatboxes/?page=${page}&size=${size}`
  if (brandId) url += `&brand_id=${brandId}`
  if (statusFilter) url += `&status_filter=${statusFilter}`

  return apiFetch<ChatboxListResponse>(url)
}

/**
 * Delete a chatbox
 */
export async function deleteChatbox(chatboxId: string): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(`/chatboxes/${chatboxId}`, {
    method: 'DELETE',
  })
}

/**
 * Chatbox Integrations (Stores & Products)
 */
export interface ChatboxStoreIntegration {
  store_id: string
  show_on_homepage: boolean
  show_on_products: boolean
  position: string
  is_active: boolean
}

export interface ChatboxProductIntegration {
  product_id: string
  show_on_product_page: boolean
  is_active: boolean
}

export interface ChatboxIntegrationsUpdate {
  stores: ChatboxStoreIntegration[]
  products: ChatboxProductIntegration[]
  stores_only: string[]
}

export interface ChatboxIntegrationsResponse {
  stores_added: number
  products_added: number
  stores_removed: number
  products_removed: number
  message: string
}

/**
 * Update chatbox integrations (stores and products)
 */
export async function updateChatboxIntegrations(
  chatboxId: string,
  integrations: ChatboxIntegrationsUpdate
): Promise<ChatboxIntegrationsResponse> {
  return apiFetch<ChatboxIntegrationsResponse>(`/chatboxes/${chatboxId}/integrations`, {
    method: 'PUT',
    body: JSON.stringify(integrations),
  })
}

/**
 * Knowledge Source (PDF) Types and Functions
 */
export interface KnowledgeSourceResponse {
  id: string
  chatbot_id: string
  source_type: string
  source_name: string
  storage_path: string
  file_size: number | null
  status: string
  token_count: number
  error_message: string | null
  is_active: boolean
  content: string | null
  created_at: string
  updated_at: string
}

/**
 * Get chatbox knowledge sources (PDFs)
 */
export async function getChatboxKnowledgeSources(
  chatboxId: string
): Promise<KnowledgeSourceResponse[]> {
  return apiFetch<KnowledgeSourceResponse[]>(`/chatboxes/${chatboxId}/knowledge-sources`)
}

/**
 * Upload knowledge source (PDF) to chatbox
 */
export async function uploadKnowledgeSource(
  chatboxId: string,
  file: File
): Promise<KnowledgeSourceResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return apiUpload<KnowledgeSourceResponse>(`/chatboxes/${chatboxId}/knowledge-sources`, formData)
}

/**
 * Upload temporary knowledge source (PDF) without chatbox assignment
 * Used during chatbox creation flow
 */
export async function uploadTempKnowledgeSource(
  file: File
): Promise<KnowledgeSourceResponse> {
  console.log('🚀 uploadTempKnowledgeSource called in api.ts')
  const formData = new FormData()
  formData.append('file', file)

  return apiUpload<KnowledgeSourceResponse>(`/chatboxes/temp-knowledge-sources`, formData)
}

/**
 * Assign pending PDFs (chatbot_id = NULL) to a chatbox
 * Used after chatbox creation to link uploaded PDFs
 */
export async function assignPendingPDFsToChatbox(
  chatboxId: string
): Promise<{ success: boolean; message: string }> {
  return apiFetch(`/chatboxes/${chatboxId}/assign-pending-pdfs`, {
    method: 'POST',
  })
}

/**
 * Toggle knowledge source active/inactive status
 */
export async function toggleKnowledgeSourceStatus(
  chatboxId: string,
  sourceId: string
): Promise<KnowledgeSourceResponse> {
  return apiFetch<KnowledgeSourceResponse>(
    `/chatboxes/${chatboxId}/knowledge-sources/${sourceId}/toggle`,
    {
      method: 'PATCH',
    }
  )
}

/**
 * Delete knowledge source (PDF)
 */
export async function deleteKnowledgeSource(
  chatboxId: string,
  sourceId: string
): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(
    `/chatboxes/${chatboxId}/knowledge-sources/${sourceId}`,
    {
      method: 'DELETE',
    }
  )
}

/**
 * Create edited PDF from modified content
 */
export async function createEditedPDF(
  chatboxId: string,
  data: {
    original_source_id: string
    edited_content: string
  }
): Promise<KnowledgeSourceResponse> {
  return apiFetch<KnowledgeSourceResponse>(
    `/chatboxes/${chatboxId}/knowledge-sources/create-edited`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  )
}

// ============================================================================
// Chatbox Store & Product Integration API Functions
// ============================================================================

export interface ChatboxStoreRelation {
  id: string
  store: {
    id: string
    name: string
    slug: string
    logo?: string
  }
  show_on_homepage: boolean
  show_on_products: boolean
  position: string
  is_active: boolean
  created_at: string
}

export interface ChatboxProductRelation {
  id: string
  product: {
    id: string
    name: string
    slug: string
    price: string
    category: string
    store_name: string
  }
  show_on_product_page: boolean
  is_active: boolean
  created_at: string
}

/**
 * Get chatbox store integrations
 */
export async function getChatboxStores(chatboxId: string): Promise<ChatboxStoreRelation[]> {
  return apiFetch<ChatboxStoreRelation[]>(`/chatboxes/${chatboxId}/stores`)
}

/**
 * Get chatbox product integrations
 */
export async function getChatboxProducts(chatboxId: string): Promise<ChatboxProductRelation[]> {
  return apiFetch<ChatboxProductRelation[]>(`/chatboxes/${chatboxId}/products`)
}

// ============================================================================
// Brand API Functions
// ============================================================================

export interface BrandCreate {
  name: string
  description?: string | null
  logo_url?: string | null
  theme_color?: string
}

export interface BrandResponse {
  id: string
  user_id: string
  name: string
  slug: string
  description: string | null
  logo_url: string | null
  theme_color: string
  is_active: boolean
  created_at: string
}

export interface BrandListItem {
  id: string
  name: string
  slug: string
  description: string | null
  logo_url: string | null
  theme_color: string
  is_active: boolean
}

export interface BrandsListResponse {
  items: BrandListItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface BrandUpdate {
  name?: string
  description?: string | null
  logo_url?: string | null
  theme_color?: string
  is_active?: boolean
}

/**
 * Create a new brand
 */
export async function createBrand(brand: BrandCreate): Promise<BrandResponse> {
  return apiFetch<BrandResponse>('/brands/', {
    method: 'POST',
    body: JSON.stringify(brand),
  })
}

/**
 * Get user's brands
 */
export async function getUserBrands(
  page: number = 1,
  size: number = 100
): Promise<BrandsListResponse> {
  return apiFetch<BrandsListResponse>(`/brands/?page=${page}&size=${size}`)
}

/**
 * Get brand by ID
 */
export async function getBrandById(brandId: string): Promise<BrandResponse> {
  return apiFetch<BrandResponse>(`/brands/${brandId}`)
}

/**
 * Update brand
 */
export async function updateBrand(
  brandId: string,
  brandUpdate: BrandUpdate
): Promise<BrandResponse> {
  return apiFetch<BrandResponse>(`/brands/${brandId}`, {
    method: 'PUT',
    body: JSON.stringify(brandUpdate),
  })
}

/**
 * Delete brand
 */
export async function deleteBrand(brandId: string): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(`/brands/${brandId}`, {
    method: 'DELETE',
  })
}

/**
 * Upload brand logo
 */
export async function uploadBrandLogo(
  brandId: string,
  file: File
): Promise<{ success: boolean; logo_url: string; message: string }> {
  const formData = new FormData()
  formData.append('file', file)

  return apiUpload(`/brands/${brandId}/logo/upload`, formData)
}

export default {
  createProduct,
  getStoreProducts,
  getProductImages,
  uploadProductImage,
  uploadProductImages,
  generateSlug,
  getUserStores,
  getStoreById,
  getProductReviews,
  createChatbox,
  getUserChatboxes,
  getChatboxKnowledgeSources,
  uploadKnowledgeSource,
  toggleKnowledgeSourceStatus,
  deleteKnowledgeSource,
  createBrand,
  getUserBrands,
  getBrandById,
  updateBrand,
  deleteBrand,
  uploadBrandLogo,
}

/**
 * Get chatbox configuration for a specific store (public endpoint)
 * Used in virtual store pages to display the integrated chatbox
 */
export async function getChatboxByStore(storeId: string): Promise<ChatboxResponse> {
  return apiFetch<ChatboxResponse>(`/stores/${storeId}/chatbox`)
}

/**
 * Get chatbox configuration for a specific product (public endpoint)
 * Used in product pages to display the integrated chatbox
 */
export async function getChatboxByProduct(productId: string): Promise<ChatboxResponse> {
  return apiFetch<ChatboxResponse>(`/products/${productId}/chatbox`)
}

/**
 * Get all chatbox integrations for the current user
 * Used to check for conflicts when selecting stores/products
 */
export async function getAllChatboxIntegrations(): Promise<Record<string, {
  chatbox_name: string
  stores: string[]
  products: string[]
  stores_only: string[]
}>> {
  return apiFetch<Record<string, {
    chatbox_name: string
    stores: string[]
    products: string[]
    stores_only: string[]
  }>>('/chatboxes/integrations/all')
}

// ============================================================================
// Chat Message API Functions
// ============================================================================

export interface SendChatMessageRequest {
  chatbot_id: string
  message: string
  session_id: string
  user_id?: string
  metadata?: Record<string, any>
}

export interface SendChatMessageResponse {
  success: boolean
  user_message_id: string
  bot_message_id: string
  bot_response: string
  processing_time_ms: number
  total_tokens?: number
  source_chunks?: string[]
  source_entry_id?: string
  session_id: string
}

export interface ChatMessage {
  id: string
  chatbot_id: string
  conversation_id?: string
  session_id: string
  user_id?: string
  message_direction: 'incoming' | 'outgoing'
  message_type: string
  content: string
  formatted_content?: Record<string, any>
  ai_model?: string
  prompt_tokens?: number
  completion_tokens?: number
  total_tokens?: number
  processing_time_ms?: number
  status: string
  error_message?: string
  source_chunks?: string[]
  source_entry_id?: string
  sentiment?: string
  was_helpful?: boolean
  user_feedback?: string
  feedback_rating?: number
  parent_message_id?: string
  thread_id?: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
  read_at?: string
}

export interface ConversationHistoryResponse {
  session_id: string
  chatbot_id: string
  messages: ChatMessage[]
  total_messages: number
  stats: {
    total_user_messages: number
    total_bot_messages: number
    avg_response_time_ms: number
    satisfaction_rate: number
  }
}

export interface UpdateFeedbackRequest {
  was_helpful?: boolean
  sentiment?: 'positive' | 'negative' | 'neutral'
  user_feedback?: string
  feedback_rating?: number
}

/**
 * Send a chat message and get AI response
 *
 * @param data - Message data including chatbot_id, message, session_id
 * @returns Bot response with message IDs and metadata
 */
export async function sendChatMessage(
  data: SendChatMessageRequest
): Promise<SendChatMessageResponse> {
  return apiFetch<SendChatMessageResponse>('/chat/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
}

/**
 * Get conversation history for a specific session
 *
 * @param sessionId - Session ID
 * @param chatbotId - Chatbot ID
 * @param limit - Maximum number of messages (default: 50)
 * @returns Conversation history with messages and stats
 */
export async function getChatHistory(
  sessionId: string,
  chatbotId: string,
  limit: number = 50
): Promise<ConversationHistoryResponse> {
  return apiFetch<ConversationHistoryResponse>(
    `/chat/history/${sessionId}?chatbot_id=${chatbotId}&limit=${limit}`
  )
}

/**
 * Update message feedback (helpful/not helpful, rating, comment)
 *
 * @param messageId - Message ID
 * @param feedback - Feedback data
 * @returns Success status
 */
export async function updateMessageFeedback(
  messageId: string,
  feedback: UpdateFeedbackRequest
): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(
    `/chat/feedback/${messageId}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    }
  )
}

/**
 * Get a single message by ID
 *
 * @param messageId - Message ID
 * @returns Message details
 */
export async function getChatMessage(messageId: string): Promise<ChatMessage> {
  return apiFetch<ChatMessage>(`/chat/message/${messageId}`)
}

/**
 * Delete all messages in a session
 *
 * @param sessionId - Session ID
 * @param chatbotId - Chatbot ID
 * @returns Success status
 */
export async function deleteChatSession(
  sessionId: string,
  chatbotId: string
): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(
    `/chat/session/${sessionId}?chatbot_id=${chatbotId}`,
    {
      method: 'DELETE',
    }
  )
}
