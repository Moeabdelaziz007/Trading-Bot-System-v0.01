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

  return (
    <div className="min-h-screen bg-axiom-bg text-gray-300 font-sans selection:bg-axiom-secondary/30 selection:text-white">
      <Sidebar isOpen={isSidebarOpen} />
      
      <div className={`transition-all duration-300 ${isSidebarOpen ? 'lg:pl-64' : 'lg:pl-20'}`}>
        <Header toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
        
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
      
      {/* Mobile overlay for sidebar */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default App;
