'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getItineraryPublic } from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import { Loader2, Hotel, CheckCircle2, XCircle, Facebook, Instagram, Twitter, Linkedin } from 'lucide-react';
import toast from 'react-hot-toast';

// Default style values — mirrors the defaults in the settings page
const DEFAULT_STYLES: Record<string, string> = {
  global_sans:          'system-ui, sans-serif',
  global_serif:         'Georgia, serif',
  hero_title_size:      '56',
  hero_title_weight:    '700',
  hero_title_family:    'serif',
  hero_desc_size:       '20',
  hero_desc_weight:     '300',
  heading_size:         '48',
  heading_weight:       '600',
  heading_spacing:      '0.2em',
  day_title_size:       '22',
  day_title_weight:     '600',
  day_desc_size:        '16',
  day_label_size:       '16',
  day_label_weight:     '700',
  day_padding_x:        '96',
  day_padding_y:        '100',
  inc_title_size:       '20',
  inc_title_weight:     '700',
  inc_desc_size:        '16',
  inc_row_gap:          '80',
  inc_col_gap:          '450',
  welcome_size:         '16',
  contact_name_size:    '16',
  contact_name_weight:  '700',
  closing_size:         '20',
  footer_name_size:     '20',
  footer_name_weight:   '700',
  footer_position_size: '14',
  footer_padding_top:   '96',
};

// Default page labels (used as fallback while loading or on error)
const DEFAULT_LABELS: Record<string, string> = {
  page_heading_itinerary:        'Itinerary',
  page_heading_accommodations:   'ACCOMMODATIONS',
  page_heading_whats_included:   "What's Included",
  page_heading_whats_excluded:   "What's Excluded",
  page_heading_about:            'ABOUT EASY TRAVEL',
  page_label_overnight_at:       'Overnight At:',
  page_label_meal_plan:          'Meal Plan:',
  page_label_todays_activities:  "Today's Activities",
  page_contact_company_name:     'Easy Travel Tanzania',
  page_contact_company_phone:    '+ 255 786 400 148',
  page_contact_fallback_email:   'info@easytravel.co.tz',
  page_color_primary:            '#5B7444',
  page_color_exclusions:         '#c25d2a',
  page_footer_bg_color:          '#EFE9E6',
};

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
}

