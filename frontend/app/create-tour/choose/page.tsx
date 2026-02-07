'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

function ChooseContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mode = searchParams.get('mode');
  const isEditMode = mode === 'edit';

  const [baseTours, setBaseTours] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    const loadBaseTours = async () => {
      try {
        const data = await apiClient.getBaseTours();
        // Handle both pagination and direct array
        setBaseTours(data.items || data || []);
      } catch (error) {
        console.error('Failed to load base tours:', error);
        toast.error('Failed to load base tour options');
      } finally {
        setLoading(false);
      }
    };
    loadBaseTours();
  }, []);

  const handleSelectTour = async (tour: any) => {
    const travelerDataStr = sessionStorage.getItem('draft_traveler_info');
    if (!travelerDataStr) {
      toast.error('Traveler information not found. Please start over.');
      router.push('/create-tour');
      return;
    }

    try {
      setProcessingId(tour.id);
      const travelerData = JSON.parse(travelerDataStr);

      // Construct travelers array for schema
      // TravelerBase needs: full_name, email, phone, age, nationality, is_primary
      const travelers = [
        {
          full_name: travelerData.primaryName,
          email: travelerData.primaryEmail,
          phone: travelerData.primaryPhone,
          age: parseInt(travelerData.primaryAge) || undefined,
          nationality: travelerData.primaryCountry,
          is_primary: true
        }
      ];

      // Add other travelers
      if (travelerData.otherTravelers && Array.isArray(travelerData.otherTravelers)) {
        travelerData.otherTravelers.forEach((t: any) => {
          if (t.name) {
            travelers.push({
              full_name: t.name,
              email: undefined,
              phone: undefined,
              age: parseInt(t.age) || undefined,
              nationality: undefined, // Or assume same group nationality? schema allows optional
              is_primary: false
            });
          }
        });
      }

      // Payload matching ItineraryCreateChooseExisting
      const durationDays = tour.duration_days || 1;
      const payload = {
        base_tour_id: tour.id,
        travelers: travelers,
        departure_date: travelerData.arrivalDate || new Date().toISOString().split('T')[0],
        tour_title: tour.tour_name || tour.title || 'Untitled Tour', // Use tour_name from BaseTour schema
        client_name: travelerData.primaryName,
        client_email: travelerData.primaryEmail,
        client_phone: travelerData.primaryPhone,
        number_of_travelers: travelerData.numberOfTravelers,
        return_date: calculateReturnDate(travelerData.arrivalDate, durationDays)
      };

      console.log('Creating itinerary with payload:', payload);

      const itinerary = await apiClient.createItineraryFromBaseTour(payload);
      
      toast.success('Itinerary created successfully!');
      sessionStorage.removeItem('draft_traveler_info');
      
      const targetUrl = isEditMode 
        ? `/dashboard/itineraries/${itinerary.id}?edit=true`
        : `/dashboard/itineraries/${itinerary.id}`;
      
      router.push(targetUrl);

    } catch (error: any) {
      console.error('Failed to create itinerary:', error);
      const errorMsg = error.response?.data?.detail;
      const displayMsg = typeof errorMsg === 'string' ? errorMsg : 
                        (Array.isArray(errorMsg) ? 'Validation Error: Check console' : 'Failed to create itinerary');
      
      if (Array.isArray(errorMsg)) {
          console.error('Validation errors:', errorMsg);
      }
      toast.error(displayMsg);
      setProcessingId(null);
    }
  };

  const calculateReturnDate = (startDateStr: string, durationDays: number) => {
    if (!startDateStr) return new Date().toISOString().split('T')[0];
    const duration = durationDays || 1; // Fallback
    const date = new Date(startDateStr);
    date.setDate(date.getDate() + (duration - 1));
    return date.toISOString().split('T')[0];
  };

  const filteredTours = baseTours.filter(tour => 
    (tour.tour_name || tour.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (tour.description || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {isEditMode ? 'Select Base Tour to Edit' : 'Select Base Tour'}
          </h1>
          <p className="text-gray-600">
            {isEditMode 
              ? 'Choose a template to customize' 
              : 'Choose a template to start your itinerary'}
          </p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="Search tours..." 
            className="pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      ) : filteredTours.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTours.map((tour) => (
            <Card key={tour.id} className="flex flex-col h-full hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gray-200 relative overflow-hidden">
                {/* Fallback image logic if tour has images */}
                {tour.images && tour.images.length > 0 ? (
                   <img src={tour.images[0].image_url} alt={tour.tour_name || tour.title} className="w-full h-full object-cover" />
                ) : (
                   <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400">
                     <span className="text-sm">No Image</span>
                   </div>
                )}
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                   {tour.number_of_days || tour.duration_days} Days
                </div>
              </div>
              <CardHeader>
                <CardTitle className="line-clamp-1">{tour.tour_name || tour.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-sm text-gray-600 line-clamp-3">
                  {tour.description || 'No description available.'}
                </p>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full" 
                  onClick={() => handleSelectTour(tour)}
                  disabled={!!processingId}
                >
                  {processingId === tour.id ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    isEditMode ? 'Select & Edit' : 'Select This Tour'
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
          No tours found matching your search.
        </div>
      )}
    </div>
  );
}

export default function ChooseBaseTourPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>}>
      <ChooseContent />
    </Suspense>
  );
}
