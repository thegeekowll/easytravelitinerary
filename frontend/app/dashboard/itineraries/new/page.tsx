'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// This page is kept for backwards compatibility but always redirects
// to the canonical /create-tour flow used by all roles.
export default function NewItineraryPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/create-tour');
  }, [router]);
  return null;
}
