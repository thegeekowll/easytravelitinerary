'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Map, Copy, PlusCircle } from 'lucide-react';
import TravelerIntakeForm, { TravelerIntakeData } from '@/components/tours/traveler-intake-form';

export default function CreateTourPage() {
  const router = useRouter(); 
  const [step, setStep] = useState(1);
  const [intakeData, setIntakeData] = useState<TravelerIntakeData | null>(null);

  useEffect(() => {
    // Clear previous sessions when starting fresh
    sessionStorage.removeItem('draft_traveler_info');
  }, []);

  const handleIntakeSubmit = (data: TravelerIntakeData) => {
    setIntakeData(data);
    sessionStorage.setItem('draft_traveler_info', JSON.stringify(data));
    setStep(2);
  };

  const creationMethods = [
    {
      title: 'Choose Existing Package',
      description: 'Select from our 200+ base tour packages. Creates an exact copy.',
      icon: Copy,
      action: () => router.push('/create-tour/choose'),
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Edit Existing Package',
      description: 'Start with a base package and customize destinations, days, and accommodations.',
      icon: Map,
      action: () => router.push('/create-tour/choose?mode=edit'),
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Build from Scratch',
      description: 'Create a completely custom itinerary day by day.',
      icon: PlusCircle,
      action: () => router.push('/create-tour/custom'),
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];
  
  return (
    <div className="space-y-6 max-w-4xl mx-auto py-8">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="icon" onClick={() => step === 1 ? router.back() : setStep(1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {step === 1 ? 'Traveler Details' : 'Select Creation Method'}
          </h1>
          <p className="text-gray-600">
            {step === 1 ? 'Enter the primary traveler details to get started' : 'How would you like to build this itinerary?'}
          </p>
        </div>
      </div>

      {step === 1 ? (
        <Card>
            <CardContent className="pt-6">
                <TravelerIntakeForm onSubmit={handleIntakeSubmit} />
            </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {creationMethods.map((method, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={method.action}>
                <CardHeader>
                <div className={`w-12 h-12 rounded-lg ${method.bgColor} flex items-center justify-center mb-4`}>
                    <method.icon className={`h-6 w-6 ${method.color}`} />
                </div>
                <CardTitle>{method.title}</CardTitle>
                </CardHeader>
                <CardContent>
                <p className="text-gray-600">{method.description}</p>
                </CardContent>
                <CardFooter>
                <Button className="w-full" variant="outline">Select</Button>
                </CardFooter>
            </Card>
            ))}
        </div>
      )}
    </div>
  );
}
