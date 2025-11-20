'use client'

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { getUserStores, getStoreProducts, type Store, type ProductListItem } from '../lib/api'

interface InventoryContextType {
    stores: Store[]
    products: ProductListItem[]
    isLoadingStores: boolean
    isLoadingProducts: boolean
    lastUpdated: Date | null
    fetchStores: (force?: boolean) => Promise<void>
    fetchProducts: (force?: boolean) => Promise<void>
    refreshInventory: () => Promise<void>
}

const InventoryContext = createContext<InventoryContextType | undefined>(undefined)

export function InventoryProvider({ children }: { children: React.ReactNode }) {
    const [stores, setStores] = useState<Store[]>([])
    const [products, setProducts] = useState<ProductListItem[]>([])
    const [isLoadingStores, setIsLoadingStores] = useState(false)
    const [isLoadingProducts, setIsLoadingProducts] = useState(false)
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

    // Fetch durumunu takip etmek için ref'ler
    const isFetchingStoresRef = useRef(false)
    const isFetchingProductsRef = useRef(false)

    // Mağazaları çek
    const fetchStores = useCallback(async (force = false) => {
        // Eğer zaten fetch ediyorsa, tekrar etme
        if (isFetchingStoresRef.current) {
            console.log('⏭️ fetchStores zaten çalışıyor, atlanıyor')
            return
        }

        // Ref kullanarak cache kontrolü (state dependency olmadan)
        if (!force && stores.length > 0) {
            console.log('✅ Stores cache\'ten alındı:', stores.length, 'mağaza')
            return
        }

        isFetchingStoresRef.current = true
        setIsLoadingStores(true)
        try {
            console.log('🌐 Stores API çağrısı yapılıyor...')
            const fetchedStores = await getUserStores()
            setStores(fetchedStores)
            setLastUpdated(new Date())
            console.log('✅ Stores API\'den yüklendi:', fetchedStores.length, 'mağaza')
        } catch (error) {
            console.error('❌ Failed to fetch stores:', error)
        } finally {
            setIsLoadingStores(false)
            isFetchingStoresRef.current = false
        }
    }, [stores.length]) // ✅ stores.length dependency ama useCallback stabil kalıyor

    // Ürünleri çek (Mağazalar yüklü değilse önce onları çeker)
    const fetchProducts = useCallback(async (force = false) => {
        // Eğer zaten fetch ediyorsa, tekrar etme
        if (isFetchingProductsRef.current) {
            console.log('⏭️ fetchProducts zaten çalışıyor, atlanıyor')
            return
        }

        // Ref kullanarak cache kontrolü
        if (!force && products.length > 0) {
            console.log('✅ Products cache\'ten alındı:', products.length, 'ürün')
            return
        }

        isFetchingProductsRef.current = true
        setIsLoadingProducts(true)
        try {
            // Mağazalar henüz yüklenmediyse önce onları yükle
            let currentStores = stores
            if (currentStores.length === 0) {
                console.log('🔄 Önce stores yükleniyor...')
                setIsLoadingStores(true)
                try {
                    currentStores = await getUserStores()
                    setStores(currentStores)
                } finally {
                    setIsLoadingStores(false)
                }
            }

            if (currentStores.length === 0) {
                console.log('⚠️ Hiç mağaza yok, ürünler boş')
                setProducts([])
                setIsLoadingProducts(false)
                isFetchingProductsRef.current = false
                return
            }

            console.log('🌐 Products API çağrısı yapılıyor...')
            // Paralel olarak tüm mağazaların ürünlerini çek
            const productPromises = currentStores.map(store =>
                getStoreProducts(store.id, 1, 100).then(res => res.items)
            )

            const productsArrays = await Promise.all(productPromises)
            const allProducts = productsArrays.flat()

            setProducts(allProducts)
            setLastUpdated(new Date())
            console.log('✅ Products API\'den yüklendi:', allProducts.length, 'ürün')
        } catch (error) {
            console.error('❌ Failed to fetch products:', error)
        } finally {
            setIsLoadingProducts(false)
            isFetchingProductsRef.current = false
        }
    }, [stores, products.length]) // ✅ stores ve products.length dependency

    // Tüm envanteri yenile
    const refreshInventory = useCallback(async () => {
        await fetchStores(true)
        // fetchProducts zaten güncel stores state'ini kullanmak için kendi içinde logic barındırıyor
        // ancak burada state update'inin yansıması için beklemek gerekebilir.
        // Basitlik adına, fetchStores tamamlandıktan sonra products'ı da force ile çağırabiliriz.
        // Ancak fetchProducts içindeki "currentStores" logic'i, state update'i hemen yansımayacağı için
        // getUserStores'u tekrar çağırabilir.
        // Bu yüzden burada manuel olarak zincirleme yapalım.

        setIsLoadingProducts(true)
        try {
            const freshStores = await getUserStores()
            setStores(freshStores)

            const productPromises = freshStores.map(store =>
                getStoreProducts(store.id, 1, 100).then(res => res.items)
            )
            const productsArrays = await Promise.all(productPromises)
            const allProducts = productsArrays.flat()

            setProducts(allProducts)
            setLastUpdated(new Date())
        } catch (error) {
            console.error('Failed to refresh inventory:', error)
        } finally {
            setIsLoadingStores(false)
            setIsLoadingProducts(false)
        }
    }, [])

    return (
        <InventoryContext.Provider
            value={{
                stores,
                products,
                isLoadingStores,
                isLoadingProducts,
                lastUpdated,
                fetchStores,
                fetchProducts,
                refreshInventory
            }}
        >
            {children}
        </InventoryContext.Provider>
    )
}

export function useInventory() {
    const context = useContext(InventoryContext)
    if (context === undefined) {
        throw new Error('useInventory must be used within an InventoryProvider')
    }
    return context
}
