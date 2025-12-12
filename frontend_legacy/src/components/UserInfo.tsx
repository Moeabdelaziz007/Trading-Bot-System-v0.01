'use client';

import { useState, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';

interface ApiData {
  userId: string;
  createdAt: string;
}

export function UserInfo() {
  const { isLoaded, isSignedIn, user } = useUser();
  const [apiData, setApiData] = useState<ApiData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isSignedIn) {
      fetchUserData();
    }
  }, [isSignedIn]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/user');
      const data = await response.json();
      setApiData(data);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    return <div>Please sign in to view user information.</div>;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-4">User Information</h2>

      <div className="space-y-2">
        <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
        <p><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</p>
        <p><strong>User ID:</strong> {user?.id}</p>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">API Data</h3>
        {loading ? (
          <p>Loading API data...</p>
        ) : apiData ? (
          <div className="space-y-2">
            <p><strong>API User ID:</strong> {apiData.userId}</p>
            <p><strong>Created At:</strong> {new Date(apiData.createdAt).toLocaleString()}</p>
          </div>
        ) : (
          <p>No API data available.</p>
        )}
      </div>
    </div>
  );
}