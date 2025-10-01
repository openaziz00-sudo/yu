const API_BASE_URL = 'http://localhost:5001/api'

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // المحادثات
  async getChats() {
    return this.request('/chats')
  }

  async createChat(title = 'محادثة جديدة') {
    return this.request('/chats', {
      method: 'POST',
      body: JSON.stringify({ title }),
    })
  }

  async getChat(chatId) {
    return this.request(`/chats/${chatId}`)
  }

  async deleteChat(chatId) {
    return this.request(`/chats/${chatId}`, {
      method: 'DELETE',
    })
  }

  // الرسائل
  async sendMessage(chatId, message, model = null) {
    return this.request(`/chats/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ 
        message,
        model 
      }),
    })
  }

  // النماذج
  async getModels() {
    return this.request('/models')
  }

  // فحص الحالة
  async healthCheck() {
    return this.request('/health')
  }
}

export default new ApiService()
