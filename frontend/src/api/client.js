const API_BASE = '/api/v1';

export const videoApi = {
    async generateTextToVideo(formData) {
        const response = await fetch(`${API_BASE}/videos/text-to-video`, {
            method: 'POST',
            body: formData,
        });
        return response.json();
    },

    async generateAudioToVideo(formData) {
        const response = await fetch(`${API_BASE}/videos/audio-to-video`, {
            method: 'POST',
            body: formData,
        });
        return response.json();
    },

    async getJobStatus(jobId) {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`);
        return response.json();
    },

    async downloadVideo(videoId) {
        window.open(`${API_BASE}/jobs/${videoId}/download`, '_blank');
    }
};