export default function ClientPresentationView() {
  const params = useParams();
  const [itinerary, setItinerary] = useState<ItineraryPublicData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [labels, setLabels] = useState<Record<string, string>>(DEFAULT_LABELS);
  const [pageStyles, setPageStyles] = useState<Record<string, string>>(DEFAULT_STYLES);

  // Helper: get a label with its default fallback
  const lbl = (key: string) => labels[key] || DEFAULT_LABELS[key] || key;
  // Helpers for styles
  const sty = (key: string) => pageStyles[key] || DEFAULT_STYLES[key] || '';
  const px  = (key: string) => `${sty(key)}px`;
  // Resolve font family shorthand to actual CSS value
  const ff  = (key: string) => sty(key) === 'serif' ? sty('global_serif') : sty('global_sans');

  useEffect(() => {
    async function loadItinerary() {
      try {
        if (!params.unique_code) return;
        const [data, pageLabels, rawStyles] = await Promise.all([
          getItineraryPublic(params.unique_code as string),
          apiClient.getPageLabels().catch(() => DEFAULT_LABELS),
          apiClient.getPageStyles().catch(() => ({})),
        ]);
        setItinerary(data);
        setLabels({ ...DEFAULT_LABELS, ...pageLabels });
        setPageStyles({ ...DEFAULT_STYLES, ...rawStyles });
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

  const nights = itinerary.duration_nights !== undefined
    ? itinerary.duration_nights
    : (itinerary.duration_days > 0 ? itinerary.duration_days - 1 : 0);

  return (
    <div className="min-h-screen bg-white">

      {/* ── Hero Section ──────────────────────────────────────────── */}
      <div className="relative h-screen w-full">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={itinerary.hero_image_url || '/images/default-hero.jpg'}
          alt={itinerary.tour_title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />

        {/* Top Header Bar — white on mobile, diagonal gradient on desktop */}
        <div className="absolute top-0 left-0 right-0 py-2 px-4 md:px-6 flex flex-col md:flex-row justify-between items-center gap-2 md:gap-4 z-10 shadow-lg font-sans bg-white md:bg-transparent md:[background:linear-gradient(110deg,#ffffff_30%,#5B7444_30%)]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={itinerary.logo_url || "/Easy-Travel-Logo-Black.webp"}
            alt="Brand Logo"
            className="h-14 md:h-24 w-auto p-1 md:p-2 object-contain"
          />
          <div className="flex flex-wrap justify-center md:justify-end gap-3 md:gap-8 text-sm font-medium w-full md:w-auto pb-2 md:pb-0">
            <div className="text-center md:text-left">
              <p className="text-gray-500 md:text-white md:opacity-80 uppercase text-xs tracking-wider">Tour Type</p>
              <p className="text-gray-800 md:text-white">{itinerary.tour_type || 'Private Tour'}</p>
            </div>
            <div className="text-center md:text-left">
              <p className="text-gray-500 md:text-white md:opacity-80 uppercase text-xs tracking-wider">Tour Length</p>
              <p className="text-gray-800 md:text-white">{itinerary.duration_days} Days / {nights} Nights</p>
            </div>
            <div className="text-center md:text-left">
              <p className="text-gray-500 md:text-white md:opacity-80 uppercase text-xs tracking-wider">Tour Code</p>
              <p className="text-gray-800 md:text-white">{itinerary.unique_code}</p>
            </div>
            <div className="text-center md:text-left">
              <p className="text-gray-500 md:text-white md:opacity-80 uppercase text-xs tracking-wider">Accommodation level</p>
              <p className="text-gray-800 md:text-white">{itinerary.accommodation_level || 'Comfort'}</p>
            </div>
          </div>
        </div>

        {/* Hero Content */}
        <div className="absolute bottom-16 md:bottom-20 left-4 md:left-20 text-white max-w-[90vw] md:max-w-4xl z-10 pr-4">
          <h1 className="mb-3 md:mb-4 leading-tight" style={{ fontSize: px('hero_title_size'), fontWeight: sty('hero_title_weight'), fontFamily: ff('hero_title_family') }}>{itinerary.tour_title}</h1>
          <p className="italic opacity-90" style={{ fontSize: px('hero_desc_size'), fontWeight: sty('hero_desc_weight'), fontFamily: sty('global_sans') }}>
            {itinerary.description || `A Private Family Safari Curated for ${itinerary.primary_traveler?.full_name ? `the ${itinerary.primary_traveler.full_name.split(' ').pop()} Family` : 'You'}`}
          </p>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-6 md:bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce z-10">
          <div className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center">
            <div className="w-1 h-2 bg-white rounded-full mt-2" />
          </div>
        </div>
      </div>

      {/* ── Welcome Letter ────────────────────────────────────────── */}
      <div className="container mx-auto px-4 py-12 md:py-24 max-w-4xl">
        <div className="prose mx-auto text-gray-700 leading-relaxed font-sans tracking-wide" style={{ fontSize: px('welcome_size') }}>
          {itinerary.welcome_message ? (
            <div className="whitespace-pre-wrap">{itinerary.welcome_message}</div>
          ) : (
            <p>Welcome to your itinerary.</p>
          )}

          <div className="mt-10 md:mt-12 flex items-center gap-4 md:gap-6 not-prose">
            <div className="h-20 w-20 md:h-28 md:w-28 bg-gray-200 overflow-hidden flex-shrink-0 border-2 border-white shadow-sm">
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
              <p className="text-gray-900 font-sans leading-none" style={{ fontSize: px('contact_name_size'), fontWeight: sty('contact_name_weight') }}>{lbl('page_contact_company_name')}</p>
              <p className="text-gray-600 font-sans leading-none" style={{ fontSize: px('contact_name_size') }}>{lbl('page_contact_company_phone')}</p>
              <p className="text-gray-900 font-sans leading-none" style={{ fontSize: px('contact_name_size') }}>{itinerary.agent_email || lbl('page_contact_fallback_email')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Day-by-Day Itinerary (Journal Style) ─────────────────── */}
      <div className="bg-white py-12 md:py-24 w-full">
        <div className="w-full">
          <div className="space-y-0">
            {itinerary.days && itinerary.days.map((day: any, index: number) => (
              <div key={day.id} className="flex flex-col md:flex-row border-b border-gray-100 last:border-b-0 w-full">

                {/* Left Column — image */}
                <div className="md:w-[calc(40%+100px)] relative min-h-[280px] md:min-h-[956px]">
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

                {/* Right Column — content */}
                <div className="md:w-[calc(60%-100px)] bg-white flex flex-col justify-center p-6" style={{ paddingLeft: `${sty('day_padding_x')}px`, paddingRight: `${Math.round(Number(sty('day_padding_x')) * 0.67)}px`, paddingTop: px('day_padding_y'), paddingBottom: px('day_padding_y') }}>
                  <div className="w-full">
                    {/* ITINERARY heading — only Day 1 */}
                    {index === 0 && (
                      <h2 className="mb-8 md:mb-10" style={{ color: lbl('page_color_primary'), fontSize: px('heading_size'), fontWeight: sty('heading_weight'), letterSpacing: sty('heading_spacing'), fontFamily: sty('global_sans') }}>{lbl('page_heading_itinerary')}</h2>
                    )}

                    {/* Day Header */}
                    <div className="mb-6 md:mb-10">
                      <h3 className="text-gray-900 mb-3" style={{ fontSize: px('day_title_size'), fontWeight: sty('day_title_weight'), fontFamily: sty('global_sans') }}>
                        Day {day.day_number}
                        <span className="text-gray-600 block mt-2" style={{ fontSize: px('day_title_size'), fontWeight: sty('day_title_weight'), fontFamily: sty('global_sans') }}>
                          {day.destinations && day.destinations.length > 0
                            ? day.destinations.map((d: any) => d.name).join(' - ')
                            : (day.title || 'Leisure Day')}
                        </span>
                      </h3>
                    </div>

                    {/* Description */}
                    <div className="prose text-gray-600 mb-4 max-w-none text-justify leading-relaxed font-sans" style={{ fontSize: px('day_desc_size') }}>
                      <p>{day.description}</p>
                    </div>

                    {/* Stay & Meals */}
                    <div className="mb-6 md:mb-8 space-y-1 text-gray-700 font-sans" style={{ fontSize: px('day_label_size') }}>
                      {day.accommodation && (
                        <div className="flex gap-2">
                          <span style={{ fontWeight: sty('day_label_weight') }}>{lbl('page_label_overnight_at')}</span>
                          <span>{day.accommodation.name}</span>
                        </div>
                      )}
                      {day.meals_included && (
                        <div className="flex gap-2">
                          <span style={{ fontWeight: sty('day_label_weight') }}>{lbl('page_label_meal_plan')}</span>
                          <span>{day.meals_included}</span>
                        </div>
                      )}
                    </div>

                    {/* Activities */}
                    {day.activities && (
                      <div className="mb-10 md:mb-12">
                        <h4 className="uppercase tracking-widest text-gray-400 mb-3 md:mb-4 font-sans" style={{ fontSize: px('day_label_size'), fontWeight: sty('day_label_weight') }}>{lbl('page_label_todays_activities')}</h4>
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

      {/* ── Accommodations Section ────────────────────────────────── */}
      <div className="bg-white pt-12 md:pt-24 pb-0 w-full">
        <h2 className="text-center mb-8 md:mb-16" style={{ color: lbl('page_color_primary'), fontSize: px('heading_size'), fontWeight: sty('heading_weight'), letterSpacing: sty('heading_spacing'), fontFamily: sty('global_sans') }}>{lbl('page_heading_accommodations')}</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 w-full">
          {Object.values(
            (itinerary.days || []).reduce((acc: any, day: any) => {
              if (day.accommodation) {
                if (!acc[day.accommodation.id]) {
                  acc[day.accommodation.id] = { details: day.accommodation, nights: 0 };
                }
                acc[day.accommodation.id].nights += 1;
              }
              return acc;
            }, {})
          ).map((item: any) => {
            const images = item.details.images && item.details.images.length > 0 ? item.details.images : [];
            const image1Url = images.length > 0 ? (images.find((img: any) => img.is_primary)?.image_url || images[0].image_url) : null;
            const image2Url = images.length > 1 ? images[1].image_url : image1Url;

            return (
              <div key={item.details.id} className="relative w-full h-[220px] md:h-[500px] flex group col-span-1 md:col-span-2">
                {/* Image 1 */}
                <div className="w-1/2 h-full relative overflow-hidden border-r border-white/10">
                  {image1Url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={image1Url} alt={`${item.details.name} 1`} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <Hotel className="w-8 h-8 md:w-12 md:h-12 text-gray-400" />
                    </div>
                  )}
                </div>
                {/* Image 2 */}
                <div className="w-1/2 h-full relative overflow-hidden">
                  {image2Url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={image2Url} alt={`${item.details.name} 2`} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <Hotel className="w-8 h-8 md:w-12 md:h-12 text-gray-400" />
                    </div>
                  )}
                </div>
                {/* Overlay */}
                <div className="absolute bottom-0 left-0 w-full h-[80px] md:h-[120px] bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-end justify-center pb-4 md:pb-8 z-10 pointer-events-none">
                  <div className="flex items-center gap-2 md:gap-3 text-white font-sans">
                    <span className="uppercase tracking-widest text-xs md:text-sm font-medium">{item.details.name}</span>
                    <span className="w-1 h-1 bg-white rounded-full opacity-50"></span>
                    <span className="uppercase tracking-widest text-xs md:text-sm font-medium text-white/80">
                      {item.nights} {item.nights === 1 ? 'Night' : 'Nights'} Stay
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── After Accommodation Image ─────────────────────────────── */}
      {(() => {
        const afterAccImage = itinerary.images?.find((img: any) =>
          img.image_role === 'accommodation_end' || img.image_role === 'ACCOMMODATION_END'
        );
        if (!afterAccImage) return null;
        return (
          <div className="w-full h-[220px] md:h-[700px] relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={afterAccImage.image_url} alt="Accommodation Details" className="w-full h-full object-cover" />
          </div>
        );
      })()}

      {/* ── Inclusions & Exclusions ───────────────────────────────── */}
      <div className="bg-gray-50 py-12 md:py-24 w-full">
        <div className="container mx-auto px-4 max-w-7xl space-y-16 md:space-y-32">

          {/* Inclusions */}
          {itinerary.inclusions && itinerary.inclusions.length > 0 && (
            <div className="mb-8 md:mb-12">
              <h2 className="text-center mb-8 md:mb-16 uppercase" style={{ color: lbl('page_color_primary'), fontSize: px('heading_size'), fontWeight: sty('heading_weight'), letterSpacing: sty('heading_spacing'), fontFamily: sty('global_sans') }}>{lbl('page_heading_whats_included')}</h2>
              <div className="flex flex-wrap justify-start" style={{ rowGap: px('inc_row_gap'), columnGap: px('inc_col_gap') }}>
                {itinerary.inclusions.map((item: any, idx: number) => (
                  <div key={idx} className="w-full md:w-[calc(50%-225px)] flex flex-row gap-4 md:gap-6 items-start text-left">
                    <div className="flex-shrink-0 mt-1">
                      {item.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={item.image_url} alt={item.name} className="h-[44px] w-[44px] md:h-[58px] md:w-[58px] object-cover rounded-md shadow-sm border border-gray-100" />
                      ) : (
                        <CheckCircle2 className="h-[28px] w-[28px] md:h-[34px] md:w-[34px] text-green-600" />
                      )}
                    </div>
                    <div className="max-w-full md:max-w-[350px] font-sans">
                      <h3 className="text-gray-900 mb-1" style={{ fontSize: px('inc_title_size'), fontWeight: sty('inc_title_weight') }}>{item.name}</h3>
                      {item.description && (
                        <p className="text-gray-600 leading-relaxed" style={{ fontSize: px('inc_desc_size') }}>{item.description}</p>
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
              <h2 className="text-center mb-8 md:mb-16 uppercase" style={{ color: lbl('page_color_exclusions'), fontSize: px('heading_size'), fontWeight: sty('heading_weight'), letterSpacing: sty('heading_spacing'), fontFamily: sty('global_sans') }}>{lbl('page_heading_whats_excluded')}</h2>
              <div className="flex flex-wrap justify-start" style={{ rowGap: px('inc_row_gap'), columnGap: px('inc_col_gap') }}>
                {itinerary.exclusions.map((item: any, idx: number) => (
                  <div key={idx} className="w-full md:w-[calc(50%-225px)] flex flex-row gap-4 md:gap-6 items-start text-left">
                    <div className="flex-shrink-0 mt-1">
                      {item.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={item.image_url} alt={item.name} className="h-[44px] w-[44px] md:h-[58px] md:w-[58px] object-cover rounded-md shadow-sm border border-gray-100" />
                      ) : (
                        <XCircle className="h-[28px] w-[28px] md:h-[34px] md:w-[34px] text-red-500" />
                      )}
                    </div>
                    <div className="max-w-full md:max-w-[350px] font-sans">
                      <h3 className="text-gray-900 mb-1" style={{ fontSize: px('inc_title_size'), fontWeight: sty('inc_title_weight') }}>{item.name}</h3>
                      {item.description && (
                        <p className="text-gray-600 leading-relaxed" style={{ fontSize: px('inc_desc_size') }}>{item.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Inclusions Banner Image ───────────────────────────────── */}
      {(() => {
        const inclusionsImage = itinerary.images?.find((img: any) => img.image_role === 'inclusions');
        if (!inclusionsImage) return null;
        return (
          <div className="w-full h-[220px] md:h-[700px] relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={inclusionsImage.image_url} alt="Inclusions" className="w-full h-full object-cover" />
          </div>
        );
      })()}

      {/* ── About Us Section ──────────────────────────────────────── */}
      {(() => {
        const aboutImage = itinerary.images?.find((img: any) => img.image_role === 'about_banner');
        if (!aboutImage) return null;
        return (
          <div className="w-full pb-16 md:pb-32 bg-white">
            <div className="mx-4 md:mx-[125px] mt-12 md:mt-[125px] relative">
              <div className="w-full h-[220px] md:h-[600px] relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={aboutImage.image_url} alt="About Easy Travel" className="w-full h-full object-cover" />

                {/* Overlay heading box */}
                <div className="absolute bottom-0 right-0 translate-y-1/2 text-white px-4 py-3 md:px-8 md:py-6 shadow-lg" style={{ backgroundColor: lbl('page_color_primary') }}>
                  <h3 className="uppercase" style={{ fontSize: px('heading_size'), fontWeight: sty('heading_weight'), letterSpacing: sty('heading_spacing'), fontFamily: sty('global_sans') }}>{lbl('page_heading_about')}</h3>
                </div>
              </div>
            </div>

            {/* About Content */}
            {itinerary.company_about && (
              <div className="mx-auto mt-16 md:mt-[100px] max-w-4xl px-4">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line text-base md:text-lg font-sans">
                  {itinerary.company_about}
                </p>
              </div>
            )}

            {/* Award Badges */}
            {itinerary.company_badges && itinerary.company_badges.length > 0 && (
              <div className="mx-auto mt-10 md:mt-16 mb-16 md:mb-32 flex flex-wrap justify-center gap-6 md:gap-12 items-center px-4">
                {itinerary.company_badges.map((badge, index) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    key={index}
                    src={badge.asset_url}
                    alt={badge.asset_name || 'Award Badge'}
                    className="h-24 md:h-48 w-auto object-contain opacity-90 hover:opacity-100 transition-opacity"
                  />
                ))}
              </div>
            )}
          </div>
        );
      })()}

      {/* ── End of Itinerary Image ────────────────────────────────── */}
      {(() => {
        const endImage = itinerary.images?.find((img: any) => img.image_role === 'end');
        if (!endImage) return null;
        return (
          <div className="w-full h-[220px] md:h-[600px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={endImage.image_url} alt="End of Itinerary" className="w-full h-full object-cover" />
          </div>
        );
      })()}

      {/* ── Closing Message ───────────────────────────────────────── */}
      {itinerary.closing_message && (
        <div className="py-12 md:py-24 bg-white">
          <div className="container mx-auto px-4 text-center max-w-4xl">
            <p className="italic text-gray-800 leading-relaxed whitespace-pre-line" style={{ fontSize: px('closing_size'), fontFamily: sty('global_serif') }}>
              {itinerary.closing_message}
            </p>
          </div>
        </div>
      )}

      {/* ── Footer ────────────────────────────────────────────────── */}
      <div className="pb-10" style={{ backgroundColor: lbl('page_footer_bg_color'), paddingTop: px('footer_padding_top') }}>
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 items-center">

            {/* Left — Agent & Company */}
            <div className="md:col-span-8 flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-12 relative">
              {/* Agent Image */}
              <div className="flex-shrink-0">
                <div className="h-28 w-28 md:h-40 md:w-40 bg-gray-200 overflow-hidden shadow-md">
                  {itinerary.agent_profile_photo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={itinerary.agent_profile_photo_url} alt="Agent" className="h-full w-full object-cover" />
                  ) : (
                    <div className="h-full w-full flex items-center justify-center text-white font-bold text-4xl" style={{ backgroundColor: lbl('page_color_primary') }}>
                      {itinerary.agent_name ? itinerary.agent_name.charAt(0) : 'A'}
                    </div>
                  )}
                </div>
              </div>

              {/* Agent Details */}
              <div className="flex flex-col text-center md:text-left space-y-3 md:space-y-4 font-sans text-gray-800">
                <div>
                  <h3 className="mb-1" style={{ fontSize: px('footer_name_size'), fontWeight: sty('footer_name_weight') }}>{itinerary.agent_name || 'Travel Consultant'}</h3>
                  <p className="tracking-wide uppercase text-gray-500" style={{ fontSize: px('footer_position_size') }}>{itinerary.agent_position || 'Travel Consultant'}</p>
                </div>
                <div className="space-y-1 text-base md:text-lg leading-relaxed">
                  {itinerary.agent_phone && (
                    <p><span className="font-bold mr-2">M:</span> {itinerary.agent_phone}</p>
                  )}
                  <p><span className="font-bold mr-2">E:</span> {itinerary.agent_email || 'info@easytravel.co.tz'}</p>
                  {itinerary.company_address && (
                    <div className="flex justify-center md:justify-start">
                      <span className="font-bold mr-2 flex-shrink-0">A:</span>
                      <span className="max-w-[250px] text-left">{itinerary.company_address}</span>
                    </div>
                  )}

                  {/* Social Media Icons */}
                  {itinerary.company_socials && (
                    <div className="flex justify-center md:justify-start mt-2 md:mt-3">
                      <div className="flex gap-2">
                        {itinerary.company_socials.facebook && (
                          <a href={itinerary.company_socials.facebook} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors">
                            <Facebook className="h-4 w-4" />
                          </a>
                        )}
                        {itinerary.company_socials.instagram && (
                          <a href={itinerary.company_socials.instagram} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors">
                            <Instagram className="h-4 w-4" />
                          </a>
                        )}
                        {itinerary.company_socials.twitter && (
                          <a href={itinerary.company_socials.twitter} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors">
                            <Twitter className="h-4 w-4" />
                          </a>
                        )}
                        {itinerary.company_socials.linkedin && (
                          <a href={itinerary.company_socials.linkedin} target="_blank" rel="noopener noreferrer" className="text-gray-900 border border-black rounded-md p-1.5 hover:bg-gray-100 transition-colors">
                            <Linkedin className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Vertical Divider — desktop only */}
              <div className="hidden md:block absolute right-[-24px] top-0 bottom-0 w-[1px] h-full opacity-50" style={{ backgroundColor: lbl('page_color_primary') }}></div>
            </div>

            {/* Right — Review Image */}
            <div className="md:col-span-4 flex justify-center">
              {itinerary.review_image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={itinerary.review_image_url} alt="Review / Testimonial" className="max-h-[200px] md:max-h-[320px] max-w-full object-contain" />
              ) : (
                <div className="h-32 w-full bg-gray-100/50 border-2 border-dashed border-gray-300 rounded flex items-center justify-center text-gray-400 text-sm">
                  No Review Image Set
                </div>
              )}
            </div>

          </div>

          {/* Footer Notes */}
          {itinerary.footer_notes && (
            <div className="mt-10 md:mt-16 pt-6 md:pt-8 border-t border-gray-300 text-center text-sm text-gray-500 font-sans whitespace-pre-line">
              {itinerary.footer_notes}
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
