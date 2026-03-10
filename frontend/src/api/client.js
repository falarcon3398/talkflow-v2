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
  },
  async updateAvatar(avatarId, name) {
    const formData = new FormData()
    formData.append('name', name)
    const response = await fetch(`${API_BASE}/avatars/${avatarId}`, {
      method: 'PUT',
      body: formData
    })
    return response.json()
  },
  async deleteAvatar(avatarId) {
    const response = await fetch(`${API_BASE}/avatars/${avatarId}`, {
      method: 'DELETE'
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
  },

  async deleteJob(jobId) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE'
    })
    return response.json()
  },
  async batchDeleteJobs(jobIds) {
    const response = await fetch(`${API_BASE}/jobs/batch-delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(jobIds)
    })
    return response.json()
  },
  async updateJob(jobId, data) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    return response.json()
  },
  async batchUpdateJobs(jobIds, data) {
    const response = await fetch(`${API_BASE}/jobs/batch-update`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ job_ids: jobIds, data })
    })
    return response.json()
  }
}

export const voiceApi = {
  async listVoices() {
    const response = await fetch(`${API_BASE}/voices/`)
    return response.json()
  },
  async createVoice(formData) {
    const response = await fetch(`${API_BASE}/voices/`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  },
  async updateVoice(voiceId, name) {
    const formData = new FormData()
    formData.append('name', name)
    const response = await fetch(`${API_BASE}/voices/${voiceId}`, {
      method: 'PATCH',
      body: formData
    })
    return response.json()
  },
  async deleteVoice(voiceId) {
    const response = await fetch(`${API_BASE}/voices/${voiceId}`, {
      method: 'DELETE'
    })
    return response.json()
  }
}
