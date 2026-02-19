const API_BASE = '/api/v1'

export const avatarApi = {
  async listAvatars() {
    const response = await fetch(`${API_BASE}/avatars/`)
    return response.json()
  },
  async createAvatar(formData) {
    const response = await fetch(`${API_BASE}/avatars/`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  }
}

export const videoApi = {
  async generateTextToVideo(formData) {
    const response = await fetch(`${API_BASE}/videos/text-to-video`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  },

  async generateAudioToVideo(formData) {
    const response = await fetch(`${API_BASE}/videos/audio-to-video`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  },

  async getJobStatus(jobId) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`)
    return response.json()
  },

  async downloadVideo(videoId) {
    window.open(`${API_BASE}/jobs/${videoId}/download`, '_blank')
  },
  async listJobs() {
    const response = await fetch(`${API_BASE}/jobs/`)
    return response.json()
  },
  async generateVideoToVideo(formData) {
    const response = await fetch(`${API_BASE}/videos/video-to-video`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  }
}
