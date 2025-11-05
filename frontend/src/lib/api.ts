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
  logo_url?: string
  status: string
  primary_color: string
  secondary_color: string
  text_color: string
  created_at: string
  updated_at: string
}

/**
 * Get user stores
 */
export async function getUserStores(): Promise<Store[]> {
  return apiFetch<Store[]>('/stores/')
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
}
