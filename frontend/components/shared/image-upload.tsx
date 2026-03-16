'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, X, Loader2 } from 'lucide-react';
import Image from 'next/image';

interface ImageUploadProps {
  onImagesSelected: (files: File[]) => void;
  maxFiles?: number;
  existingImages?: { id: string; url: string; caption?: string }[];
  onDeleteExisting?: (id: string) => void;
  disabled?: boolean;
}

export default function ImageUpload({ 
  onImagesSelected, 
  maxFiles = 5,
  existingImages = [],
  onDeleteExisting,
  disabled = false
}: ImageUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      if (selectedFiles.length + newFiles.length > maxFiles) {
        alert(`You can only upload up to ${maxFiles} images.`);
        return;
      }
      
      setSelectedFiles(prev => [...prev, ...newFiles]);
      onImagesSelected([...selectedFiles, ...newFiles]);

      // Create previews
      newFiles.forEach(file => {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviews(prev => [...prev, reader.result as string]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    setPreviews(newPreviews);
    onImagesSelected(newFiles);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        {/* Existing Images */}
        {existingImages.map((img) => (
          <div key={img.id} className="relative w-32 h-32 rounded-lg overflow-hidden border bg-gray-100 group">
             <Image 
               src={img.url} 
               alt={img.caption || 'Accommodation Image'} 
               fill 
               className="object-cover"
             />
             {onDeleteExisting && !disabled && (
               <button
                 type="button"
                 onClick={() => onDeleteExisting(img.id)}
                 className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
               >
                 <X className="h-4 w-4" />
               </button>
             )}
          </div>
        ))}

        {/* New File Previews */}
        {previews.map((preview, index) => (
          <div key={`new-${index}`} className="relative w-32 h-32 rounded-lg overflow-hidden border bg-gray-100 group">
             <Image 
               src={preview} 
               alt="New upload" 
               fill 
               className="object-cover"
             />
             {!disabled && (
               <button
                 type="button"
                 onClick={() => removeFile(index)}
                 className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
               >
                 <X className="h-4 w-4" />
               </button>
             )}
          </div>
        ))}

        {/* Upload Button */}
        {(existingImages.length + selectedFiles.length) < maxFiles && !disabled && (
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-primary hover:bg-gray-50 transition-colors"
          >
            <Upload className="h-8 w-8 text-gray-400 mb-2" />
            <span className="text-xs text-gray-500 font-medium">Add Image</span>
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="image/*" 
              multiple 
              onChange={handleFileSelect}
            />
          </div>
        )}
      </div>
    </div>
  );
}
