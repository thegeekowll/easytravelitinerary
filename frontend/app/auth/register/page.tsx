'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Registration
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Easy. Travel Itinerary Builder
          </p>
        </div>

        <div className="mt-8 space-y-6 bg-white p-8 rounded-lg shadow">
          <div className="text-center">
            <p className="text-gray-700 mb-4">
              User accounts are created by system administrators only.
            </p>
            <p className="text-sm text-gray-600 mb-6">
              If you need an account, please contact your system administrator.
            </p>
            <Link href="/auth/login">
              <Button>Back to Login</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
