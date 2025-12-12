'use client';

import { Sidebar } from '@/components/dashboard/Sidebar';
import { Header } from '@/components/dashboard/Header';
import { SelfPlayLearningLoop } from '@/components/dashboard/SelfPlayLearningLoop';
import { useState } from 'react';
import { SignedIn, SignedOut } from '@clerk/nextjs';

export default function SelfPlayDashboardPage() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    // Function to close the sidebar
    const closeSidebar = () => {
        setIsSidebarOpen(false);
    };

    // Function to toggle sidebar
    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="min-h-screen bg-axiom-bg text-gray-300 font-sans">
            <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

            <div className={`transition-all duration-300 ${isSidebarOpen ? 'lg:pl-64' : 'lg:pl-20'}`}>
                <Header toggleSidebar={toggleSidebar} />
                
                <main className="p-4 lg:p-6 max-w-[1600px] mx-auto">
                    <SignedIn>
                        <div className="mb-6">
                            <h1 className="text-2xl font-bold font-mono text-white mb-2">Self-Play Learning Loop</h1>
                            <p className="text-gray-400">
                                Monitor the adversarial AI agents and evolutionary optimization in real-time
                            </p>
                            <div className="mt-4">
                                <a 
                                    href="/dashboard/shadow-center" 
                                    className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg font-mono text-sm hover:from-purple-700 hover:to-indigo-700 transition-all duration-300"
                                >
                                    <span>Enter War Room</span>
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-2" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                </a>
                            </div>
                        </div>
                        
                        <SelfPlayLearningLoop />
                    </SignedIn>
                    
                    <SignedOut>
                        <div className="flex flex-col items-center justify-center h-[70vh] text-center">
                            <h1 className="text-3xl font-bold mb-4">Access Restricted</h1>
                            <p className="text-gray-400 mb-8 max-w-2xl">
                                Please sign in to access the Self-Play Learning Loop dashboard with real-time 
                                monitoring of AI agents and evolutionary optimization.
                            </p>
                            <div className="bg-gradient-to-r from-axiom-primary to-blue-500 p-1 rounded-full">
                                <button 
                                    className="bg-axiom-bg px-6 py-3 rounded-full font-semibold hover:bg-axiom-bg/90 transition-colors"
                                    onClick={() => window.location.href = '/sign-in'}
                                >
                                    Sign In to Continue
                                </button>
                            </div>
                        </div>
                    </SignedOut>
                </main>
            </div>
            
            {/* Overlay for sidebar - now works on all screen sizes */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
                    onClick={closeSidebar}
                />
            )}
        </div>
    );
}