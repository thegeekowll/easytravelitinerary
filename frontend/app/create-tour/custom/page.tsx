'use client';

import BaseTourForm from '@/components/tours/base-tour-form';

export default function CustomBuilderPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Build Custom Itinerary</h1>
        <p className="text-muted-foreground">
          Create a unique itinerary from scratch using the tour builder.
        </p>
      </div>
      
      <BaseTourForm isCustomItinerary={true} />
    </div>
  );
}
