'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getItineraryPublic } from '@/lib/api';
import { Loader2, Hotel, CheckCircle2, XCircle, Facebook, Instagram, Twitter, Linkedin } from 'lucide-react';
import toast from 'react-hot-toast';

// Define types locally or import from shared types
interface ItineraryPublicData {
  unique_code: string;
  tour_title: string;
  tour_type?: string;
  accommodation_level?: string;
  hero_image_url?: string;
  duration_days: number;
  duration_nights?: number;
  primary_traveler?: {
    full_name: string;
  };
  welcome_message?: string;
  days?: any[]; // To be typed properly later
  inclusions?: any[];
  exclusions?: any[];
  images?: any[];
  company_about?: string;
  company_badges?: { asset_url: string; asset_name: string }[];
  agent_name?: string;
  agent_position?: string;
  agent_email?: string;
  agent_phone?: string;
  agent_profile_photo_url?: string;
  company_address?: string;
  company_phone?: string;
  company_website?: string;
  company_socials?: Record<string, string>;
  footer_notes?: string;
  review_image_url?: string;
  closing_message?: string;
  logo_url?: string;
  description?: string;
  // Add other fields as needed
}

export default function ClientPresentationView() {
  const params = useParams();
  const [itinerary, setItinerary] = useState<ItineraryPublicData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadItinerary() {
      try {
        if (!params.unique_code) return;
        
        // Use the existing public API which fetches by unique_code
        // Note: verify if getItineraryPublic expects ID or Code. 
        // Based on backend endpoints, public endpoint uses unique_code.
        const data = await getItineraryPublic(params.unique_code as string);
        setItinerary(data);
      } catch (err: any) {
        console.error('Failed to load itinerary:', err);
        setError(err.message || 'Failed to load itinerary');
        toast.error('Failed to load itinerary');
      } finally {
        setLoading(false);
      }
    }

    loadItinerary();
  }, [params.unique_code]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <Loader2 className="h-8 w-8 animate-spin text-white" />
      </div>
    );
  }

  if (error || !itinerary) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Itinerary Not Found</h2>
          <p className="text-gray-400">{error || 'Please check the link and try again.'}</p>
        </div>
      </div>
    );
  }

  // Calculate nights if not provided
  const nights = itinerary.duration_nights !== undefined 
    ? itinerary.duration_nights 
    : (itinerary.duration_days > 0 ? itinerary.duration_days - 1 : 0);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative h-screen w-full">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={itinerary.hero_image_url || '/images/default-hero.jpg'}
          alt={itinerary.tour_title}
          className="w-full h-full object-cover"
        />
          <div className="absolute inset-0 bg-black/40" />
        
        {/* Top Header Bar */}
        <div 
          className="absolute top-0 left-0 right-0 py-2 px-6 flex flex-col md:flex-row justify-between items-center gap-4 z-10 shadow-lg font-sans"
          style={{ background: 'linear-gradient(110deg, #ffffff 30%, #5B7444 30%)' }}
        >
           {/* eslint-disable-next-line @next/next/no-img-element */}
           <img 
              src={itinerary.logo_url || "/Easy-Travel-Logo-Black.webp"} 
              alt="Brand Logo" 
              className="h-24 w-auto p-2 object-contain" 
           />
           <div className="flex flex-wrap justify-end gap-4 md:gap-8 text-white text-sm font-medium text-left">
             <div className="text-left">
               <p className="opacity-80 uppercase text-xs tracking-wider">Tour Type</p>
               <p>{itinerary.tour_type || 'Private Tour'}</p>
             </div>
             <div className="text-left">
               <p className="opacity-80 uppercase text-xs tracking-wider">Tour Length</p>
               <p>{itinerary.duration_days} Days / {nights} Nights</p>
             </div>
             <div className="text-left">
               <p className="opacity-80 uppercase text-xs tracking-wider">Tour Code</p>
               <p>{itinerary.unique_code}</p>
             </div>
             <div className="text-left">
               <p className="opacity-80 uppercase text-xs tracking-wider">Accommodation level</p>
               <p>{itinerary.accommodation_level || 'Comfort'}</p>
             </div>
           </div>
        </div>

        {/* Hero Content */}
        <div className="absolute bottom-20 left-6 md:left-20 text-white max-w-4xl z-10">
           <h1 className="text-5xl md:text-7xl font-bold mb-4 font-serif leading-tight">{itinerary.tour_title}</h1>
           <p className="text-xl md:text-2xl font-light italic opacity-90 font-sans">
             {itinerary.description || `A Private Family Safari Curated for ${itinerary.primary_traveler?.full_name ? `the ${itinerary.primary_traveler.full_name.split(' ').pop()} Family` : 'You'}`}
           </p>
        </div>
        
        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce z-10">
          <div className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center">
            <div className="w-1 h-2 bg-white rounded-full mt-2" />
          </div>
        </div>
      </div>

      {/* Welcome Letter Section */}
      <div className="container mx-auto px-4 py-16 md:py-24 max-w-4xl">
         <div className="prose prose-lg mx-auto text-gray-700 leading-relaxed font-sans tracking-wide">
            {itinerary.welcome_message ? (
              <div className="whitespace-pre-wrap">{itinerary.welcome_message}</div>
            ) : (
              <p>Welcome to your itinerary.</p>
            )}
            
            <div className="mt-12 flex items-center gap-6 not-prose">
               <div className="h-28 w-28 bg-gray-200 overflow-hidden flex-shrink-0 border-2 border-white shadow-sm">
                 {itinerary.agent_profile_photo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={itinerary.agent_profile_photo_url} alt="Agent" className="h-full w-full object-cover" />
                 ) : (
                    <div className="h-full w-full bg-primary/10 flex items-center justify-center text-primary font-bold text-2xl">
                        {itinerary.agent_name ? itinerary.agent_name.charAt(0) : 'A'}
                    </div>
                 )}
               </div>
               <div className="flex flex-col gap-1.5">
                  <p className="font-bold text-gray-900 text-lg font-sans leading-none">Easy Travel Tanzania</p>
                  <p className="text-gray-600 text-sm font-sans leading-none">+ 255 786 400 148</p>
                  <p className="text-gray-900 text-sm font-sans leading-none">{itinerary.agent_email || 'info@easytravel.co.tz'}</p>
               </div>
            </div>
         </div>
      </div>
      {/* ITINERARY Section (Journal Style) */}
      <div className="bg-white py-24 min-h-screen w-full">
        <div className="w-full">
          <div className="space-y-0">
            {itinerary.days && itinerary.days.map((day: any, index: number) => (
              <div key={day.id} className="flex flex-col md:flex-row border-b border-gray-100 last:border-b-0 w-full">
                
                {/* Left Column (Image) - 40% + 100px */}
                <div className="md:w-[calc(40%+100px)] relative min-h-[400px] md:min-h-full">
                  <div className="relative h-full w-full">
                     {day.atmospheric_image_url || (day.destinations?.[0]?.images?.[0]?.image_url) ? (
                       // eslint-disable-next-line @next/next/no-img-element
                       <img 
                         src={day.atmospheric_image_url || day.destinations?.[0]?.images?.[0]?.image_url} 
                         alt={day.title}
                         className="w-full h-full object-cover"
                       />
                     ) : (
                       <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                         <p className="text-gray-400 font-serif italic text-lg">Journey</p>
                       </div>
                     )}
                  </div>
                </div>

                {/* Right Column (Content) - 60% - 100px */}
                <div className="md:w-[calc(60%-100px)] bg-white p-8 md:pl-24 md:pr-16 md:py-[100px] flex flex-col justify-center">
                   <div className="w-full">
                      {/* ITINERARY Heading - Only on Day 1 */}
                      {index === 0 && (
                          <h2 className="text-4xl font-sans text-[#5B7444] tracking-widest mb-10">Itinerary</h2>
                      )}

                      {/* Day Header */}
                      <div className="mb-10 border-l-4 border-primary pl-6">
                         <h3 className="text-3xl font-sans font-bold text-gray-900 mb-3">
                           Day {day.day_number}
                           {day.day_number === 1 ? (
                              <span className="font-light text-gray-600 block mt-2 text-xl font-sans">Arrival Day: {day.destinations?.map((d: any) => d.name).join(' - ') || 'Arrival'}</span>
                           ) : (
                              <span className="font-light text-gray-600 block mt-2 text-xl font-sans">
                                 {day.destinations && day.destinations.length > 0 
                                   ? day.destinations.map((d: any) => d.name).join(' - ')
                                   : (day.title || 'Leisure Day')}
                              </span>
                           )}
                         </h3>
                      </div>
                      
                      {/* Description */}
                      <div className="prose prose-lg text-gray-600 mb-12 max-w-none text-justify leading-relaxed font-sans">
                        <p>{day.description}</p>
                      </div>

                      {/* Stay & Meals - Plain Text */}
                      <div className="mb-8 space-y-2 text-gray-700 font-sans text-lg">
                        {day.accommodation && (
                          <div className="flex gap-2">
                            <span className="font-bold">Overnight At:</span>
                            <span>{day.accommodation.name}</span>
                          </div>
                        )}
                        {day.meals_included && (
                          <div className="flex gap-2">
                            <span className="font-bold">Meal Plan:</span>
                            <span>{day.meals_included}</span>
                          </div>
                        )}
                      </div>

                      {/* activities */}
                      {day.activities && (
                         <div className="mb-12">
                            <h4 className="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4 font-sans">Today's Activities</h4>
                            <div className="prose text-gray-700 font-medium font-sans">
                               <p>{day.activities}</p>
                            </div>
                         </div>
                      )}
                   </div>
                </div>

              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Accommodations Section */}
      <div className="bg-white pt-24 pb-0 w-full">
        <h2 className="text-4xl font-sans text-center mb-16 text-gray-900 tracking-widest">ACCOMMODATIONS</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 w-full">
          {Object.values(
             (itinerary.days || []).reduce((acc: any, day: any) => {
               if (day.accommodation) {
                 if (!acc[day.accommodation.id]) {
                   acc[day.accommodation.id] = {
                     details: day.accommodation,
                     nights: 0
                   };
                 }
                 acc[day.accommodation.id].nights += 1;
               }
               return acc;
             }, {})
           ).map((item: any) => {
             // Get first two images, or fallback if not enough
             const images = item.details.images && item.details.images.length > 0 
               ? item.details.images 
               : [];
             
             const image1Url = images.length > 0 ? (images.find((img: any) => img.is_primary)?.image_url || images[0].image_url) : null;
             // Try to find a second image that isn't the primary one, or just the second in list
             const image2Url = images.length > 1 ? images[1].image_url : image1Url; // Fallback to same image if only 1 exists

             return (
               <div key={item.details.id} className="relative w-full h-[500px] flex group col-span-1 md:col-span-2">
                  {/* Image 1 (Left Half) */}
                  <div className="w-1/2 h-full relative overflow-hidden border-r border-white/10">
                    {image1Url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img 
                        src={image1Url} 
                        alt={`${item.details.name} 1`}
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                        <Hotel className="w-12 h-12 text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* Image 2 (Right Half) */}
                  <div className="w-1/2 h-full relative overflow-hidden">
                    {image2Url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img 
                        src={image2Url} 
                        alt={`${item.details.name} 2`}
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                        <Hotel className="w-12 h-12 text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* Unified Centered Overlay */}
                  <div className="absolute bottom-0 left-0 w-full h-[120px] bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-end justify-center pb-8 z-10 pointer-events-none">
                     <div className="flex items-center gap-3 text-white font-sans">
                        <span className="uppercase tracking-widest text-sm font-medium">{item.details.name}</span>
                        <span className="w-1 h-1 bg-white rounded-full opacity-50"></span>
                        <span className="uppercase tracking-widest text-sm font-medium text-white/80">
                           {item.nights} {item.nights === 1 ? 'Night' : 'Nights'} Stay
                        </span>
                     </div>
                  </div>
               </div>
             );
           })}
        </div>
      </div>

      {/* After Accommodation Image Section */}
      {(() => {
         // Try to find image with role 'accommodation_end' or 'ACCOMMODATION_END'
         // Also check for 'cover' if that was intended, but user said "Images > After Accommodation"
         // The backend model comment says: "Role of the image: cover, accommodation_end, inclusions, about_banner, end"
         const afterAccImage = itinerary.images?.find((img: any) => 
            img.image_role === 'accommodation_end' || img.image_role === 'ACCOMMODATION_END'
         );
         
         if (!afterAccImage) return null;

         return (
            <div className="w-full h-[700px] relative">
               {/* eslint-disable-next-line @next/next/no-img-element */}
               <img 
                  src={afterAccImage.image_url} 
                  alt="Accommodation Details" 
                  className="w-full h-full object-cover"
               />
            </div>
         );
      })()}

      {/* Inclusions & Exclusions Section */}
      <div className="bg-gray-50 py-24 w-full">
        <div className="container mx-auto px-4 max-w-7xl space-y-32">
            
            {/* Inclusions */}
            {itinerary.inclusions && itinerary.inclusions.length > 0 && (
                <div className="mb-12">
                    <h2 className="text-3xl font-sans text-center mb-16 text-gray-900 tracking-widest uppercase">What's Included</h2>
                     <div className="flex flex-wrap justify-center gap-y-[80px] gap-x-[550px]">
                         {itinerary.inclusions.map((item: any, idx: number) => (
                             <div key={idx} className="w-full md:w-[calc(50%-275px)] flex flex-row gap-6 items-start justify-center text-left">
                                 <div className="flex-shrink-0 mt-1">
                                    {item.image_url ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img 
                                            src={item.image_url} 
                                            alt={item.name} 
                                            className="h-12 w-12 object-cover rounded-md shadow-sm border border-gray-100" 
                                        />
                                    ) : (
                                        <CheckCircle2 className="h-6 w-6 text-green-600" />
                                    )}
                                 </div>
                                 <div className="max-w-xs font-sans">
                                     <h3 className="font-bold text-lg text-gray-900 mb-1">{item.name}</h3>
                                     {item.description && (
                                         <p className="text-gray-600 text-sm leading-relaxed">{item.description}</p>
                                     )}
                                 </div>
                             </div>
                         ))}
                    </div>
                </div>
            )}

            {/* Exclusions */}
            {itinerary.exclusions && itinerary.exclusions.length > 0 && (
                <div>
                     <h2 className="text-3xl font-sans text-center mb-16 text-gray-900 tracking-widest uppercase">What's Excluded</h2>
                     <div className="flex flex-wrap justify-center gap-y-[80px] gap-x-[550px]">
                         {itinerary.exclusions.map((item: any, idx: number) => (
                             <div key={idx} className="w-full md:w-[calc(50%-275px)] flex flex-row gap-6 items-start justify-center text-left">
                                 <div className="flex-shrink-0 mt-1">
                                    {item.image_url ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img 
                                            src={item.image_url} 
                                            alt={item.name} 
                                            className="h-12 w-12 object-cover rounded-md shadow-sm border border-gray-100" 
                                        />
                                    ) : (
                                        <XCircle className="h-6 w-6 text-red-500" />
                                    )}
                                 </div>
                                 <div className="max-w-xs font-sans">
                                     <h3 className="font-bold text-lg text-gray-900 mb-1">{item.name}</h3>
                                     {item.description && (
                                         <p className="text-gray-600 text-sm leading-relaxed">{item.description}</p>
                                     )}
                                 </div>
                             </div>
                         ))}
                    </div>
                </div>
            )}
        </div>
      </div>

      {/* Inclusions Page Image Section */}
      {(() => {
         const inclusionsImage = itinerary.images?.find((img: any) => 
            img.image_role === 'inclusions'
         );
         
         if (!inclusionsImage) return null;

         return (
            <div className="w-full h-[700px] relative">
               {/* eslint-disable-next-line @next/next/no-img-element */}
               <img 
                  src={inclusionsImage.image_url} 
                  alt="Inclusions" 
                  className="w-full h-full object-cover"
               />
            </div>
         );
      })()}
      {/* About Us Banner Section */}
      {(() => {
         const aboutImage = itinerary.images?.find((img: any) => 
            img.image_role === 'about_banner'
         );
         
         if (!aboutImage) return null;

         return (
            <div className="w-full pb-32 bg-white"> 
                <div className="mx-4 md:mx-[125px] mt-[125px] relative">
                   <div className="w-full h-[600px] relative">
                       {/* eslint-disable-next-line @next/next/no-img-element */}
                       <img 
                          src={aboutImage.image_url} 
                          alt="About Easy Travel" 
                          className="w-full h-full object-cover"
                       />
                       
                       {/* Overlay Box: Half on image, half below */}
                       <div className="absolute bottom-0 right-0 translate-y-1/2 bg-[#5B7444] text-white px-8 py-6 mr-0 shadow-lg whitespace-nowrap">
                           <h3 className="text-5xl font-sans tracking-widest uppercase mb-0">ABOUT EASY TRAVEL</h3>
                       </div>
                   </div>
                </div>

                {/* About Content Text */}
                {itinerary.company_about && (
                    <div className="mx-auto mt-[100px] max-w-4xl px-4">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-line text-lg font-sans">
                            {itinerary.company_about}
                        </p>
                    </div>
                )}

                {/* Award Badges */}
                {itinerary.company_badges && itinerary.company_badges.length > 0 && (
                    <div className="mx-auto mt-16 mb-32 flex flex-wrap justify-center gap-12 items-center px-4">
                        {itinerary.company_badges.map((badge, index) => (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img 
                                key={index} 
                                src={badge.asset_url} 
                                alt={badge.asset_name || 'Award Badge'} 
                                className="h-48 w-auto object-contain opacity-90 hover:opacity-100 transition-opacity"
                            />
                        ))}
                    </div>
                )}
            </div>
         );
      })()}

      {/* End of Itinerary Image */}
      {(() => {
         const endImage = itinerary.images?.find((img: any) => img.image_role === 'end');
         if (!endImage) return null;

         return (
             <div className="w-full h-[600px]">
                 {/* eslint-disable-next-line @next/next/no-img-element */}
                 <img 
                     src={endImage.image_url} 
                     alt="End of Itinerary" 
                     className="w-full h-full object-cover"
                 />
             </div>
         );
      })()}

      {/* Final Closing Message */}
      {itinerary.closing_message && (
        <div className="py-24 bg-white">
            <div className="container mx-auto px-4 text-center max-w-4xl">
                <p className="text-xl md:text-2xl font-serif italic text-gray-800 leading-relaxed whitespace-pre-line">
                    {itinerary.closing_message}
                </p>
            </div>
        </div>
      )}
      {/* Footer Section - Contact & Branding */}
      <div className="pt-24 pb-10" style={{ backgroundColor: '#EFE9E6' }}>
         <div className="container mx-auto px-4 max-w-6xl">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
                
                {/* Left Side (Agent & Company) - 70% approx (8 cols) */}
                <div className="md:col-span-8 flex flex-col md:flex-row items-center md:items-start gap-8 md:gap-12 relative">
                    {/* Agent Image */}
                    <div className="flex-shrink-0">
                        <div className="h-40 w-40 bg-gray-200 overflow-hidden shadow-md">
                            {itinerary.agent_profile_photo_url ? (
                                // eslint-disable-next-line @next/next/no-img-element
                                <img src={itinerary.agent_profile_photo_url} alt="Agent" className="h-full w-full object-cover" />
                            ) : (
                                <div className="h-full w-full bg-[#5B7444] flex items-center justify-center text-white font-bold text-4xl">
                                    {itinerary.agent_name ? itinerary.agent_name.charAt(0) : 'A'}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Agent & Company Details */}
                    <div className="flex flex-col text-center md:text-left space-y-4 font-sans text-gray-800">
                        <div>
                            <h3 className="text-2xl font-bold mb-1">{itinerary.agent_name || 'Travel Consultant'}</h3>
                            <p className="text-sm tracking-wide uppercase text-gray-500">{itinerary.agent_position || 'Travel Consultant'}</p>
                        </div>

                        <div className="space-y-1 text-lg leading-relaxed">
                            {itinerary.agent_phone && (
                                <p><span className="font-bold mr-2">M:</span> {itinerary.agent_phone}</p>
                            )}
                            <p><span className="font-bold mr-2">E:</span> {itinerary.agent_email || 'info@easytravel.co.tz'}</p>
                            {itinerary.company_address && (
                                <div className="flex">
                                    <span className="font-bold mr-2 flex-shrink-0">A:</span> 
                                    <span className="max-w-[250px]">{itinerary.company_address}</span>
                                </div>
                            )}
                            
                            {/* Social Media Icons */}
                            {itinerary.company_socials && (
                                <div className="flex mt-3">
                                    <span className="font-bold mr-2 flex-shrink-0 opacity-0 select-none">A:</span>
                                    <div className="flex gap-2 justify-center md:justify-start">
                                        {itinerary.company_socials.facebook && (
                                            <a href={itinerary.company_socials.facebook} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors" title="Facebook">
                                                <Facebook className="h-4 w-4" />
                                            </a>
                                        )}
                                        {itinerary.company_socials.instagram && (
                                            <a href={itinerary.company_socials.instagram} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors" title="Instagram">
                                                <Instagram className="h-4 w-4" />
                                            </a>
                                        )}
                                        {itinerary.company_socials.twitter && (
                                            <a href={itinerary.company_socials.twitter} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors" title="Twitter">
                                                <Twitter className="h-4 w-4" />
                                            </a>
                                        )}
                                        {itinerary.company_socials.linkedin && (
                                            <a href={itinerary.company_socials.linkedin} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors" title="LinkedIn">
                                                <Linkedin className="h-4 w-4" />
                                            </a>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    
                    {/* Vertical Divider - Only on desktop */}
                    <div className="hidden md:block absolute right-[-24px] top-0 bottom-0 w-[1px] bg-[#5B7444] h-full opacity-50"></div>
                </div>

                {/* Right Side (Review Image) - 30% approx (4 cols) */}
                <div className="md:col-span-4 flex justify-center md:justify-center">
                    {itinerary.review_image_url ? (
                         // eslint-disable-next-line @next/next/no-img-element
                         <img src={itinerary.review_image_url} alt="Review / Testimonial" className="max-h-[320px] max-w-full object-contain" />
                    ) : (
                        <div className="h-32 w-full bg-gray-100/50 border-2 border-dashed border-gray-300 rounded flex items-center justify-center text-gray-400 text-sm">
                            No Review Image Set
                        </div>
                    )}
                </div>

            </div>
            
            {/* Footer Notes */}
            {itinerary.footer_notes && (
                <div className="mt-16 pt-8 border-t border-gray-300 text-center text-sm text-gray-500 font-sans whitespace-pre-line">
                    {itinerary.footer_notes}
                </div>
            )}
         </div>
      </div>


      
      {/* PDF Button Removed */}

    </div>
  );
}
