'use client';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Download,
  Mail,
  Calendar,
  Users,
  Hotel,
  UtensilsCrossed,
  Plane,
  Phone,
  Loader2,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getItineraryPublic, downloadPDF } from '@/lib/api';

// Define types locally or import from types file
interface ItineraryDay {
  day_number: number;
  title: string;
  description: string;
  accommodation?: string; // API might return this
  accommodation_name?: string; // Or this depending on join
  meals?: string;
  activities?: string[]; // API returns list of strings or objects?
}

interface ItineraryData {
  id: string;
  reference_number: string;
  title: string;
  customer_name?: string; // Might be primary_traveler_name
  primary_traveler_name?: string;
  customer_email?: string;
  customer_phone?: string;
  number_of_pax: number;
  start_date: string;
  end_date: string;
  duration_days: number;
  duration_nights: number;
  status: string;
  agent_name?: string;
  agent_email?: string;
  agent_phone?: string;
  days: ItineraryDay[];
  includes: string[];
  excludes: string[];
}

export default function PublicItineraryPage() {
  const params = useParams();
  const id = params.id as string;

  const [itinerary, setItinerary] = useState<ItineraryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        // Attempt to fetch public itinerary
        const data = await getItineraryPublic(id);
        
        // Map backend response to UI structure if needed 
        // Backend returns "days" as list of objects?
        // We'll trust the shape for now and debug if needed
        setItinerary(data);
      } catch (err: any) {
        console.error('Failed to fetch itinerary:', err);
        setError('Itinerary not found or access denied.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleDownloadPDF = async () => {
    if (!id) return;
    try {
      setDownloading(true);
      toast.loading('Generating PDF...', { id: 'pdf-toast' });
      
      const blob = await downloadPDF(id);
      
      // Create object URL and trigger download
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      // Use efficient filename if possible, otherwise generic
      link.setAttribute('download', `Itinerary_${itinerary?.reference_number || 'Travel'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      
      toast.success('PDF Downloaded!', { id: 'pdf-toast' });
    } catch (err) {
      console.error('PDF download failed:', err);
      toast.error('Failed to download PDF. Please try again.', { id: 'pdf-toast' });
    } finally {
      setDownloading(false);
    }
  };

  const handleContactAgent = () => {
    if (itinerary?.agent_email) {
      window.location.href = `mailto:${itinerary.agent_email}`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
        <p className="ml-4 text-gray-600">Loading your itinerary...</p>
      </div>
    );
  }

  if (error || !itinerary) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
        <h1 className="text-2xl font-bold text-red-600 mb-2">Error</h1>
        <p className="text-gray-600">{error || 'Itinerary not found.'}</p>
        <Button className="mt-4" onClick={() => window.location.reload()}>
          Try Again
        </Button>
      </div>
    );
  }

  // Helper to safely get traveler info
  const customerName = itinerary.customer_name || itinerary.primary_traveler_name || 'Guest';
  const customerEmail = itinerary.customer_email || 'N/A';
  const customerPhone = itinerary.customer_phone || 'N/A';
  const agentName = itinerary.agent_name || 'Travel Agent';
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-3">
              <Badge className="bg-white text-blue-800">{itinerary.reference_number || 'REF'}</Badge>
              <Badge
                variant={itinerary.status === 'CONFIRMED' || itinerary.status === 'COMPLETED' ? 'success' : 'default'}
                className={itinerary.status === 'CONFIRMED' || itinerary.status === 'COMPLETED' ? "bg-green-500 text-white" : "bg-gray-500 text-white"}
              >
                {itinerary.status}
              </Badge>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">{itinerary.title}</h1>
            <p className="text-blue-100 text-lg">
              {itinerary.duration_days === 1
                ? '1 Day Safari Experience'
                : `${itinerary.duration_days} Days / ${itinerary.duration_nights !== undefined ? itinerary.duration_nights : (itinerary.duration_days - 1)} ${(itinerary.duration_nights !== undefined ? itinerary.duration_nights : (itinerary.duration_days - 1)) === 1 ? 'Night' : 'Nights'} Safari Experience`}
            </p>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Quick Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <Calendar className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Travel Dates</p>
                    <p className="font-semibold">
                      {new Date(itinerary.start_date).toLocaleDateString()} -{' '}
                      {new Date(itinerary.end_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Travelers</p>
                    <p className="font-semibold">{itinerary.number_of_pax} People</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <Plane className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Start Location</p>
                    <p className="font-semibold">Arusha, Tanzania</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mb-8">
            <Button onClick={handleDownloadPDF} className="flex-1" disabled={downloading}>
              {downloading ? (
                 <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              {downloading ? "Generating PDF..." : "Download PDF"}
            </Button>
            <Button onClick={handleContactAgent} variant="outline" className="flex-1">
              <Mail className="h-4 w-4 mr-2" />
              Contact Agent
            </Button>
          </div>

          {/* Customer Information */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Traveler Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{customerName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-semibold">{customerEmail}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-semibold">{customerPhone}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Group Size</p>
                  <p className="font-semibold">{itinerary.number_of_pax} travelers</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Day by Day Itinerary */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Day by Day Itinerary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {itinerary.days?.map((day) => (
                  <div key={day.day_number} className="border-l-4 border-blue-600 pl-6 pb-6">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold flex-shrink-0">
                        {day.day_number}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{day.title}</h3>
                        <p className="text-gray-600 mt-1">{day.description}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 ml-13">
                      <div className="flex items-start gap-2">
                        <Hotel className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-500">Accommodation</p>
                          <p className="font-medium text-gray-900">{day.accommodation || day.accommodation_name || 'TBA'}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <UtensilsCrossed className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-500">Meals Included</p>
                          <p className="font-medium text-gray-900">{day.meals || 'Breakfast, Lunch, Dinner'}</p>
                        </div>
                      </div>
                    </div>

                    {day.activities && day.activities.length > 0 && (
                      <div className="mt-4 ml-13">
                        <p className="text-sm text-gray-500 mb-2">Activities:</p>
                        <div className="flex flex-wrap gap-2">
                          {day.activities.map((activity, idx) => (
                            <Badge key={idx} variant="outline">
                              {activity}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* What's Included/Excluded */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-green-700">What's Included</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {itinerary.includes?.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-green-600 mt-1">✓</span>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-red-700">What's Not Included</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {itinerary.excludes?.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-red-600 mt-1">✗</span>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Contact Agent */}
          {agentName && (
            <Card>
              <CardHeader>
                <CardTitle>Your Travel Agent</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl font-bold text-blue-600">
                    {agentName.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-lg">{agentName}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                      {itinerary.agent_email && (
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          <a
                            href={`mailto:${itinerary.agent_email}`}
                            className="hover:text-blue-600"
                          >
                            {itinerary.agent_email}
                          </a>
                        </div>
                      )}
                      {itinerary.agent_phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          <a
                            href={`tel:${itinerary.agent_phone}`}
                            className="hover:text-blue-600"
                          >
                            {itinerary.agent_phone}
                          </a>
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      Feel free to contact me if you have any questions or need assistance with
                      your trip.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Footer */}
          <div className="text-center mt-8 text-gray-600 text-sm">
            <p>Easy. Travel Itinerary Builder</p>
            <p className="mt-1">Thank you for choosing us for your adventure!</p>
          </div>
        </div>
      </div>
    </div>
  );
}
