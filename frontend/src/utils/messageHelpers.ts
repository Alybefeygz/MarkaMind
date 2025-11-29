/**
 * Message Helpers
 * Mesajlaşma kayıtları için yardımcı fonksiyonlar
 */

import { ChatMessage } from '@/lib/api'

/**
 * Mesaj tarihini Türkçe formatta döndürür
 * Örnek: "15 Ekim 2024 • 14:32"
 */
export function formatMessageDate(dateString: string): string {
  const date = new Date(dateString)

  const dateStr = date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })

  const timeStr = date.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })

  return `${dateStr} • ${timeStr}`
}

/**
 * Sadece saat bilgisini döndürür
 * Örnek: "14:32"
 */
export function formatMessageTime(dateString: string): string {
  const date = new Date(dateString)

  return date.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Session'ın ilk kullanıcı mesajını döndürür
 * Bot mesajlarını atlar, sadece kullanıcının ilk mesajını alır
 */
export function getFirstUserMessage(messages: ChatMessage[]): string {
  if (!messages || messages.length === 0) {
    return 'Mesaj bulunamadı'
  }

  const firstUserMessage = messages.find(
    msg => msg.message_direction === 'incoming'
  )

  return firstUserMessage?.content || 'Mesaj bulunamadı'
}

/**
 * Ziyaretçi ID'sini görüntülenebilir formata çevirir
 * Örnek: "MM00001" → "Ziyaretçi #MM00001"
 */
export function getSessionDisplayName(ziyaretciId?: string): string {
  if (!ziyaretciId) {
    return 'Anonim Ziyaretçi'
  }

  return `Ziyaretçi #${ziyaretciId}`
}

/**
 * Mesaj sayısını formatlı string olarak döndürür
 * Örnek: 5 → "5 mesaj"
 */
export function formatMessageCount(count: number): string {
  return `${count} mesaj`
}

/**
 * Session'ın son aktivite zamanını göreceli olarak döndürür
 * Örnek: "2 saat önce", "Dün", "3 gün önce"
 */
export function getRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Az önce'
  if (diffMins < 60) return `${diffMins} dakika önce`
  if (diffHours < 24) return `${diffHours} saat önce`
  if (diffDays === 1) return 'Dün'
  if (diffDays < 7) return `${diffDays} gün önce`

  return formatMessageDate(dateString)
}
