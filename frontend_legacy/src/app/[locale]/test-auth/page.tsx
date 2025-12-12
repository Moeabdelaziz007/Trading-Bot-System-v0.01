'use client';

import { SignedIn, SignedOut, SignInButton, SignOutButton, UserButton } from '@clerk/nextjs';
import { UserInfo } from '@/components/UserInfo';

export default function AuthTestPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Authentication Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Authentication Status */}
          <div className="bg-gray-900 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
            
            <SignedIn>
              <div className="space-y-4">
                <p className="text-green-400">You are signed in!</p>
                <div className="flex items-center gap-4">
                  <UserButton />
                  <SignOutButton>
                    <button className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition-colors">
                      Sign Out
                    </button>
                  </SignOutButton>
                </div>
              </div>
            </SignedIn>
            
            <SignedOut>
              <div className="space-y-4">
                <p className="text-yellow-400">You are not signed in</p>
                <SignInButton>
                  <button className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors">
                    Sign In
                  </button>
                </SignInButton>
              </div>
            </SignedOut>
          </div>
          
          {/* User Information */}
          <div className="bg-gray-900 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">User Information</h2>
            <UserInfo />
          </div>
        </div>
      </div>
    </div>
  );
}