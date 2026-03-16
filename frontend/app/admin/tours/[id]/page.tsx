'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import BaseTourForm from '@/components/tours/base-tour-form';
import { apiClient } from '@/lib/api/client';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function EditBaseTourPage() {
  const params = useParams();
  const id = params.id as string;
  const [tour, setTour] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const fetchTour = async () => {
      try {
        const data = await apiClient.getBaseTour(id);
        setTour(data);
      } catch (error: any) {
        console.error("Failed to load tour", error);
        setErrorMsg(error.response?.data?.detail || "Failed to load tour details");
        toast.error("Failed to load tour details");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
        fetchTour();
    }
  }, [id]);

  if (loading) {
      return <div className="flex justify-center py-12"><Loader2 className="animate-spin h-8 w-8 text-gray-400"/></div>;
  }

  if (!tour) {
      return <div className="text-center py-12 text-red-500">Error: {errorMsg || "Tour not found"}</div>;
  }

  return <BaseTourForm initialData={tour} isEditing={true} />;
}
