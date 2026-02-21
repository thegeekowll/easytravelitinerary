import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async getCurrentUser() {
    // Add timestamp to prevent browser caching of user data
    const response = await this.client.get('/auth/me', {
      params: { _t: new Date().getTime() }
    });
    return response.data;
  }

  async getItineraries(params?: { 
    page?: number; 
    limit?: number; 
    status_filter?: string; 
    search?: string; 
    departure_date_from?: string; 
    departure_date_to?: string; 
    created_at_from?: string;
    created_at_to?: string;
    creator_id?: string;
  }) {
    const response = await this.client.get('/itineraries', { params });
    return response.data;
  }

  async getItinerary(id: string) {
    const response = await this.client.get(`/itineraries/${id}`);
    return response.data;
  }

  async createItinerary(data: any) {
    const response = await this.client.post('/itineraries', data);
    return response.data;
  }

  async createItineraryFromBaseTour(data: any) {
    const response = await this.client.post('/itineraries/create-from-base', data);
    return response.data;
  }

  async createCustomItinerary(data: any) {
    const response = await this.client.post('/itineraries/create-custom', data);
    return response.data;
  }

  async updateItinerary(id: string, data: any) {
    const response = await this.client.patch(`/itineraries/${id}`, data);
    return response.data;
  }

  async addTraveler(itineraryId: string, data: any) {
    const response = await this.client.post(`/itineraries/${itineraryId}/travelers`, data);
    return response.data;
  }



  async updateTraveler(itineraryId: string, travelerId: string, data: any) {
    const response = await this.client.patch(`/itineraries/${itineraryId}/travelers/${travelerId}`, data);
    return response.data;
  }

  async deleteTraveler(itineraryId: string, travelerId: string) {
    const response = await this.client.delete(`/itineraries/${itineraryId}/travelers/${travelerId}`);
    return response.data;
  }

  async delete(url: string) {
    const response = await this.client.delete(url);
    return response.data;
  }

  // Admin User Management
  async getUsers(params?: any) {
    const response = await this.client.get('/users', { params });
    return response.data;
  }
  
  async getAgents() {
      // Helper to fetch just agents/admins for dropdowns
      // Assuming GET /users supports role filtering or we fetch all and filter client side if small list
      // For now, let's fetch all users, as the system scale suggests it's manageable.
      const response = await this.client.get('/users');
      return response.data; 
  }

  async createUser(data: any) {
    const response = await this.client.post('/users', data);
    return response.data;
  }

  async deleteUser(userId: string) {
    const response = await this.client.delete(`/users/${userId}`);
    return response.data;
  }

  async updateUser(userId: string, data: any) {
    const response = await this.client.patch(`/users/${userId}`, data);
    return response.data;
  }

  async getPermissions() {
    const response = await this.client.get('/permissions');
    return response.data;
  }

  async getUser(userId: string) {
    const response = await this.client.get(`/users/${userId}`);
    return response.data;
  }

  // Admin Tour Management
  async getBaseTours(params?: any) {
    const response = await this.client.get('/base-tours', { params });
    return response.data;
  }

  async getTourTypes() {
    const response = await this.client.get('/tour-types');
    return response.data;
  }

  async createTourType(data: any) {
    const response = await this.client.post('/tour-types', data);
    return response.data;
  }

  async createBaseTour(data: any) {
    const response = await this.client.post('/base-tours', data);
    return response.data;
  }

  async getBaseTour(id: string) {
    const response = await this.client.get(`/base-tours/${id}`);
    return response.data;
  }


  
  async updateBaseTourImage(imageId: string, data: any) {
    const response = await this.client.put(`/base-tours/images/${imageId}`, data);
    return response.data;
  }



  async updateBaseTour(id: string, data: any) {
    const response = await this.client.patch(`/base-tours/${id}`, data);
    return response.data;
  }

  // Admin Accommodation Management
  async getAccommodations(params?: any) {
    const response = await this.client.get('/accommodations', { params });
    return response.data;
  }

  async createAccommodation(data: any) {
    const response = await this.client.post('/accommodations', data);
    return response.data;
  }

  async getAccommodation(id: string) {
    const response = await this.client.get(`/accommodations/${id}`);
    return response.data;
  }

  async updateAccommodation(id: string, data: any) {
    const response = await this.client.patch(`/accommodations/${id}`, data);
    return response.data;
  }

  async deleteAccommodation(id: string) {
    const response = await this.client.delete(`/accommodations/${id}`);
    return response.data;
  }

  async getAccommodationTypes() {
    const response = await this.client.get('/accommodations/types');
    return response.data;
  }

  async createAccommodationType(data: { name: string; description?: string }) {
    const response = await this.client.post('/accommodations/types', data);
    return response.data;
  }

  async getAccommodationLevels() {
    const response = await this.client.get('/accommodation-levels');
    return response.data;
  }

  async createAccommodationLevel(data: { name: string; description?: string }) {
    const response = await this.client.post('/accommodation-levels', data);
    return response.data;
  }

  async deleteAccommodationLevel(id: string) {
    const response = await this.client.delete(`/accommodation-levels/${id}`);
    return response.data;
  }

  async uploadAccommodationImages(id: string, files: File[]) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    
    const response = await this.client.post(`/accommodations/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteAccommodationImage(imageId: string) {
    const response = await this.client.delete(`/accommodations/images/${imageId}`);
    return response.data;
  }

  // Admin Destinatinos Management
  async getDestinations(params?: any) {
    const response = await this.client.get('/destinations', { params });
    return response.data;
  }

  async createDestination(data: any) {
    const response = await this.client.post('/destinations', data);
    return response.data;
  }


  // Notifications
  async getNotifications(params?: { page?: number; limit?: number; is_read?: boolean; notification_type?: string; priority?: string }) {
    const response = await this.client.get('/notifications', { params });
    return response.data;
  }

  // Analytics
  async getAnalytics() {
      const response = await this.client.get('/analytics');
      return response.data;
  }

  async getUnreadCount() {
    const response = await this.client.get('/notifications/unread-count');
    return response.data;
  }

  async markNotificationRead(id: string) {
    const response = await this.client.patch(`/notifications/${id}/read`);
    return response.data;
  }

  async markAllNotificationsRead() {
    const response = await this.client.patch('/notifications/mark-all-read');
    return response.data;
  }

  async deleteNotification(id: string) {
    const response = await this.client.delete(`/notifications/${id}`);
    return response.data;
  }

  async triggerNotificationChecks() {
      const response = await this.client.post('/notifications/trigger-checks');
      return response.data;
  }

  // Inclusions & Exclusions
  async getAutoFill(destinationIds: string[], mode: string = 'chain') {
    const response = await this.client.post('/destination-combinations/auto-fill', { destination_ids: destinationIds, mode });
    return response.data;
  }

  async getInclusions() {
    const response = await this.client.get('/inclusions');
    return response.data;
  }

  async createInclusion(data: { name: string; category?: string; icon_name?: string }) {
    const response = await this.client.post('/inclusions', data);
    return response.data;
  }

  async deleteInclusion(id: string) {
    const response = await this.client.delete(`/inclusions/${id}`);
    return response.data;
  }

  async getExclusions() {
    const response = await this.client.get('/exclusions');
    return response.data;
  }

  async createExclusion(data: { name: string; category?: string; icon_name?: string }) {
    const response = await this.client.post('/exclusions', data);
    return response.data;
  }

  async deleteExclusion(id: string) {
    const response = await this.client.delete(`/exclusions/${id}`);
    return response.data;
  }

  // Company Content & Assets
  async getCompanyTemplates() {
    const response = await this.client.get('/content/company/templates');
    return response.data;
  }

  async updateCompanyTemplate(key: string, data: { content: string }) {
    const response = await this.client.patch(`/content/company/templates/${key}`, data);
    return response.data;
  }

  async listCompanyAssets(assetType?: string) {
    const params = assetType ? { asset_type: assetType } : {};
    const response = await this.client.get('/content/company/assets', { params });
    return response.data;
  }

  async uploadCompanyAsset(file: File, assetType: string, assetName?: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('asset_type', assetType);
    if (assetName) formData.append('asset_name', assetName);
    
    const response = await this.client.post('/content/company/assets', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async linkCompanyAsset(data: { asset_url: string; asset_type: string; asset_name?: string }) {
    const response = await this.client.post('/content/company/assets/link', data);
    return response.data;
  }

  async deleteCompanyAsset(id: string) {
    const response = await this.client.delete(`/content/company/assets/${id}`);
    return response.data;
  }


  async uploadBaseTourImages(id: string, files: File[]) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    
    const response = await this.client.post(`/base-tours/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async linkBaseTourImages(id: string, images: { image_url: string; caption?: string; image_role?: string }[]) {
    const response = await this.client.post(`/base-tours/${id}/images/link`, images);
    return response.data;
  }

  async uploadItineraryImages(id: string, files: File[]) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    
    const response = await this.client.post(`/itineraries/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }


  async deleteItineraryImage(imageId: string) {
     const response = await this.client.delete(`/itineraries/images/${imageId}`);
     return response.data;
  }

  // Media Library
  async getMediaLibrary(params?: any) {
    const response = await this.client.get('/media/library', { params });
    return response.data;
  }

  async deleteMediaImage(sourceType: string, imageId: string) {
    const response = await this.client.delete(`/media/library/${sourceType}/${imageId}`);
    return response.data;
  }

  async linkItineraryImages(id: string, images: {image_url: string, caption?: string}[]) {
      const response = await this.client.post(`/itineraries/${id}/images/link`, images);
      return response.data;
  }

  async updateItineraryImage(imageId: string, data: { caption?: string, image_role?: string, sort_order?: number }) {
      const response = await this.client.put(`/itineraries/images/${imageId}`, data);
      return response.data;
  }
}

export const apiClient = new APIClient();
export default apiClient;
