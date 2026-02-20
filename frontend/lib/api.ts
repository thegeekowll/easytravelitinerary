import axios from 'axios';

const getBaseUrl = () => {
  let url = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
  if (!url.endsWith('/api/v1')) {
    url = url.replace(/\/$/, '') + '/api/v1';
  }
  return url;
};

const API_URL = getBaseUrl();

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Itinerary {
  id: string;
  reference_number?: string;
  unique_code: string;
  tour_title: string;
  client_name?: string;
  client_email?: string;
  customer_name?: string; // Keep for backward compatibility if needed, but client_name is preferred
  departure_date: string;
  return_date: string;
  duration_days: number;
  duration_nights: number;
  status: 'draft' | 'sent' | 'confirmed' | 'completed' | 'cancelled';
  payment_status?: 'not_paid' | 'partially_paid' | 'fully_paid' | 'custom';
  total_price?: number;
  created_by?: string;
  created_by_name?: string;
  created_at: string;
  creation_method: 'choose_existing' | 'edit_existing' | 'custom';
  base_tour_title?: string;
  pdf_url?: string;
  primary_traveler?: {
    full_name: string;
    email?: string;
  };
}

export const getItineraries = async (params?: { skip?: number; limit?: number }) => {
  const response = await api.get('/itineraries/', { params });
  return response.data.items;
};

export const deleteItinerary = async (id: string) => {
  const response = await api.delete(`/itineraries/${id}`);
  return response.data;
};

export const getItineraryPublic = async (id: string, code?: string) => {
  const url = code ? `/public/itineraries/${code}` : `/public/itineraries/${id}`;
  const response = await api.get(url);
  return response.data;
};

export interface AutoFillResponse {
  type: 'single' | 'pair' | 'multiple';
  description?: string;
  activity?: string;
  suggestions: Array<{
    pair_name: string;
    description: string;
    activity: string;
    destination_1_id: string;
    destination_2_id: string;
  }>;
}

export const autoFillDestinations = async (destinationIds: string[]) => {
  const response = await api.post<AutoFillResponse>('/destination-combinations/auto-fill', {
    destination_ids: destinationIds,
  });
  return response.data;
};

export interface Destination {
  id: string;
  name: string;
  country: string;
}

export const getDestinations = async (search?: string) => {
  const response = await api.get('/destinations', { params: { search, limit: 100 } });
  return response.data.items;
};

export const getMatrixGrid = async (rowPage = 0, colPage = 0) => {
  const response = await api.get('/destination-combinations/grid', {
    params: { page_row: rowPage, page_col: colPage, page_size: 20 }
  });
  const data = response.data;
  
  // Transform combinations list to map for easier lookup
  const combinationsMap: Record<string, any> = {};
  if (Array.isArray(data.combinations)) {
    data.combinations.forEach((combo: any) => {
      // Add lookup for forward direction only (A->B)
      // Key format must match what page.tsx expects: `${row.id}_${col.id}`
      // Backend returns destination_1_id and destination_2_id (or None)
      
      const key = `${combo.destination_1_id}_${combo.destination_2_id || combo.destination_1_id}`; 
      // Note: If diagonal (dest_2 is null), backend behaves as A->A. 
      // In page.tsx, diagonal is row.id == col.id. 
      
      combinationsMap[key] = combo;
    });
  }

  return {
    rows: data.row_destinations,
    cols: data.col_destinations,
    combinations: combinationsMap,
    total: data.total_destinations,
    page: data.page_row,
    pageSize: data.page_size
  };
};

export const updateCombination = async (id: string, data: { description?: string, activity?: string, bidirectional?: boolean }) => {
  const response = await api.patch(`/destination-combinations/${id}`, {
    description_content: data.description,
    activity_content: data.activity,
    bidirectional: data.bidirectional
  });
  return response.data;
};

export const createCombination = async (data: { dest1Id: string, dest2Id?: string, description: string, activity: string, bidirectional?: boolean }) => {
  const response = await api.post('/destination-combinations', {
    destination_1_id: data.dest1Id,
    destination_2_id: data.dest2Id,
    description_content: data.description,
    activity_content: data.activity,
    bidirectional: data.bidirectional
  });
  return response.data;
};



// ==================== Destination Management ====================

export const createDestination = async (data: {
  name: string;
  country: string;
  region?: string;
  description?: string;
  image_urls?: string[];
}) => {
  const response = await api.post('/destinations', data);
  return response.data;
};

export const updateDestination = async (id: string, data: {
  name?: string;
  country?: string;
  region?: string;
  description?: string;
  image_urls?: string[];
  is_active?: boolean;
}) => {
  const response = await api.patch(`/destinations/${id}`, data);
  return response.data;
};

export const deleteDestination = async (id: string) => {
  const response = await api.delete(`/destinations/${id}`);
  return response.data;
};

export const uploadDestinationImages = async (id: string, files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/destinations/${id}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// ==================== Accommodation Management ====================

export const getAccommodations = async (params?: { search?: string; limit?: number }) => {
  const response = await api.get('/accommodations', { params });
  return response.data;
};

// ==================== Itinerary Management ====================

export const createCustomItinerary = async (data: any) => {
  const response = await api.post('/itineraries/create-custom', data);
  return response.data;
};

export const uploadItineraryImages = async (id: string, files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/itineraries/${id}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteItineraryImage = async (imageId: string) => {
  const response = await api.delete(`/itineraries/images/${imageId}`);
  return response.data;
};

// ==================== Analytics ====================

export interface AnalyticsResponse {
  overview: {
    totalRevenue: number;
    revenueGrowth: number;
    totalBookings: number;
    bookingsGrowth: number;
    activeCustomers: number;
    customersGrowth: number;
    avgBookingValue: number;
    avgBookingGrowth: number;
  };
  monthlyRevenue: Array<{
    month: string;
    revenue: number;
    bookings: number;
  }>;
  topDestinations: Array<{
    destination: string;
    bookings: number;
    revenue: number;
  }>;
  topAgents: Array<{
    name: string;
    bookings: number;
    revenue: number;
    conversion: number;
  }>;
  bookingsByStatus: Array<{
    status: string;
    count: number;
    percentage: number;
  }>;
  paymentMetrics: {
    totalPaid: number;
    totalPending: number;
    totalDeposits: number;
    avgPaymentTime: number;
  };
}

export const getAnalytics = async () => {
  const response = await api.get<AnalyticsResponse>('/analytics');
  return response.data;
};
