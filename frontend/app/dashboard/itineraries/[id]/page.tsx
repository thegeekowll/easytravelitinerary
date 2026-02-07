'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
    Plus, ImageIcon, Upload,
    ArrowLeft, Save, Hotel, UtensilsCrossed, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client'; 
 
import DayEditor from '@/components/tours/day-editor';
import InclusionManager from '@/components/tours/inclusion-manager';
import TravelersList from '@/components/itineraries/travelers-list';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

const statusColors: Record<string, "default" | "secondary" | "destructive" | "outline" | "success" | "warning" | "info" | "purple"> = {
  draft: 'secondary',
  confirmed: 'info',
  sent: 'purple',
  under_review: 'warning',
  completed: 'success',
  cancelled: 'destructive',
};

export default function ItineraryDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const shouldEdit = searchParams.get('edit') === 'true';
  const [isEditing, setIsEditing] = useState(shouldEdit);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [targetImageRole, setTargetImageRole] = useState<string | null>(null);

  // 1. Fetch Itinerary
  const { data: initialItinerary, isLoading, error, refetch } = useQuery({
    queryKey: ['itinerary', params.id],
    queryFn: () => apiClient.getItinerary(params.id),
  });

  // 2. Fetch Reference Data for Editors
  const { data: destinationsData } = useQuery({ queryKey: ['destinations', 'all'], queryFn: () => apiClient.getDestinations({ limit: 100 }) });
  const { data: accommodationsData } = useQuery({ queryKey: ['accommodations', 'all'], queryFn: () => apiClient.getAccommodations({ limit: 100 }) });
  const { data: tourTypes } = useQuery({ queryKey: ['tourTypes'], queryFn: () => apiClient.getTourTypes() });
  const { data: accLevels } = useQuery({ queryKey: ['accLevels'], queryFn: () => apiClient.getAccommodationLevels() });

  const destinations = destinationsData?.items || [];
  const accommodations = accommodationsData?.items || [];

  // Local state for editing
  const [itinerary, setItinerary] = useState<any>(null);

  // Sync initial state
  useEffect(() => {
    // console.log("Itinerary State Debug:", { initialItinerary, itinerary, isLoading, error });
    if (initialItinerary && !itinerary) {
      // Ensure days have destination_ids mapped from destinations object if missing
      const mappedDays = (initialItinerary.days || []).map((day: any) => ({
        ...day,
        destination_ids: day.destination_ids || (day.destinations || []).map((d: any) => d.id)
      }));
      
      setItinerary({
          ...initialItinerary,
          days: mappedDays
      });
    }
  }, [initialItinerary]);

  // Auto-calculate payment status
  useEffect(() => {
    if (isEditing && itinerary) { // Ensure itinerary is not null
        const total = parseFloat(itinerary.total_price) || 0;
        const deposit = parseFloat(itinerary.deposit_amount) || 0;
        let newStatus = 'not_paid';
        
        if (deposit > 0) {
           newStatus = (deposit >= total && total > 0) ? 'fully_paid' : 'partially_paid';
        }
        
        if (itinerary.payment_status !== newStatus) {
           setItinerary(prev => ({...prev, payment_status: newStatus}));
        }
    }
  }, [itinerary?.total_price, itinerary?.deposit_amount, isEditing]); // Add itinerary to dependencies to avoid null access

  // Handle Save
  const handleSave = async (statusOverride?: string, isAutoSave = false) => {
    if (!itinerary) return;
    
    // Determine status
    let newStatus = statusOverride || itinerary.status;
    if (!statusOverride && !isAutoSave && itinerary.status === 'draft') {
         // If manually saving and currently draft, ask user or default to confirmed? 
         // Logic: If user clicks "Save Changes", we keep it as is unless they click "Save Draft".
         // But previous logic was auto-promote. Let's keep it simple: retain status unless explicitly changed.
         newStatus = itinerary.status; 
    }

    try {
      const updateData = {
        // Basic Info
        tour_title: itinerary.tour_title,
        status: newStatus,
        notes: itinerary.notes,
        
        // Client Info
        client_name: itinerary.client_name,
        client_email: itinerary.client_email,
        client_phone: itinerary.client_phone,
        number_of_travelers: parseInt(itinerary.number_of_travelers) || 1,
        
        // Trip Details
        departure_date: itinerary.departure_date,
        return_date: itinerary.return_date,
        total_price: parseFloat(itinerary.total_price) || 0,
        deposit_amount: parseFloat(itinerary.deposit_amount) || 0,
        currency: itinerary.currency || 'USD',
        
        // Metadata
        tour_type_id: itinerary.tour_type_id || null,
        accommodation_level_id: itinerary.accommodation_level_id || null,
        difficulty_level: itinerary.difficulty_level,
        description: itinerary.description,
        highlights: itinerary.highlights,

        // Days
        days: itinerary.days.map((day: any) => ({
          id: day.id,
          day_number: day.day_number,
          day_title: day.day_title,
          description: day.description,
          activities: day.activities,
          meals_included: day.meals_included, 
          destination_ids: day.destination_ids || [],
          accommodation_id: day.accommodation_id,
          is_description_custom: day.is_description_custom ?? true,
          is_activity_custom: day.is_activity_custom ?? true,
          atmospheric_image_url: day.atmospheric_image_url
        })),
        
        // Inclusions/Exclusions (Map objects to IDs)
        inclusion_ids: itinerary.inclusions?.map((i: any) => i.id) || [],
        exclusion_ids: itinerary.exclusions?.map((e: any) => e.id) || [],
      };

      // console.log("DEBUG: handleSave payload:", updateData);
      await apiClient.updateItinerary(itinerary.id, updateData);
      
      const msg = isAutoSave ? 'Auto-saved' : 'Changes saved successfully';
      toast.success(msg);
      
      if (!isAutoSave) {
          setIsEditing(false);
          refetch(); // Refresh data from server
          // Do not nullify itinerary here; let useEffect sync it when initialItinerary updates
      } else {
           setItinerary({ ...itinerary, status: newStatus });
      }

    } catch (error) {
      console.error('Failed to update itinerary:', error);
      if (!isAutoSave) toast.error('Failed to save changes: ' + (error as any).message);
    }
  };

  // Handlers for Day Editor
  const handleDayChange = (updatedDay: any) => {
    const newDays = itinerary.days.map((d: any) => d.day_number === updatedDay.day_number ? updatedDay : d);
    setItinerary({ ...itinerary, days: newDays });
  };

  const handleAddDay = () => {
    const nextDayNum = (itinerary.days?.length || 0) + 1;
    const newDay = {
      day_number: nextDayNum,
      day_title: `Day ${nextDayNum}`,
      description: '',
      activities: '',
      destination_ids: [],
      accommodation_id: null,
      meals_included: ''
    };
    setItinerary({ ...itinerary, days: [...(itinerary.days || []), newDay] });
  };

  const handleRemoveDay = (dayNum: number) => {
      if (!confirm("Delete this day?")) return;
      const newDays = itinerary.days.filter((d: any) => d.day_number !== dayNum)
                                    .map((d: any, idx: number) => ({ ...d, day_number: idx + 1 }));
      setItinerary({ ...itinerary, days: newDays });
  };


  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin h-8 w-8" /></div>;
  if (error || !itinerary) return <div className="text-center py-20 text-red-500">Failed to load itinerary. Please try again.</div>;

  return (
    <div className="max-w-7xl mx-auto pb-20 p-6 space-y-6">
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="space-y-1">
             <div className="flex items-center gap-3">
                <Button variant="ghost" size="sm" onClick={() => router.back()} className="p-0 h-auto hover:bg-transparent text-gray-500">
                    <ArrowLeft className="h-4 w-4 mr-1" /> Back
                </Button>
             </div>
             <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold">{itinerary.tour_title}</h1>
                <Badge variant={statusColors[itinerary.status] as any}>{itinerary.status}</Badge>
             </div>
             <p className="text-gray-500 text-sm">
                Ref: {itinerary.unique_code} • {itinerary.duration_days === 1 ? '1 Day' : `${itinerary.duration_days} Days / ${itinerary.duration_nights !== undefined ? itinerary.duration_nights : (itinerary.duration_days - 1)} ${(itinerary.duration_nights !== undefined ? itinerary.duration_nights : (itinerary.duration_days - 1)) === 1 ? 'Night' : 'Nights'}`}
             </p>
        </div>
        <div className="flex gap-2">
            {!isEditing ? (
                <>
                    <Button variant="outline" onClick={() => window.open(`/view/${itinerary.unique_code}`, '_blank')}>Preview</Button>
                    <Button onClick={() => setIsEditing(true)}>Edit Itinerary</Button>
                </>
            ) : (
                <>
                    <Button variant="ghost" onClick={() => {
                        setItinerary(initialItinerary);
                        setIsEditing(false);
                    }}>Cancel</Button>
                    <Button onClick={() => handleSave(undefined, false)}>
                        <Save className="h-4 w-4 mr-2" /> Save Changes
                    </Button>
                </>
            )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Metadata & Config */}
        <div className="lg:col-span-1 space-y-6 transition-all">
            
            {/* Customer Information */}
            <Card>
                <CardHeader><CardTitle className="text-lg">Customer</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500 uppercase">Primary Contact</Label>
                        <p className="font-medium text-lg">{itinerary.client_name}</p>
                    </div>
                    <div className="text-sm text-gray-500 space-y-1">
                        {itinerary.client_email && <p>{itinerary.client_email}</p>}
                        {itinerary.client_phone && <p>{itinerary.client_phone}</p>}
                    </div>
                </CardContent>
            </Card>

            {/* Tour Configuration */}
            {/* General Settings (Type, Level, Difficulty) */}
            <Card>
                <CardHeader><CardTitle className="text-lg">General Info</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                     <div className="space-y-1">
                         <Label className="text-xs text-gray-500 uppercase">Tour Type</Label>
                         {isEditing ? (
                             <select 
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={itinerary.tour_type_id || ''}
                                onChange={(e) => setItinerary({...itinerary, tour_type_id: e.target.value})}
                             >
                                <option value="">Select Type</option>
                                {(Array.isArray(tourTypes) ? tourTypes : tourTypes?.items || [])?.map((t:any) => <option key={t.id} value={t.id}>{t.name}</option>)}
                             </select>
                         ) : (
                            <p className="font-medium">{itinerary.tour_type?.name || 'Unspecified'}</p>
                         )}
                     </div>

                     <div className="space-y-1">
                         <Label className="text-xs text-gray-500 uppercase">Accommodation Level</Label>
                         {isEditing ? (
                             <select 
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={itinerary.accommodation_level_id || ''}
                                onChange={(e) => setItinerary({...itinerary, accommodation_level_id: e.target.value})}
                             >
                                <option value="">Select Level</option>
                                {(Array.isArray(accLevels) ? accLevels : accLevels?.items || [])?.map((l:any) => <option key={l.id} value={l.id}>{l.name}</option>)}
                             </select>
                         ) : <p className="font-medium">{itinerary.accommodation_level?.name || (accLevels?.map ? accLevels.find((l:any) => l.id === itinerary.accommodation_level_id)?.name : accLevels?.items?.find((l:any) => l.id === itinerary.accommodation_level_id)?.name || 'Unspecified')}</p>}
                     </div>

                     <div className="space-y-1">
                         <Label className="text-xs text-gray-500 uppercase">Difficulty</Label>
                         {isEditing ? (
                             <select 
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={itinerary.difficulty_level || 'Moderate'}
                                onChange={(e) => setItinerary({...itinerary, difficulty_level: e.target.value})}
                             >
                                <option value="Easy">Easy</option>
                                <option value="Moderate">Moderate</option>
                                <option value="Challenging">Challenging</option>
                             </select>
                         ) : <p className="font-medium">{itinerary.difficulty_level || 'Unspecified'}</p>}
                     </div>
                </CardContent>
            </Card>

            {/* Payment & Pricing - NEW */}
            <Card>
                <CardHeader><CardTitle className="text-lg">Payment & Pricing</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                     <div className="grid grid-cols-2 gap-4">
                         <div className="col-span-2 flex flex-col gap-2">
                             <Label className="text-xs text-gray-500 uppercase">Payment Status</Label>
                             <div className="w-full">
                                <Badge 
                                    className="w-full justify-center py-1 text-sm font-semibold" 
                                    variant={itinerary.payment_status === 'fully_paid' ? 'success' : itinerary.payment_status === 'not_paid' ? 'destructive' : 'warning'}
                                >
                                    {itinerary.payment_status?.replace('_', ' ').toUpperCase() || 'NOT PAID'}
                                </Badge>
                             </div>
                         </div>
                         
                         <div className="space-y-1">
                             <Label className="text-xs text-gray-500 uppercase">Total Price</Label>
                             {isEditing ? (
                                <div className="relative">
                                    <span className="absolute left-2 top-2.5 text-gray-500 text-xs">$</span>
                                    <Input className="pl-6" type="number" value={itinerary.total_price} onChange={e => setItinerary({...itinerary, total_price: e.target.value})} />
                                </div>
                             ) : <p className="font-bold text-lg">{itinerary.currency} {itinerary.total_price}</p>}
                         </div>

                         <div className="space-y-1">
                             <Label className="text-xs text-gray-500 uppercase">Deposit</Label>
                             {isEditing ? (
                                <div className="relative">
                                    <span className="absolute left-2 top-2.5 text-gray-500 text-xs">$</span>
                                    <Input className="pl-6" type="number" value={itinerary.deposit_amount} onChange={e => setItinerary({...itinerary, deposit_amount: e.target.value})} />
                                </div>
                             ) : <p className="font-medium text-gray-600">{itinerary.currency} {itinerary.deposit_amount}</p>}
                         </div>
                     </div>
                </CardContent>
            </Card>

            {/* Admin Tools (Restored) */}
            <Card>
                <CardHeader><CardTitle className="text-lg">Admin Tools</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                     <div className="flex flex-col gap-2">
                        <Label className="text-xs text-gray-500 uppercase">Status</Label>
                        {isEditing ? (
                             <select 
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={itinerary.status}
                                onChange={(e) => setItinerary({...itinerary, status: e.target.value})}
                             >
                                <option value="draft">Draft</option>
                                <option value="under_review">Under Review</option>
                                <option value="sent">Sent</option>
                                <option value="confirmed">Confirmed</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                             </select>
                        ) : (
                            <div className="w-full">
                                <Badge 
                                    className="w-full justify-center py-1 text-sm font-semibold" 
                                    variant={statusColors[itinerary.status] as any}
                                >
                                    {itinerary.status?.replace('_', ' ').toUpperCase()}
                                </Badge>
                            </div>
                        )}
                     </div>
                     <div className="space-y-1">
                        <Label className="text-xs text-gray-500 uppercase">Internal Notes</Label>
                        {isEditing ? (
                            <textarea 
                                className="w-full border rounded p-2 text-sm" 
                                rows={4} 
                                value={itinerary.notes || ''} 
                                onChange={e => setItinerary({...itinerary, notes: e.target.value})}
                                placeholder="Internal notes not visible to customer..."
                            />
                        ) : (
                            <p className="text-sm text-gray-600 whitespace-pre-line">{itinerary.notes || 'No notes'}</p>
                        )}
                     </div>
                </CardContent>
            </Card>

            {/* Inclusions / Exclusions */}
            <Card>
                <CardHeader><CardTitle className="text-lg">Inclusions & Exclusions</CardTitle></CardHeader>
                <CardContent className="space-y-6">
                    {isEditing ? (
                        <>
                            <div className="space-y-2">
                                <Label className="text-xs font-bold text-green-700 uppercase">Included</Label>
                                <InclusionManager 
                                    type="inclusion" 
                                    selectedIds={itinerary.inclusions?.map((i:any) => i.id) || []}
                                    onSelectionChange={(_ids, items) => {
                                        setItinerary({...itinerary, inclusions: items || []})
                                    }}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-xs font-bold text-red-700 uppercase">Excluded</Label>
                                <InclusionManager 
                                    type="exclusion" 
                                    selectedIds={itinerary.exclusions?.map((e:any) => e.id) || []}
                                    onSelectionChange={(_ids, items) => setItinerary({...itinerary, exclusions: items || []})}
                                />
                            </div>
                        </>
                    ) : (
                        <div className="space-y-4 text-sm">
                            <div>
                                <h4 className="font-semibold text-green-700 mb-1">Included</h4>
                                <ul className="list-disc pl-4 space-y-1">{itinerary.inclusions?.map((i:any) => <li key={i.id}>{i.name}</li>)}</ul>
                                {(!itinerary.inclusions?.length) && <span className="text-gray-400 italic">None</span>}
                            </div>
                            <div>
                                <h4 className="font-semibold text-red-700 mb-1">Excluded</h4>
                                <ul className="list-disc pl-4 space-y-1">{itinerary.exclusions?.map((e:any) => <li key={e.id}>{e.name}</li>)}</ul>
                                {(!itinerary.exclusions?.length) && <span className="text-gray-400 italic">None</span>}
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>

        {/* Right Column: Main Content */}
        <div className="lg:col-span-2 space-y-6">
             
             {/* Key Details */}
             <Card>
                <CardHeader><CardTitle className="text-lg">Trip Details</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                        <Label className="text-xs text-gray-500 uppercase mb-1 block">Itinerary Title</Label>
                        {isEditing ? <Input value={itinerary.tour_title} onChange={e => setItinerary({...itinerary, tour_title: e.target.value})} /> : <p className="text-lg font-medium">{itinerary.tour_title}</p>}
                    </div>
                    
                    <div>
                        <Label className="text-xs text-gray-500 uppercase mb-1 block">Start Date</Label>
                        {isEditing ? <Input type="date" value={itinerary.departure_date} onChange={e => setItinerary({...itinerary, departure_date: e.target.value})} /> : <p>{new Date(itinerary.departure_date).toLocaleDateString()}</p>}
                    </div>
                    <div>
                        <Label className="text-xs text-gray-500 uppercase mb-1 block">End Date</Label>
                        {isEditing ? <Input type="date" value={itinerary.return_date} onChange={e => setItinerary({...itinerary, return_date: e.target.value})} /> : <p>{new Date(itinerary.return_date).toLocaleDateString()}</p>}
                    </div>

                    <div>
                         <Label className="text-xs text-gray-500 uppercase mb-1 block">Total Price</Label>
                         <p className="text-sm text-gray-500">Managed in Payment section</p>
                    </div>
                    <div>
                         <Label className="text-xs text-gray-500 uppercase mb-1 block">Deposit</Label>
                         <p className="text-sm text-gray-500">Managed in Payment section</p>
                    </div>
                </CardContent>
             </Card>
            
             {/* Description & Highlights */}
             <Card>
                <CardContent className="pt-6 space-y-4">
                     <div className="space-y-2">
                        <Label className="font-semibold">Description</Label>
                        {isEditing ? (
                            <textarea className="w-full border rounded p-2 text-sm" rows={4} value={itinerary.description || ''} onChange={e => setItinerary({...itinerary, description: e.target.value})} />
                        ) : <p className="text-gray-700 whitespace-pre-line">{itinerary.description || 'No description provided.'}</p>}
                     </div>
                     <div className="space-y-2">
                        <Label className="font-semibold">Highlights</Label>
                         {isEditing ? (
                            <textarea className="w-full border rounded p-2 text-sm" rows={3} value={itinerary.highlights || ''} onChange={e => setItinerary({...itinerary, highlights: e.target.value})} />
                        ) : <p className="text-gray-700 whitespace-pre-line">{itinerary.highlights || 'No highlights listed.'}</p>}
                     </div>
                </CardContent>
             </Card>

             {/* Images */}
             <Card>
                <CardHeader><CardTitle className="text-lg">Images</CardTitle></CardHeader>
                <CardContent className="pt-6">
                    {isEditing ? (
                        <div className="space-y-6">
                            {[
                                { role: 'cover', label: 'Cover Photo', desc: 'Main image displayed at the top' },
                                { role: 'accommodation_end', label: 'After Accommodations', desc: 'Displayed after the accommodation section' },
                                { role: 'inclusions', label: 'Includes/Excludes Page', desc: 'Background for inclusions section' },
                                { role: 'about_banner', label: 'About Us Banner', desc: 'Banner for the company info section' },
                                { role: 'end', label: 'End of Itinerary', desc: 'Final image at the end of the document' }
                            ].map((slot) => {
                                const activeImage = itinerary.images?.find((img: any) => img.image_role === slot.role);
                                
                                return (
                                    <div key={slot.role} className="border rounded-lg p-4 bg-gray-50/50">
                                        <div className="mb-3">
                                            <h4 className="font-medium text-sm text-gray-900">{slot.label}</h4>
                                            <p className="text-xs text-gray-500">{slot.desc}</p>
                                        </div>
                                        
                                        {activeImage ? (
                                            <div className="relative aspect-video w-full max-w-md rounded-md overflow-hidden group">
                                                <img src={activeImage.image_url} alt={slot.label} className="w-full h-full object-cover" />
                                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                    <Button 
                                                        type="button" 
                                                        variant="destructive" 
                                                        size="sm"
                                                        onClick={async () => {
                                                            try {
                                                                await apiClient.deleteItineraryImage(activeImage.id);
                                                                setItinerary((prev: any) => ({
                                                                    ...prev,
                                                                    images: prev.images.filter((img: any) => img.id !== activeImage.id)
                                                                }));
                                                                toast.success("Image removed");
                                                            } catch(e) {
                                                                toast.error("Failed to remove image");
                                                            }
                                                        }}
                                                    >
                                                        Remove
                                                    </Button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex gap-3">
                                                 <Button 
                                                    type="button" 
                                                    variant="outline" 
                                                    size="sm"
                                                    onClick={() => {
                                                        // We need a way to know WHICH slot we are selecting for.
                                                        // Using a ref or state would be best. 
                                                        // But safely, we can just Open Gallery, and handle 'onSelect' dynamically?
                                                        // Better: Set a 'targetRole' state.
                                                        setTargetImageRole(slot.role);
                                                        setIsGalleryOpen(true);
                                                    }}
                                                >
                                                    <ImageIcon className="mr-2 h-4 w-4" />
                                                    Library
                                                 </Button>
                                                 <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-3">
                                                     <Upload className="mr-2 h-4 w-4" /> Upload
                                                     <input 
                                                        type="file" 
                                                        className="hidden" 
                                                        accept="image/*"
                                                        onChange={async (e) => {
                                                            const file = e.target.files?.[0];
                                                            if (!file) return;
                                                            
                                                            const loadingId = toast.loading("Uploading...");
                                                            try {
                                                                // Upload
                                                                const newImages = await apiClient.uploadItineraryImages(itinerary.id, [file]);
                                                                const newImage = newImages[0];
                                                                
                                                                // Update Role
                                                                await apiClient.updateItineraryImage(newImage.id, { image_role: slot.role });
                                                                
                                                                // Update State: Remove old image with this role first
                                                                setItinerary((prev: any) => ({
                                                                    ...prev,
                                                                    images: [
                                                                        ...(prev.images || []).filter((i: any) => i.image_role !== slot.role), 
                                                                        { ...newImage, image_role: slot.role }
                                                                    ]
                                                                }));
                                                                
                                                                toast.success("Uploaded", { id: loadingId });
                                                            } catch (err) {
                                                                console.error(err);
                                                                toast.error("Failed to upload", { id: loadingId });
                                                            }
                                                        }}
                                                     />
                                                 </label>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                            
                            {/* Gallery Modal needs to know about targetRole */}
                             <ImageGalleryModal 
                                open={isGalleryOpen} 
                                onOpenChange={(open) => {
                                    setIsGalleryOpen(open);
                                    // if (!open) setTargetImageRole(null); // Keep role for safety until next open
                                }}
                                limit={1} // Single select for slots
                                onSelect={async (selectedImages) => {
                                    if (!targetImageRole) return;
                                    
                                    try {
                                        const img = selectedImages[0];
                                        // Link generic image
                                        // Wait, 'linkItineraryImages' creates a NEW ItineraryImage record from a URL.
                                        // It doesn't allow setting role in creation (yet).
                                        // So we Link -> Then Update Role.
                                        
                                        const linkedImages = await apiClient.linkItineraryImages(itinerary.id, [{
                                            image_url: img.url, 
                                            caption: img.caption
                                        }]);
                                        
                                        const newItineraryImage = linkedImages[0];
                                        
                                        // Update Role
                                        await apiClient.updateItineraryImage(newItineraryImage.id, { image_role: targetImageRole });
                                        
                                        // Update State: Remove old image with this role first
                                        setItinerary((prev: any) => ({
                                            ...prev,
                                            images: [
                                                ...(prev.images || []).filter((i: any) => i.image_role !== targetImageRole), 
                                                { ...newItineraryImage, image_role: targetImageRole }
                                            ]
                                        }));
                                        
                                        toast.success("Image selected");
                                    } catch (e) {
                                        console.error(e);
                                        toast.error("Failed to set image");
                                    }
                                }}
                             />
                        </div>
                    ) : ( 
                        // View Mode - Show images with labels? Or just list them? 
                        // User said "We are going to have a total of 5 images there".
                        // Let's show them in a grid clearly labeled.
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {[
                                { role: 'cover', label: 'Cover Photo' },
                                { role: 'accommodation_end', label: 'After Accommodations' },
                                { role: 'inclusions', label: 'Includes/Excludes Page' },
                                { role: 'about_banner', label: 'About Us Banner' },
                                { role: 'end', label: 'End of Itinerary' }
                            ].map((slot) => {
                                const img = itinerary.images?.find((i: any) => i.image_role === slot.role);
                                if (!img) return null;
                                return (
                                    <div key={slot.role} className="border rounded-lg overflow-hidden">
                                        <div className="bg-gray-50 px-3 py-2 border-b text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            {slot.label}
                                        </div>
                                        <div className="aspect-video relative">
                                            <img src={img.image_url} alt={slot.label} className="w-full h-full object-cover" />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
             </Card>

             {/* Days Editor */}
             <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-bold">Daily Itinerary</h2>
                    {isEditing && (
                        <Button size="sm" onClick={handleAddDay}>
                            <Plus className="mr-2 h-4 w-4" /> Add Day
                        </Button>
                    )}
                </div>
                
                <div className="space-y-4">
                    {[...(itinerary.days || [])].sort((a: any, b: any) => a.day_number - b.day_number).map((day: any, index: number) => (
                        isEditing ? (
                            <DayEditor 
                                key={day.id || `temp-${index}`}
                                index={index}
                                day={day}
                                destinations={destinations}
                                accommodations={accommodations}
                                onChange={handleDayChange}
                                onRemove={() => handleRemoveDay(day.day_number)}
                            />
                        ) : (
                            <Card key={day.id} className="hover:shadow-sm transition-shadow">
                                <CardContent className="pt-6">
                                    <div className="flex justify-between mb-2">
                                        <h3 className="font-bold text-lg text-primary">Day {day.day_number}: {day.day_title}</h3>
                                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                            {day.day_date ? new Date(day.day_date).toLocaleDateString(undefined, {weekday: 'short', month: 'short', day: 'numeric'}) : `Day ${day.day_number}`}
                                        </span>
                                    </div>
                                    <p className="text-gray-700 mb-4 whitespace-pre-line leading-relaxed">{day.description}</p>
                                    
                                    {/* Atmospheric Image */}
                                    {day.atmospheric_image_url && (
                                        <div className="mb-4 rounded-lg overflow-hidden aspect-video relative">
                                            <img 
                                                src={day.atmospheric_image_url} 
                                                alt={day.day_title} 
                                                className="object-cover w-full h-full"
                                            />
                                        </div>
                                    )}

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 bg-gray-50 p-4 rounded-lg border border-gray-100">
                                        {/* Destinations */}
                                        {day.destinations?.length > 0 && (
                                            <div className="md:col-span-2 flex items-start gap-2">
                                                <span className="font-semibold min-w-24">Destinations:</span>
                                                <div className="flex gap-2 flex-wrap">
                                                    {day.destinations.map((d: any) => <Badge key={d.name || d} variant="outline" className="bg-white">{d.name || d}</Badge>)}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {/* Accommodation */}
                                        <div className="flex items-center gap-2">
                                            <Hotel className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <span className="font-semibold mr-1">Stay:</span>
                                                { (typeof day.accommodation === 'object' ? day.accommodation?.name : day.accommodation) || 'Not selected'}
                                            </div>
                                        </div>

                                        {/* Meals */}
                                        <div className="flex items-center gap-2">
                                            <UtensilsCrossed className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <span className="font-semibold mr-1">Meals:</span>
                                                {day.meals_included || 'Not specified'}
                                            </div>
                                        </div>
                                        
                                        {/* Activities */}
                                        {day.activities && (
                                            <div className="md:col-span-2 pt-2 border-t mt-2">
                                                <span className="font-semibold block mb-1 text-xs uppercase text-gray-500">Activities</span>
                                                <p>{day.activities}</p>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        )
                    ))}
                    
                    {(!itinerary.days || itinerary.days.length === 0) && (
                        <div className="text-center py-10 border-2 border-dashed rounded-lg text-gray-400">
                            <p>No days added to this itinerary yet.</p>
                            {isEditing && <Button variant="link" onClick={handleAddDay}>Add the first day</Button>}
                        </div>
                    )}
                </div>
             </div>

             {/* Travelers (Read-Only/Manage via Modal if needed, or inline) */}
             <div className="pt-8 border-t">
                <h3 className="font-bold text-lg mb-4">Travelers</h3>
                <TravelersList 
                    itineraryId={itinerary.id} 
                    travelers={itinerary.travelers || []} 
                    onUpdate={async () => {
                        const { data } = await refetch();
                        if (data) {
                            setItinerary(data);
                        }
                    }} 
                    isEditing={isEditing}
                />
             </div>
        </div>

      </div>
    </div>
  );
}
