'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';
import { Loader2, Trash2, Upload, Plus } from 'lucide-react';
import ImageGalleryModal from '@/components/shared/image-gallery-modal';

// ── Group Types Card ────────────────────────────────────────────────────────
function GroupTypesCard() {
  const [types, setTypes] = useState<string[]>([]);
  const [newType, setNewType] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiClient.getGroupTypes().then(setTypes).catch(() => {});
  }, []);

  const save = async (updated: string[]) => {
    setSaving(true);
    try {
      await apiClient.updateGroupTypes(updated);
      setTypes(updated);
      toast.success('Group types saved');
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleAdd = () => {
    const trimmed = newType.trim();
    if (!trimmed) return;
    if (types.map(t => t.toLowerCase()).includes(trimmed.toLowerCase())) {
      toast.error('Already exists');
      return;
    }
    setNewType('');
    save([...types, trimmed]);
  };

  const handleRemove = (idx: number) => {
    save(types.filter((_, i) => i !== idx));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Group Types</CardTitle>
        <CardDescription>
          Manage the list of group types available when creating an itinerary (e.g. Solo, Family, Friends).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {types.map((t, i) => (
            <span
              key={i}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border bg-muted text-sm font-medium"
            >
              {t}
              <button
                type="button"
                onClick={() => handleRemove(i)}
                className="text-gray-400 hover:text-red-500 transition-colors"
                title="Remove"
              >
                ×
              </button>
            </span>
          ))}
          {types.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No group types defined yet.</p>
          )}
        </div>
        <div className="flex gap-2 max-w-sm">
          <Input
            placeholder="e.g. Honeymoon"
            value={newType}
            onChange={e => setNewType(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), handleAdd())}
          />
          <Button type="button" onClick={handleAdd} disabled={saving || !newType.trim()}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
            Add
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
// ────────────────────────────────────────────────────────────────────────────

interface Template {
  key: string;
  content: string;
}

interface Asset {
  id: string;
  asset_name: string;
  asset_url: string;
  asset_type: string;
}

export default function SettingsPage() {
  const [initialLoad, setInitialLoad] = useState(true);
  
  // Tab State
  const [activeTab, setActiveTab] = useState("platform");

  // Gallery State
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [activeGalleryRole, setActiveGalleryRole] = useState<string | null>(null);
  const [activeGalleryType, setActiveGalleryType] = useState<string>('DEFAULT_IMAGE');

  // Templates State
  const [templates, setTemplates] = useState<Record<string, string>>({});
  
  // Assets State
  const [awards, setAwards] = useState<Asset[]>([]);
  const [reviewImages, setReviewImages] = useState<Asset[]>([]);
  const [defaults, setDefaults] = useState<Asset[]>([]);
  const [logo, setLogo] = useState<Asset | null>(null);

  // Asset Types Enum
  const ASSET_TYPES = {
    AWARD: 'AWARD_BADGE',
    REVIEW: 'REVIEW_IMAGE',
    DEFAULT: 'DEFAULT_IMAGE',
    LOGO: 'LOGO'
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    // Only set loading true if it's the initial load or we want to block UI. 
    // For background refreshes (like after upload), we don't want to block UI or unmount tabs.
    
    // Helper to safely fetch or return default
    const safeFetch = async <T,>(promise: Promise<T>, fallback: T, name: string): Promise<T> => {
        try {
            return await promise;
        } catch (err: any) {
            console.error(`Failed to fetch ${name}:`, err);
            return fallback;
        }
    };

    try {
      // Execute in parallel but safely
      const [tpls, allAssetsData] = await Promise.all([
        safeFetch(apiClient.getCompanyTemplates(), [], 'templates'),
        safeFetch(apiClient.listCompanyAssets(), [], 'allAssets') // fetch all at once to save roundtrips
      ]);

      const tplMap: Record<string, string> = {};
      if (Array.isArray(tpls)) {
          tpls.forEach((t: Template) => {
            tplMap[t.key] = t.content;
          });
      }
      setTemplates(tplMap);

      if (Array.isArray(allAssetsData)) {
          const awardsData = allAssetsData.filter(a => a.asset_type === ASSET_TYPES.AWARD);
          const reviewsData = allAssetsData.filter(a => a.asset_type === ASSET_TYPES.REVIEW);
          const defaultsData = allAssetsData.filter(a => a.asset_type === ASSET_TYPES.DEFAULT);
          const logoData = allAssetsData.filter(a => a.asset_type === ASSET_TYPES.LOGO);

          setAwards(awardsData);
          setReviewImages(reviewsData);
          setDefaults(defaultsData);
          // Take the most recent logo if multiple exist
          setLogo(logoData.length > 0 ? logoData[logoData.length - 1] : null);
      }

    } catch (error) {
      console.error("Critical error in fetchData:", error);
      toast.error('Failed to initialize settings page');
    } finally {
      setInitialLoad(false);
    }
  };

  const handleTemplateSave = async (key: string) => {
    const toastId = toast.loading('Saving...');
    try {
      await apiClient.updateCompanyTemplate(key, { content: templates[key] || '' });
      toast.success('Saved', { id: toastId });
    } catch (error) {
      toast.error('Failed to save', { id: toastId });
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, type: string, assetName?: string) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const toastId = toast.loading('Uploading...');
    try {
      await apiClient.uploadCompanyAsset(file, type, assetName);
      toast.success('Uploaded', { id: toastId });
      fetchData(); // Refresh all
    } catch (error) {
      toast.error('Upload failed', { id: toastId });
    }
  };

  const handleDeleteAsset = async (id: string) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;
    const toastId = toast.loading('Deleting...');
    try {
      await apiClient.deleteCompanyAsset(id);
      toast.success('Deleted', { id: toastId });
      fetchData();
    } catch (error) {
      toast.error('Delete failed', { id: toastId });
    }
  };
  

  const handleGallerySelect = async (images: {url: string, caption?: string}[]) => {
      if (!images || images.length === 0) return;
      const image = images[0]; 
      
      const toastId = toast.loading('Linking asset...');
      try {
          await apiClient.linkCompanyAsset({
              asset_url: image.url,
              asset_type: activeGalleryType,
              asset_name: activeGalleryRole || image.caption || "Linked Asset", 
          });
          
          toast.success('Asset set from gallery', { id: toastId });
          setIsGalleryOpen(false);
          setActiveGalleryRole(null);
          // Don't await this, let it update in background so UI stays responsive
          fetchData(); 
      } catch (error: any) {
          console.error("Gallery Select Error:", error);
          const errorMsg = error.response?.data?.detail || error.message || 'Failed to set asset';
          toast.error(`Error: ${errorMsg}`, { id: toastId });
      }
  };

  const openGalleryForDefault = (role: string) => {
      setActiveGalleryRole(role);
      setActiveGalleryType(ASSET_TYPES.DEFAULT);
      setIsGalleryOpen(true);
  };
  
  const openGalleryForAsset = (type: string) => {
      setActiveGalleryRole(null); // No specific role for list items
      setActiveGalleryType(type);
      setIsGalleryOpen(true);
  };

  const getDefaultImage = (role: string) => {
    return defaults.find(d => d.asset_name === role);
  };

  // ── Page Styles helpers (stored as JSON in templates['page_styles']) ──────
  const getStyle = (key: string, def: string = '') => {
    try {
      const s = JSON.parse(templates['page_styles'] || '{}');
      return s[key] !== undefined ? String(s[key]) : def;
    } catch { return def; }
  };

  const setStyle = (key: string, value: string) => {
    try {
      const s = JSON.parse(templates['page_styles'] || '{}');
      s[key] = value;
      setTemplates(prev => ({ ...prev, page_styles: JSON.stringify(s) }));
    } catch {
      setTemplates(prev => ({ ...prev, page_styles: JSON.stringify({ [key]: value }) }));
    }
  };

  const saveStyles = () => handleTemplateSave('page_styles');

  // Common select className reused from theme tab
  const SEL = "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

  if (initialLoad) {
    return <div className="p-8 flex justify-center"><Loader2 className="animate-spin" /></div>;
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Global Content Settings</h1>
        <p className="text-muted-foreground">Manage platform settings, content, templates, and imagery.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="flex-wrap h-auto gap-1">
            <TabsTrigger value="platform">Platform Settings</TabsTrigger>
          <TabsTrigger value="theme">Theme & Design</TabsTrigger>
          <TabsTrigger value="homepage">Homepage</TabsTrigger>
          <TabsTrigger value="content">Messages & Content</TabsTrigger>
          <TabsTrigger value="itinerary-page">Itinerary Page</TabsTrigger>
          <TabsTrigger value="assets">Media Assets</TabsTrigger>
          <TabsTrigger value="defaults">Default Images</TabsTrigger>
        </TabsList>

        {/* PLATFORM TAB */}
        <TabsContent value="platform" className="space-y-4">
             <div className="grid gap-4 md:grid-cols-2">
                 <Card>
                    <CardHeader>
                        <CardTitle>Platform Branding</CardTitle>
                        <CardDescription>Customize the application name and description displayed in the dashboard.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="app-name">Application Name</Label>
                            <Input
                                id="app-name"
                                value={templates['app_name'] || ''}
                                onChange={(e) => setTemplates({...templates, app_name: e.target.value})}
                                placeholder="e.g. Acme Travels"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="app-desc">Application Description</Label>
                            <Textarea
                                id="app-desc"
                                value={templates['app_description'] || ''}
                                onChange={(e) => setTemplates({...templates, app_description: e.target.value})}
                                placeholder="A brief description of your platform..."
                                className="min-h-[100px]"
                            />
                        </div>
                         <Button onClick={() => {
                             handleTemplateSave('app_name');
                             handleTemplateSave('app_description');
                         }}>Save Branding</Button>
                    </CardContent>
                 </Card>

                 <Card>
                    <CardHeader>
                        <CardTitle>Company Logo</CardTitle>
                        <CardDescription>Upload your company logo. This will be displayed in the header and emails.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center p-6">
                        {logo ? (
                            <div className="relative group w-full max-w-sm aspect-video bg-muted rounded-lg border flex items-center justify-center p-4">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img src={logo.asset_url} alt="Company Logo" className="max-h-full max-w-full object-contain" />
                                <Button
                                    variant="destructive"
                                    size="icon"
                                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleDeleteAsset(logo.id)}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        ) : (
                            <div className="w-full max-w-sm h-64 border-2 border-dashed rounded-lg flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors">
                                <Upload className="h-10 w-10 text-muted-foreground mb-2" />
                                <span className="text-sm text-muted-foreground">No Logo Uploaded</span>
                            </div>
                        )}

                        <div className="mt-4 flex gap-2 w-full max-w-sm">
                            <Button 
                                variant="outline" 
                                className="flex-1"
                                onClick={() => openGalleryForAsset(ASSET_TYPES.LOGO)}
                            >
                                <Plus className="h-4 w-4 mr-2" /> From Library
                            </Button>
                            <Label htmlFor="upload-logo" className="flex-1">
                                <div className="flex h-10 w-full cursor-pointer items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 text-sm font-medium transition-colors">
                                    <Upload className="h-4 w-4 mr-2" /> Upload New
                                </div>
                                <input 
                                    id="upload-logo" 
                                    type="file" 
                                    className="hidden" 
                                    accept="image/*"
                                    onChange={(e) => handleFileUpload(e, ASSET_TYPES.LOGO, 'Company Logo')}
                                />
                            </Label>
                        </div>
                    </CardContent>
                 </Card>
             </div>

             {/* Company Contact & Socials */}
             <div className="grid gap-4 md:grid-cols-1">
                 <Card>
                    <CardHeader>
                        <CardTitle>Company Information</CardTitle>
                        <CardDescription>Contact details and social media links displayed in the itinerary footer.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="comp-address">Company Address</Label>
                                <Input
                                    id="comp-address"
                                    value={templates['company_address'] || ''}
                                    onChange={(e) => setTemplates({...templates, company_address: e.target.value})}
                                    placeholder="123 Safari Way, Arusha, Tanzania"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="comp-phone">Company Phone</Label>
                                <Input
                                    id="comp-phone"
                                    value={templates['company_phone'] || ''}
                                    onChange={(e) => setTemplates({...templates, company_phone: e.target.value})}
                                    placeholder="+255 123 456 789"
                                />
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <Label htmlFor="comp-website">Website URL</Label>
                                <Input
                                    id="comp-website"
                                    value={templates['company_website'] || ''}
                                    onChange={(e) => setTemplates({...templates, company_website: e.target.value})}
                                    placeholder="https://www.easytravel.co.tz"
                                />
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h4 className="text-sm font-medium leading-none">Social Media Links</h4>
                            <div className="grid gap-4 md:grid-cols-2">
                                <div className="space-y-2">
                                    <Label htmlFor="social-fb">Facebook</Label>
                                    <Input
                                        id="social-fb"
                                        value={templates['social_facebook'] || ''}
                                        onChange={(e) => setTemplates({...templates, social_facebook: e.target.value})}
                                        placeholder="Facebook URL"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="social-ig">Instagram</Label>
                                    <Input
                                        id="social-ig"
                                        value={templates['social_instagram'] || ''}
                                        onChange={(e) => setTemplates({...templates, social_instagram: e.target.value})}
                                        placeholder="Instagram URL"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="social-tw">Twitter / X</Label>
                                    <Input
                                        id="social-tw"
                                        value={templates['social_twitter'] || ''}
                                        onChange={(e) => setTemplates({...templates, social_twitter: e.target.value})}
                                        placeholder="Twitter URL"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="social-li">LinkedIn</Label>
                                    <Input
                                        id="social-li"
                                        value={templates['social_linkedin'] || ''}
                                        onChange={(e) => setTemplates({...templates, social_linkedin: e.target.value})}
                                        placeholder="LinkedIn URL"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="footer-notes">Footer Notes</Label>
                            <Textarea
                                id="footer-notes"
                                value={templates['footer_notes'] || ''}
                                onChange={(e) => setTemplates({...templates, footer_notes: e.target.value})}
                                placeholder="Additional notes to display at the bottom of the itinerary footer..."
                                className="min-h-[80px]"
                            />
                        </div>

                        <Button onClick={() => {
                             handleTemplateSave('company_address');
                             handleTemplateSave('company_phone');
                             handleTemplateSave('company_website');
                             handleTemplateSave('social_facebook');
                             handleTemplateSave('social_instagram');
                             handleTemplateSave('social_twitter');
                             handleTemplateSave('social_linkedin');
                             handleTemplateSave('footer_notes');
                        }}>Save Company Details</Button>
                    </CardContent>
                 </Card>
             </div>

             {/* Group Types Management */}
             <GroupTypesCard />

        </TabsContent>

        {/* THEME TAB */}
        <TabsContent value="theme" className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>Global Theme & Typography</CardTitle>
                    <CardDescription>Customize the primary color and typography for your platform and itineraries.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                            <Label htmlFor="theme-color">Primary Theme Color</Label>
                            <div className="flex items-center gap-3">
                                <Input
                                    id="theme-color"
                                    type="color"
                                    value={templates['theme_primary_color'] || '#1d4ed8'}
                                    onChange={(e) => setTemplates({...templates, theme_primary_color: e.target.value})}
                                    className="w-16 h-10 p-1 cursor-pointer"
                                />
                                <Input
                                    type="text"
                                    value={templates['theme_primary_color'] || '#1d4ed8'}
                                    onChange={(e) => setTemplates({...templates, theme_primary_color: e.target.value})}
                                    className="flex-1 font-mono uppercase"
                                    maxLength={7}
                                    placeholder="#1D4ED8"
                                />
                            </div>
                            <p className="text-xs text-muted-foreground">Used for buttons, links, and accents.</p>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="theme-font">Global Typography</Label>
                            <select
                                id="theme-font"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={templates['theme_font_family'] || 'sans'}
                                onChange={(e) => setTemplates({...templates, theme_font_family: e.target.value})}
                            >
                                <option value="sans">System Default (Sans-serif)</option>
                                <option value="inter">Inter (Modern Sans)</option>
                                <option value="lato">Lato (Classic Sans)</option>
                                <option value="playfair">Playfair Display (Elegant Serif)</option>
                            </select>
                            <p className="text-xs text-muted-foreground">The primary font used throughout the app.</p>
                        </div>
                    </div>
                    <Button onClick={() => {
                        handleTemplateSave('theme_primary_color');
                        handleTemplateSave('theme_font_family');
                        setTimeout(() => window.location.reload(), 1000); // Reload to apply theme
                    }}>Save Theme Preferences</Button>
                </CardContent>
            </Card>
        </TabsContent>

        {/* HOMEPAGE TAB */}
        <TabsContent value="homepage" className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>Homepage Content</CardTitle>
                    <CardDescription>Customize the text displayed on the public landing page.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-4 border-b pb-4">
                        <h3 className="font-semibold text-lg">Hero Section</h3>
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="hero-title">Main Title</Label>
                                <Input
                                    id="hero-title"
                                    value={templates['home_hero_title'] || ''}
                                    placeholder="Travel Agency Management System"
                                    onChange={(e) => setTemplates({...templates, home_hero_title: e.target.value})}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="hero-subtitle">Subtitle</Label>
                                <Input
                                    id="hero-subtitle"
                                    value={templates['home_hero_subtitle'] || ''}
                                    placeholder="Comprehensive platform for creating..."
                                    onChange={(e) => setTemplates({...templates, home_hero_subtitle: e.target.value})}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4 border-b pb-4">
                        <h3 className="font-semibold text-lg">Features Section</h3>
                        {[1, 2, 3, 4].map((num) => (
                            <div key={num} className="grid gap-4 md:grid-cols-2 bg-slate-50 p-4 rounded-lg">
                                <div className="space-y-2">
                                    <Label htmlFor={`feat${num}-title`}>Feature {num} Title</Label>
                                    <Input
                                        id={`feat${num}-title`}
                                        value={templates[`home_feat${num}_title`] || ''}
                                        placeholder={`Feature ${num} Title`}
                                        onChange={(e) => setTemplates({...templates, [`home_feat${num}_title`]: e.target.value})}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor={`feat${num}-desc`}>Feature {num} Description</Label>
                                    <Input
                                        id={`feat${num}-desc`}
                                        value={templates[`home_feat${num}_desc`] || ''}
                                        placeholder={`Feature ${num} validation text`}
                                        onChange={(e) => setTemplates({...templates, [`home_feat${num}_desc`]: e.target.value})}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="space-y-4 border-b pb-4">
                        <h3 className="font-semibold text-lg">Quick Links Section</h3>
                        <div className="space-y-4 bg-slate-50 p-4 rounded-lg">
                            <div className="space-y-2">
                                <Label htmlFor="links-title">Main Section Title</Label>
                                <Input
                                    id="links-title"
                                    value={templates['home_links_title'] || ''}
                                    placeholder="Platform Features"
                                    onChange={(e) => setTemplates({...templates, home_links_title: e.target.value})}
                                />
                            </div>
                            
                            <div className="grid gap-4 md:grid-cols-3">
                                {[1, 2, 3].map((colNum) => (
                                    <div key={colNum} className="space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor={`col${colNum}-title`}>Column {colNum} Title</Label>
                                            <Input
                                                id={`col${colNum}-title`}
                                                value={templates[`home_links_col${colNum}_title`] || ''}
                                                placeholder={`e.g. For Travelers`}
                                                onChange={(e) => setTemplates({...templates, [`home_links_col${colNum}_title`]: e.target.value})}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor={`col${colNum}-items`}>Column {colNum} Items (One per line)</Label>
                                            <Textarea
                                                id={`col${colNum}-items`}
                                                value={templates[`home_links_col${colNum}_items`] || ''}
                                                placeholder={`Item 1\nItem 2\nItem 3`}
                                                className="min-h-[120px]"
                                                onChange={(e) => setTemplates({...templates, [`home_links_col${colNum}_items`]: e.target.value})}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <Button onClick={() => {
                        handleTemplateSave('home_hero_title');
                        handleTemplateSave('home_hero_subtitle');
                        for(let i=1; i<=4; i++) {
                            handleTemplateSave(`home_feat${i}_title`);
                            handleTemplateSave(`home_feat${i}_desc`);
                        }
                        handleTemplateSave('home_links_title');
                        for(let i=1; i<=3; i++) {
                            handleTemplateSave(`home_links_col${i}_title`);
                            handleTemplateSave(`home_links_col${i}_items`);
                        }
                    }}>Save Homepage Content</Button>
                </CardContent>
            </Card>
        </TabsContent>

        {/* CONTENT TAB */}
        <TabsContent value="content" className="space-y-4">

          {/* Variable Reference Card */}
          <Card className="border-blue-100 bg-blue-50/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-blue-800">Available Template Variables</CardTitle>
              <CardDescription className="text-xs text-blue-600">
                Click any variable to copy it. Paste it anywhere in the templates below — it will be replaced with real data when the itinerary is viewed.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {[
                  { tag: '[Traveller Name]',         desc: 'Primary traveller\'s name' },
                  { tag: '[Tour Name]',               desc: 'Name of the tour' },
                  { tag: '[Tour Days]',               desc: 'Number of days' },
                  { tag: '[From Date]',               desc: 'Departure date (e.g. March 20, 2026)' },
                  { tag: '[To Date]',                 desc: 'Return date' },
                  { tag: '[List of Travellers]',      desc: 'All traveller names, comma-separated' },
                  { tag: '[List of Destinations]',    desc: 'All destinations in day order, comma-separated' },
                  { tag: '[List of Accommodations]',  desc: 'All unique accommodations, comma-separated' },
                  { tag: '[Agent Name]',              desc: 'Assigned agent\'s full name' },
                  { tag: '[Client Name]',             desc: 'Alias for Traveller Name' },
                ].map(({ tag, desc }) => (
                  <button
                    key={tag}
                    type="button"
                    title={desc}
                    onClick={() => {
                      // navigator.clipboard requires HTTPS — use execCommand fallback for HTTP
                      const copy = (text: string) => {
                        if (navigator.clipboard && window.isSecureContext) {
                          return navigator.clipboard.writeText(text);
                        }
                        const el = document.createElement('textarea');
                        el.value = text;
                        el.style.position = 'fixed';
                        el.style.opacity = '0';
                        document.body.appendChild(el);
                        el.focus();
                        el.select();
                        document.execCommand('copy');
                        document.body.removeChild(el);
                        return Promise.resolve();
                      };
                      copy(tag)
                        .then(() => toast.success(`Copied ${tag}`))
                        .catch(() => toast.error('Copy failed'));
                    }}
                    className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-white border border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-400 transition-colors cursor-pointer shadow-sm"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Greeting Message</CardTitle>
              <CardDescription>
                Default greeting for the itinerary intro page.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Textarea
                value={templates['intro_letter_template'] || ''}
                onChange={(e) => setTemplates({...templates, intro_letter_template: e.target.value})}
                className="min-h-[200px] font-mono text-sm"
                placeholder="Hello [Traveller Name], we are excited to present your [Tour Name] itinerary from [From Date] to [To Date]..."
              />
              <Button onClick={() => handleTemplateSave('intro_letter_template')}>Save Changes</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>About Easy Travel</CardTitle>
              <CardDescription>
                "About Us" content displayed in the itinerary.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Textarea
                value={templates['about_company_template'] || ''}
                onChange={(e) => setTemplates({...templates, about_company_template: e.target.value})}
                className="min-h-[150px] font-mono text-sm"
                placeholder="We are..."
              />
              <Button onClick={() => handleTemplateSave('about_company_template')}>Save Changes</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Final Closing Message</CardTitle>
              <CardDescription>
                Message displayed on the final page of the itinerary.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Textarea
                value={templates['cta_message_template'] || ''}
                onChange={(e) => setTemplates({...templates, cta_message_template: e.target.value})}
                className="min-h-[100px] font-mono text-sm"
                placeholder="We look forward to welcoming [List of Travellers] on their journey to [List of Destinations]..."
              />
              <Button onClick={() => handleTemplateSave('cta_message_template')}>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ITINERARY PAGE TAB */}
        <TabsContent value="itinerary-page" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Itinerary Page Editor</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Customise every piece of text shown on the client-facing itinerary view page. Changes apply to all itineraries instantly.
              </p>
            </div>
          </div>

          {/* Section Headings */}
          <Card>
            <CardHeader>
              <CardTitle>Section Headings</CardTitle>
              <CardDescription>The large uppercase headings that appear between each section of the itinerary.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  { key: 'page_heading_itinerary',           label: 'Day-by-Day Section Heading',    placeholder: 'Itinerary' },
                  { key: 'page_heading_accommodations',      label: 'Accommodations Heading',         placeholder: 'ACCOMMODATIONS' },
                  { key: 'page_heading_whats_included',      label: "What's Included Heading",        placeholder: "What's Included" },
                  { key: 'page_heading_whats_excluded',      label: "What's Excluded Heading",        placeholder: "What's Excluded" },
                  { key: 'page_heading_about',               label: 'About Section Heading',          placeholder: 'ABOUT EASY TRAVEL' },
                ].map(({ key, label, placeholder }) => (
                  <div key={key} className="space-y-2">
                    <Label>{label}</Label>
                    <Input
                      value={templates[key] || ''}
                      placeholder={placeholder}
                      onChange={(e) => setTemplates({ ...templates, [key]: e.target.value })}
                    />
                  </div>
                ))}
              </div>
              <Button onClick={() => {
                ['page_heading_itinerary','page_heading_accommodations','page_heading_whats_included','page_heading_whats_excluded','page_heading_about'].forEach(handleTemplateSave);
              }}>Save Headings</Button>
            </CardContent>
          </Card>

          {/* Day Labels */}
          <Card>
            <CardHeader>
              <CardTitle>Day Detail Labels</CardTitle>
              <CardDescription>Labels shown inside each day card for accommodation, meals, and activities.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                {[
                  { key: 'page_label_overnight_at',         label: '"Overnight At" Label',            placeholder: 'Overnight At:' },
                  { key: 'page_label_meal_plan',            label: '"Meal Plan" Label',               placeholder: 'Meal Plan:' },
                  { key: 'page_label_todays_activities',    label: '"Today\'s Activities" Label',     placeholder: "Today's Activities" },
                ].map(({ key, label, placeholder }) => (
                  <div key={key} className="space-y-2">
                    <Label>{label}</Label>
                    <Input
                      value={templates[key] || ''}
                      placeholder={placeholder}
                      onChange={(e) => setTemplates({ ...templates, [key]: e.target.value })}
                    />
                  </div>
                ))}
              </div>
              <Button onClick={() => {
                ['page_label_overnight_at','page_label_meal_plan','page_label_todays_activities'].forEach(handleTemplateSave);
              }}>Save Labels</Button>
            </CardContent>
          </Card>

          {/* Contact Block */}
          <Card>
            <CardHeader>
              <CardTitle>Welcome Letter Contact Block</CardTitle>
              <CardDescription>The company name, phone, and email shown below the welcome message on every itinerary.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                {[
                  { key: 'page_contact_company_name',     label: 'Company Display Name',    placeholder: 'Easy Travel Tanzania' },
                  { key: 'page_contact_company_phone',    label: 'Display Phone Number',     placeholder: '+ 255 786 400 148' },
                  { key: 'page_contact_fallback_email',   label: 'Fallback Email Address',   placeholder: 'info@easytravel.co.tz' },
                ].map(({ key, label, placeholder }) => (
                  <div key={key} className="space-y-2">
                    <Label>{label}</Label>
                    <Input
                      value={templates[key] || ''}
                      placeholder={placeholder}
                      onChange={(e) => setTemplates({ ...templates, [key]: e.target.value })}
                    />
                  </div>
                ))}
              </div>
              <Button onClick={() => {
                ['page_contact_company_name','page_contact_company_phone','page_contact_fallback_email'].forEach(handleTemplateSave);
              }}>Save Contact Info</Button>
            </CardContent>
          </Card>

          {/* ── Typography & Spacing ─────────────────────────────── */}
          <div className="pt-4 border-t">
            <h2 className="text-xl font-semibold mb-1">Typography & Spacing</h2>
            <p className="text-sm text-muted-foreground mb-4">Font size (px), weight, and family for each section. Spacing controls gaps and padding. All changes apply instantly.</p>
          </div>

          {/* Global Fonts */}
          <Card>
            <CardHeader>
              <CardTitle>Global Font Families</CardTitle>
              <CardDescription>Base font stacks used throughout the page. Sans-serif for body/labels, serif for headings like the hero title.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Sans-serif Family</Label>
                  <select className={SEL} value={getStyle('global_sans', 'system-ui, sans-serif')} onChange={e => setStyle('global_sans', e.target.value)}>
                    <option value="system-ui, sans-serif">System Default</option>
                    <option value="Arial, sans-serif">Arial</option>
                    <option value="'Helvetica Neue', sans-serif">Helvetica</option>
                    <option value="Verdana, sans-serif">Verdana</option>
                    <option value="'Trebuchet MS', sans-serif">Trebuchet MS</option>
                    <option value="'Gill Sans', sans-serif">Gill Sans</option>
                    <option value="Tahoma, sans-serif">Tahoma</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Serif Family (hero title, etc.)</Label>
                  <select className={SEL} value={getStyle('global_serif', 'Georgia, serif')} onChange={e => setStyle('global_serif', e.target.value)}>
                    <option value="Georgia, serif">Georgia</option>
                    <option value="'Times New Roman', serif">Times New Roman</option>
                    <option value="Palatino, serif">Palatino</option>
                    <option value="Garamond, serif">Garamond</option>
                    <option value="'Book Antiqua', serif">Book Antiqua</option>
                    <option value="'Cormorant Garamond', serif">Cormorant Garamond</option>
                  </select>
                </div>
              </div>
              <Button onClick={saveStyles}>Save Global Fonts</Button>
            </CardContent>
          </Card>

          {/* Hero Section */}
          <Card>
            <CardHeader>
              <CardTitle>Hero Section</CardTitle>
              <CardDescription>The full-screen opening image with tour title and description.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Tour Title</div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('hero_title_size', '56')} onChange={e => setStyle('hero_title_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('hero_title_weight', '700')} onChange={e => setStyle('hero_title_weight', e.target.value)}>
                    <option value="300">Light (300)</option><option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option><option value="800">Extra Bold (800)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Font Family</Label>
                  <select className={SEL} value={getStyle('hero_title_family', 'serif')} onChange={e => setStyle('hero_title_family', e.target.value)}>
                    <option value="serif">Serif (global serif)</option>
                    <option value="sans-serif">Sans-serif (global sans)</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Tour Description / Subtitle</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('hero_desc_size', '20')} onChange={e => setStyle('hero_desc_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('hero_desc_weight', '300')} onChange={e => setStyle('hero_desc_weight', e.target.value)}>
                    <option value="300">Light (300)</option><option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
              </div>
              <Button onClick={saveStyles}>Save Hero Typography</Button>
            </CardContent>
          </Card>

          {/* Section Headings Typography */}
          <Card>
            <CardHeader>
              <CardTitle>Section Headings Typography</CardTitle>
              <CardDescription>Applies to Itinerary, Accommodations, What's Included, What's Excluded, and About headings.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('heading_size', '48')} onChange={e => setStyle('heading_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('heading_weight', '600')} onChange={e => setStyle('heading_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option><option value="800">Extra Bold (800)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Letter Spacing</Label>
                  <select className={SEL} value={getStyle('heading_spacing', '0.2em')} onChange={e => setStyle('heading_spacing', e.target.value)}>
                    <option value="0">None</option>
                    <option value="0.05em">Tight (0.05em)</option>
                    <option value="0.1em">Normal (0.1em)</option>
                    <option value="0.2em">Wide (0.2em)</option>
                    <option value="0.3em">Wider (0.3em)</option>
                    <option value="0.4em">Widest (0.4em)</option>
                  </select>
                </div>
              </div>
              <Button onClick={saveStyles}>Save Heading Typography</Button>
            </CardContent>
          </Card>

          {/* Day Cards Typography */}
          <Card>
            <CardHeader>
              <CardTitle>Day Cards Typography</CardTitle>
              <CardDescription>Text inside each day's content block — title, description, and detail labels.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Day Title</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('day_title_size', '22')} onChange={e => setStyle('day_title_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('day_title_weight', '600')} onChange={e => setStyle('day_title_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Day Description</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('day_desc_size', '16')} onChange={e => setStyle('day_desc_size', e.target.value)} />
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Detail Labels (Overnight At, Meal Plan, etc.)</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('day_label_size', '16')} onChange={e => setStyle('day_label_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('day_label_weight', '700')} onChange={e => setStyle('day_label_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Day Card Internal Padding</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Horizontal Padding (px)</Label>
                  <Input type="number" value={getStyle('day_padding_x', '96')} onChange={e => setStyle('day_padding_x', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Vertical Padding (px)</Label>
                  <Input type="number" value={getStyle('day_padding_y', '100')} onChange={e => setStyle('day_padding_y', e.target.value)} />
                </div>
              </div>
              <Button onClick={saveStyles}>Save Day Card Typography</Button>
            </CardContent>
          </Card>

          {/* Inclusions & Exclusions Typography + Layout */}
          <Card>
            <CardHeader>
              <CardTitle>Inclusions & Exclusions Typography & Layout</CardTitle>
              <CardDescription>Font styling for item titles and descriptions, plus spacing between items.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Item Title</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('inc_title_size', '20')} onChange={e => setStyle('inc_title_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Font Weight</Label>
                  <select className={SEL} value={getStyle('inc_title_weight', '700')} onChange={e => setStyle('inc_title_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Item Description</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('inc_desc_size', '16')} onChange={e => setStyle('inc_desc_size', e.target.value)} />
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Layout Spacing</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Row Gap — between items vertically (px)</Label>
                  <Input type="number" value={getStyle('inc_row_gap', '80')} onChange={e => setStyle('inc_row_gap', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Column Gap — space between the 2 columns (px)</Label>
                  <Input type="number" value={getStyle('inc_col_gap', '450')} onChange={e => setStyle('inc_col_gap', e.target.value)} />
                </div>
              </div>
              <Button onClick={saveStyles}>Save Inclusions/Exclusions Styles</Button>
            </CardContent>
          </Card>

          {/* Welcome Letter & Closing */}
          <Card>
            <CardHeader>
              <CardTitle>Welcome Letter & Closing Message</CardTitle>
              <CardDescription>Typography for the personalised welcome text and the final closing message.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Welcome Letter Body</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('welcome_size', '16')} onChange={e => setStyle('welcome_size', e.target.value)} />
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Contact Block (Company Name / Phone / Email)</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('contact_name_size', '16')} onChange={e => setStyle('contact_name_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Company Name Weight</Label>
                  <select className={SEL} value={getStyle('contact_name_weight', '700')} onChange={e => setStyle('contact_name_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Closing Message</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Font Size (px)</Label>
                  <Input type="number" value={getStyle('closing_size', '20')} onChange={e => setStyle('closing_size', e.target.value)} />
                </div>
              </div>
              <Button onClick={saveStyles}>Save Welcome & Closing Styles</Button>
            </CardContent>
          </Card>

          {/* Footer Typography */}
          <Card>
            <CardHeader>
              <CardTitle>Footer Typography</CardTitle>
              <CardDescription>Agent name, position, and contact text sizing in the footer section.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Agent Name — Font Size (px)</Label>
                  <Input type="number" value={getStyle('footer_name_size', '20')} onChange={e => setStyle('footer_name_size', e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Agent Name — Font Weight</Label>
                  <select className={SEL} value={getStyle('footer_name_weight', '700')} onChange={e => setStyle('footer_name_weight', e.target.value)}>
                    <option value="400">Regular (400)</option><option value="500">Medium (500)</option>
                    <option value="600">Semi Bold (600)</option><option value="700">Bold (700)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Agent Position — Font Size (px)</Label>
                  <Input type="number" value={getStyle('footer_position_size', '14')} onChange={e => setStyle('footer_position_size', e.target.value)} />
                </div>
              </div>
              <div className="space-y-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider pt-2">Section Spacing</div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Footer Top Padding (px)</Label>
                  <Input type="number" value={getStyle('footer_padding_top', '96')} onChange={e => setStyle('footer_padding_top', e.target.value)} />
                </div>
              </div>
              <Button onClick={saveStyles}>Save Footer Styles</Button>
            </CardContent>
          </Card>

          {/* Brand Colours */}
          <Card>
            <CardHeader>
              <CardTitle>Brand Colours</CardTitle>
              <CardDescription>Colours used throughout the itinerary view. Enter valid hex codes (e.g. #5B7444).</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-6 md:grid-cols-3">
                {[
                  { key: 'page_color_primary',       label: 'Primary (headings, accents)',     placeholder: '#5B7444',  preview: templates['page_color_primary'] || '#5B7444' },
                  { key: 'page_color_exclusions',    label: "What's Excluded heading colour",  placeholder: '#c25d2a',  preview: templates['page_color_exclusions'] || '#c25d2a' },
                  { key: 'page_footer_bg_color',     label: 'Footer Background Colour',        placeholder: '#EFE9E6',  preview: templates['page_footer_bg_color'] || '#EFE9E6' },
                ].map(({ key, label, placeholder, preview }) => (
                  <div key={key} className="space-y-2">
                    <Label>{label}</Label>
                    <div className="flex gap-2 items-center">
                      <div
                        className="h-10 w-10 rounded-md border shadow-sm flex-shrink-0"
                        style={{ backgroundColor: preview }}
                      />
                      <Input
                        value={templates[key] || ''}
                        placeholder={placeholder}
                        onChange={(e) => setTemplates({ ...templates, [key]: e.target.value })}
                        className="font-mono"
                      />
                    </div>
                  </div>
                ))}
              </div>
              <Button onClick={() => {
                ['page_color_primary','page_color_exclusions','page_footer_bg_color'].forEach(handleTemplateSave);
              }}>Save Colours</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ASSETS TAB */}
        <TabsContent value="assets" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Award Badges</CardTitle>
              <CardDescription>Images displayed in the "About Us" section.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                {awards.map((asset) => (
                  <div key={asset.id} className="relative group border rounded-lg p-2">
                    <div className="relative h-20 w-full overflow-hidden rounded-md">
                       {/* eslint-disable-next-line @next/next/no-img-element */}
                       <img src={asset.asset_url} alt={asset.asset_name} className="h-full w-full object-contain" />
                    </div>
                    <Button
                      variant="destructive"
                      size="icon"
                      className="absolute top-0 right-0 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => handleDeleteAsset(asset.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
                
                <div className="flex flex-col gap-2">
                   <Button 
                      variant="outline" 
                      className="h-24 w-full flex-col gap-2 border-dashed"
                      onClick={() => openGalleryForAsset(ASSET_TYPES.AWARD)}
                   >
                       <div className="flex items-center justify-center h-8 w-8 rounded-full bg-slate-100">
                         <Plus className="h-4 w-4" />
                       </div>
                       <span className="text-xs text-muted-foreground">From Library</span>
                   </Button>
                    <Label htmlFor="upload-award" className="cursor-pointer border-dashed border-2 rounded-lg flex flex-col items-center justify-center h-24 hover:bg-slate-50 transition-colors">
                        <Upload className="h-6 w-6 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground mt-1">Upload New</span>
                        <input 
                            id="upload-award" 
                            type="file" 
                            className="hidden" 
                            accept="image/*"
                            onChange={(e) => handleFileUpload(e, ASSET_TYPES.AWARD)}
                        />
                    </Label>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Review / Testimonial Image</CardTitle>
              <CardDescription>Image displayed below the final message (e.g. TripAdvisor, Trustpilot).</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                 {reviewImages.map((asset) => (
                  <div key={asset.id} className="relative group border rounded-lg p-2">
                    <div className="relative h-20 w-full overflow-hidden rounded-md">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={asset.asset_url} alt={asset.asset_name} className="h-full w-full object-contain" />
                     </div>
                     <Button
                       variant="destructive"
                       size="icon"
                      className="absolute top-0 right-0 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => handleDeleteAsset(asset.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}

                <div className="flex flex-col gap-2">
                   <Button 
                      variant="outline" 
                      className="h-24 w-full flex-col gap-2 border-dashed"
                      onClick={() => openGalleryForAsset(ASSET_TYPES.REVIEW)}
                   >
                       <div className="flex items-center justify-center h-8 w-8 rounded-full bg-slate-100">
                         <Plus className="h-4 w-4" />
                       </div>
                       <span className="text-xs text-muted-foreground">From Library</span>
                   </Button>
                    <Label htmlFor="upload-review" className="cursor-pointer border-dashed border-2 rounded-lg flex flex-col items-center justify-center h-24 hover:bg-slate-50 transition-colors">
                        <Upload className="h-6 w-6 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground mt-1">Upload New</span>
                        <input 
                            id="upload-review" 
                            type="file" 
                            className="hidden" 
                            accept="image/*"
                            onChange={(e) => handleFileUpload(e, ASSET_TYPES.REVIEW)}
                        />
                    </Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* DEFAULTS TAB */}
        <TabsContent value="defaults" className="space-y-4">
             <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {[
                    { role: 'cover', label: 'Default Cover Photo', desc: 'Fallback cover image.' },
                    { role: 'accommodation_end', label: 'Default After Accommodations', desc: 'Fallback image after accommodations.' },
                    { role: 'inclusions', label: 'Default Inclusions Banner', desc: 'Fallback inclusions banner.' },
                    { role: 'about_banner', label: 'Default About Us Banner', desc: 'Fallback About Us banner.' },
                    { role: 'end', label: 'Default End Image', desc: 'Fallback closing image.' }
                ].map((slot) => {
                    const current = getDefaultImage(slot.role);
                    return (
                        <Card key={slot.role}>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">{slot.label}</CardTitle>
                                <CardDescription className="text-xs">{slot.desc}</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {current ? (
                                    <div className="space-y-2">
                                        <div className="relative aspect-video w-full overflow-hidden rounded-md border bg-muted">
                                            {/* eslint-disable-next-line @next/next/no-img-element */}
                                            <img src={current.asset_url} alt={slot.label} className="h-full w-full object-cover" />
                                        </div>
                                        <Button 
                                            variant="destructive" 
                                            size="sm" 
                                            className="w-full"
                                            onClick={() => handleDeleteAsset(current.id)}
                                        >
                                            <Trash2 className="w-4 h-4 mr-2" /> Remove
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <Button 
                                          variant="outline" 
                                          className="w-full h-24 flex-col gap-2 border-dashed"
                                          onClick={() => openGalleryForDefault(slot.role)}
                                        >
                                           <div className="flex items-center justify-center h-8 w-8 rounded-full bg-slate-100">
                                             <Plus className="h-4 w-4" />
                                           </div>
                                           <span className="text-xs text-muted-foreground">Select from Library</span>
                                        </Button>
                                        
                                        <Label className="cursor-pointer border-dashed border-2 rounded-lg flex flex-col items-center justify-center h-12 hover:bg-slate-50 transition-colors">
                                            <span className="text-xs text-muted-foreground">Or Upload File</span>
                                            <input 
                                                type="file" 
                                                className="hidden" 
                                                accept="image/*"
                                                onChange={(e) => handleFileUpload(e, ASSET_TYPES.DEFAULT, slot.role)}
                                            />
                                        </Label>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    );
                })}
             </div>
        </TabsContent>
        </Tabs>

      <ImageGalleryModal
          open={isGalleryOpen}
          onOpenChange={setIsGalleryOpen}
          onSelect={handleGallerySelect}
          limit={1}
      />
    </div>
  );
}

