'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { Loader2, Trash2, Search, ImageIcon } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

interface MediaItem {
    id: string;
    url: string;
    caption?: string;
    source_type: string;
    source_name: string;
    created_at: string;
}

export default function ImageGalleryPage() {
    const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterType, setFilterType] = useState<string>('all');
    
    // Pagination state (simple infinite scroll or load more for MVP)
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [isFetchingMore, setIsFetchingMore] = useState(false);

    const fetchMedia = useCallback(async (pageNum: number, search: string, type: string, isLoadMore = false) => {
        try {
            if (!isLoadMore) setIsLoading(true);
            else setIsFetchingMore(true);

            const params: any = {
                page: pageNum,
                limit: 24, // good grid size
            };
            
            if (search) params.search = search;
            if (type !== 'all') params.source_type = type;

            const res = await apiClient.getMediaLibrary(params);
            
            if (isLoadMore) {
                setMediaItems(prev => [...prev, ...res.items]);
            } else {
                setMediaItems(res.items);
            }
            
            setHasMore(pageNum < res.pages);
            
        } catch (error) {
            console.error("Failed to fetch media:", error);
            toast.error("Failed to load image gallery");
        } finally {
            setIsLoading(false);
            setIsFetchingMore(false);
        }
    }, []);

    // Initial load and filter changes
    useEffect(() => {
        setPage(1);
        fetchMedia(1, searchQuery, filterType, false);
    }, [searchQuery, filterType, fetchMedia]);

    const handleLoadMore = () => {
        if (!hasMore || isFetchingMore) return;
        const nextPage = page + 1;
        setPage(nextPage);
        fetchMedia(nextPage, searchQuery, filterType, true);
    };

    const handleDelete = async (item: MediaItem) => {
        if (!confirm(`Are you sure you want to delete this image? It will be removed from ${item.source_name}.`)) return;

        const toastId = toast.loading('Deleting image...');
        try {
            // Need a specific endpoint format based on source_type, or rely on media.py delete endpoint
            await apiClient.deleteMediaImage(item.source_type, item.id);
            toast.success('Image deleted from system', { id: toastId });
            
            // Remove from local state
            setMediaItems(prev => prev.filter(img => img.id !== item.id));
        } catch (error: any) {
            const msg = error.response?.data?.detail || "Delete failed";
            toast.error(`Error: ${msg}`, { id: toastId });
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Image Gallery</h1>
                    <p className="text-muted-foreground">Manage and view all images across destinations, accommodations, tours, and company assets.</p>
                </div>
            </div>

            <Card>
                <CardContent className="p-4 sm:p-6">
                    {/* Filters & Search */}
                    <div className="flex flex-col sm:flex-row gap-4 mb-6">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input 
                                placeholder="Search by caption or source name..." 
                                className="pl-9"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                        <div className="w-full sm:w-[200px]">
                            <Select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                                <option value="all">All Sources</option>
                                <option value="destination">Destinations</option>
                                <option value="accommodation">Accommodations</option>
                                <option value="itinerary">Itineraries / Tours</option>
                                <option value="company_asset">Company Assets</option>
                            </Select>
                        </div>
                    </div>

                    {/* Gallery Grid */}
                    {isLoading ? (
                        <div className="py-20 flex justify-center">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : mediaItems.length === 0 ? (
                        <div className="py-20 text-center flex flex-col items-center text-muted-foreground">
                            <ImageIcon className="h-12 w-12 mb-4 opacity-20" />
                            <p className="font-medium text-lg">No Images Found</p>
                            <p className="text-sm">Try adjusting your search or filter criteria.</p>
                        </div>
                    ) : (
                        <div className="space-y-8">
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                                {mediaItems.map((item) => (
                                    <div key={item.id} className="group relative rounded-lg border bg-slate-50 overflow-hidden flex flex-col">
                                        <div className="aspect-square w-full relative overflow-hidden bg-muted">
                                            {/* eslint-disable-next-line @next/next/no-img-element */}
                                            <img 
                                                src={item.url} 
                                                alt={item.caption || 'Gallery Image'} 
                                                className="absolute inset-0 w-full h-full object-cover transition-transform group-hover:scale-105"
                                                loading="lazy"
                                            />
                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-[1px]">
                                                {/* Open Full Size button (optional future enhancement) */}
                                                <Button 
                                                    variant="destructive" 
                                                    size="icon" 
                                                    className="h-8 w-8 rounded-full shadow-sm"
                                                    onClick={() => handleDelete(item)}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                            <div className="absolute top-2 left-2 bg-black/60 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded shadow-sm opacity-90">
                                                {item.source_type.replace('_', ' ')}
                                            </div>
                                        </div>
                                        <div className="p-2 border-t bg-white">
                                            <p className="text-xs font-medium truncate text-slate-800" title={item.caption || 'No Caption'}>
                                                {item.caption || 'No Caption'}
                                            </p>
                                            <p className="text-[10px] text-muted-foreground truncate" title={item.source_name}>
                                                Source: {item.source_name}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Load More Button */}
                            {hasMore && (
                                <div className="flex justify-center pt-4">
                                    <Button 
                                        variant="outline" 
                                        onClick={handleLoadMore}
                                        disabled={isFetchingMore}
                                        className="w-full sm:w-auto min-w-[200px]"
                                    >
                                        {isFetchingMore ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading...</>
                                        ) : (
                                            'Load More Images'
                                        )}
                                    </Button>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
