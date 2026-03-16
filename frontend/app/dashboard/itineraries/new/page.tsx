'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Copy, Pencil, ArrowRight, Loader2 } from 'lucide-react';
import apiClient from '@/lib/api/client';

type CreationMethod = 'choose' | 'edit' | 'custom' | null;

interface BaseTour {
  id: string;
  title: string;
  tour_code: string;
  duration_days: number;
  duration_nights: number;
  description: string;
}

interface TourType {
  id: string;
  name: string;
}

export default function NewItineraryPage() {
  const router = useRouter();
  const [method, setMethod] = useState<CreationMethod>(null);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API data state
  const [baseTours, setBaseTours] = useState<BaseTour[]>([]);
  const [tourTypes, setTourTypes] = useState<TourType[]>([]);
  const [loadingTours, setLoadingTours] = useState(false);

  // Customer details state
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [numberOfPax, setNumberOfPax] = useState('2');
  const [nationality, setNationality] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');

  // Itinerary details state
  const [title, setTitle] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [tourTypeId, setTourTypeId] = useState('');

  // For method 1 & 2: Package selection
  const [selectedPackage, setSelectedPackage] = useState('');

  // Fetch base tours and tour types on mount
  useEffect(() => {
    const fetchData = async () => {
      setLoadingTours(true);
      try {
        const [toursResponse, typesResponse] = await Promise.all([
          apiClient.get('/api/v1/base-tours?page_size=100'),
          apiClient.get('/api/v1/tour-types')
        ]);

        setBaseTours(toursResponse.data.items || []);
        setTourTypes(typesResponse.data.items || typesResponse.data || []);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Failed to load tour packages. Please refresh the page.');
      } finally {
        setLoadingTours(false);
      }
    };

    fetchData();
  }, []);

  const handleMethodSelection = (selectedMethod: CreationMethod) => {
    setMethod(selectedMethod);
    setStep(2);
  };

  const handlePackageSelect = (packageId: string) => {
    setSelectedPackage(packageId);
    const tour = baseTours.find(t => t.id === packageId);
    if (tour) {
      setTitle(tour.title);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const travelers = [
        {
          full_name: customerName,
          email: customerEmail,
          phone: customerPhone || null,
          nationality: nationality || null,
          special_requests: specialRequests || null,
          is_primary: true
        }
      ];

      // Add additional travelers if numberOfPax > 1
      const paxCount = parseInt(numberOfPax, 10);
      for (let i = 1; i < paxCount; i++) {
        travelers.push({
          full_name: `Traveler ${i + 1}`,
          email: null,
          phone: null,
          nationality: null,
          special_requests: null,
          is_primary: false
        });
      }

      let endpoint = '';
      let payload: Record<string, unknown> = {};

      if (method === 'choose') {
        endpoint = '/api/v1/itineraries/create-from-base';
        payload = {
          base_tour_id: selectedPackage,
          travelers,
          departure_date: departureDate
        };
      } else if (method === 'edit') {
        endpoint = '/api/v1/itineraries/create-from-edited';
        payload = {
          base_tour_id: selectedPackage,
          title,
          travelers,
          departure_date: departureDate,
          days: [] // Will be populated in next step
        };
      } else if (method === 'custom') {
        endpoint = '/api/v1/itineraries/create-custom';
        payload = {
          title,
          tour_type_id: tourTypeId,
          description: '',
          travelers,
          departure_date: departureDate,
          days: [] // Will be populated in next step
        };
      }

      const response = await apiClient.post(endpoint, payload);

      if (response.data && response.data.id) {
        // Redirect to the itinerary edit page for further customization
        router.push(`/dashboard/itineraries/${response.data.id}`);
      } else {
        router.push('/dashboard/itineraries');
      }
    } catch (err: unknown) {
      console.error('Failed to create itinerary:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to create itinerary. Please try again.';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || errorMessage);
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  if (step === 1) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Create New Itinerary</h1>
          <p className="text-gray-600 mt-1">
            Choose how you want to create the itinerary
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Method 1: Choose Existing Package */}
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-primary">
            <CardHeader>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <FileText className="h-8 w-8 text-primary" />
                </div>
              </div>
              <CardTitle>Choose Existing Package</CardTitle>
              <CardDescription>
                Select from {baseTours.length || '200+'}  pre-designed tour packages and assign to customer
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Quick and easy setup</li>
                <li>• Pre-configured itineraries</li>
                <li>• Proven tour designs</li>
                <li>• Instant availability</li>
              </ul>
              <Button
                className="w-full"
                onClick={() => handleMethodSelection('choose')}
                disabled={loadingTours}
              >
                {loadingTours ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    Choose Package
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Method 2: Edit Existing Package */}
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-green-500">
            <CardHeader>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-100 rounded-lg">
                  <Pencil className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <CardTitle>Edit Existing Package</CardTitle>
              <CardDescription>
                Start with a package template and customize it for your customer
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Customizable itineraries</li>
                <li>• Modify accommodations</li>
                <li>• Adjust activities</li>
                <li>• Flexible pricing</li>
              </ul>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => handleMethodSelection('edit')}
                disabled={loadingTours}
              >
                {loadingTours ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    Edit Package
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Method 3: Build Custom */}
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-purple-500">
            <CardHeader>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Copy className="h-8 w-8 text-purple-600" />
                </div>
              </div>
              <CardTitle>Build Custom Itinerary</CardTitle>
              <CardDescription>
                Create a completely custom itinerary from scratch
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Full customization</li>
                <li>• Pick any destinations</li>
                <li>• Custom activities</li>
                <li>• Unique experiences</li>
              </ul>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => handleMethodSelection('custom')}
              >
                Build Custom
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => setStep(1)}
          className="mb-4"
        >
          ← Back to method selection
        </Button>
        <h1 className="text-2xl font-bold text-gray-900">
          {method === 'choose' && 'Choose Existing Package'}
          {method === 'edit' && 'Edit Package Template'}
          {method === 'custom' && 'Build Custom Itinerary'}
        </h1>
        <p className="text-gray-600 mt-1">
          Fill in the customer details and itinerary information
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer Information */}
        <Card>
          <CardHeader>
            <CardTitle>Customer Information</CardTitle>
            <CardDescription>Enter the primary traveler details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <Input
                  required
                  placeholder="John Smith"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <Input
                  required
                  type="email"
                  placeholder="john@example.com"
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <Input
                  placeholder="+1 234 567 8900"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nationality
                </label>
                <Input
                  placeholder="United States"
                  value={nationality}
                  onChange={(e) => setNationality(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Travelers *
                </label>
                <Input
                  required
                  type="number"
                  min="1"
                  placeholder="2"
                  value={numberOfPax}
                  onChange={(e) => setNumberOfPax(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Special Requests
                </label>
                <Input
                  placeholder="Dietary requirements, accessibility needs..."
                  value={specialRequests}
                  onChange={(e) => setSpecialRequests(e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Package Selection for Method 1 & 2 */}
        {(method === 'choose' || method === 'edit') && (
          <Card>
            <CardHeader>
              <CardTitle>
                {method === 'choose' ? 'Select Package' : 'Select Package to Edit'}
              </CardTitle>
              <CardDescription>
                {method === 'choose'
                  ? 'Choose from available tour packages'
                  : 'Choose a package as your starting point'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingTours ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                  <span className="ml-2 text-gray-500">Loading packages...</span>
                </div>
              ) : baseTours.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No tour packages available. Please contact admin.
                </div>
              ) : (
                <select
                  required={method !== 'custom'}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
                  value={selectedPackage}
                  onChange={(e) => handlePackageSelect(e.target.value)}
                >
                  <option value="">Select a package...</option>
                  {baseTours.map((tour) => (
                    <option key={tour.id} value={tour.id}>
                      {tour.title} - {tour.duration_days} Days / {tour.duration_nights} Nights
                      {tour.tour_code && ` (${tour.tour_code})`}
                    </option>
                  ))}
                </select>
              )}
            </CardContent>
          </Card>
        )}

        {/* Tour Type for Custom Method */}
        {method === 'custom' && (
          <Card>
            <CardHeader>
              <CardTitle>Tour Type</CardTitle>
              <CardDescription>Select the type of tour</CardDescription>
            </CardHeader>
            <CardContent>
              <select
                required
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
                value={tourTypeId}
                onChange={(e) => setTourTypeId(e.target.value)}
              >
                <option value="">Select tour type...</option>
                {tourTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>
        )}

        {/* Itinerary Details */}
        <Card>
          <CardHeader>
            <CardTitle>Itinerary Details</CardTitle>
            <CardDescription>Provide travel dates and title</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Itinerary Title *
              </label>
              <Input
                required
                placeholder="Tanzania Safari Adventure"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Departure Date *
              </label>
              <Input
                required
                type="date"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
              />
              <p className="text-xs text-gray-500 mt-1">
                Return date will be auto-calculated based on the tour duration
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Form Actions */}
        <div className="flex justify-end gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push('/dashboard/itineraries')}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              method === 'custom' ? 'Continue to Builder' : 'Create Itinerary'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
