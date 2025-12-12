import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { BotScores } from './components/BotScores';
import { PriceChart } from './components/PriceChart';
import { AutomationPipeline } from './components/AutomationPipeline';
import { TransactionsTable } from './components/TransactionsTable';
import { TrendingTopics } from './components/TrendingTopics';
import { PatternRecognition } from './components/PatternRecognition';

const App: React.FC = () => {
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
    <div className="min-h-screen bg-axiom-bg text-gray-300 font-sans selection:bg-axiom-secondary/30 selection:text-white">
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
      
      <div className={`transition-all duration-300 ${isSidebarOpen ? 'lg:pl-64' : 'lg:pl-20'}`}>
        <Header toggleSidebar={toggleSidebar} />
        
        <main className="p-4 lg:p-6 max-w-[1600px] mx-auto space-y-6">
          
          {/* Top Grid: Bot Scores & Price Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 xl:col-span-3">
              <BotScores />
            </div>
            <div className="lg:col-span-8 xl:col-span-9 h-[400px] lg:h-auto">
              <PriceChart />
            </div>
          </div>

          {/* Middle Grid: Pipeline, Trending, Patterns */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 xl:col-span-3">
               <AutomationPipeline />
            </div>
            <div className="lg:col-span-4 xl:col-span-4">
              <TrendingTopics />
            </div>
             <div className="lg:col-span-4 xl:col-span-5">
              <PatternRecognition />
            </div>
          </div>

          {/* Bottom: Transactions */}
          <div className="grid grid-cols-1">
            <TransactionsTable />
          </div>

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
};

export default App;