import React from 'react';
import { Search, Bell, Menu, Send } from 'lucide-react';

interface HeaderProps {
  toggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ toggleSidebar }) => {
  return (
    <header className="h-16 border-b border-white/5 bg-[#0D0D0D]/80 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-4 lg:px-8">
      <div className="flex items-center gap-4">
        <button onClick={toggleSidebar} className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/5 lg:hidden">
          <Menu className="w-5 h-5" />
        </button>
        
        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input 
            type="text" 
            placeholder="Search markets..." 
            className="bg-[#13131F] border border-white/5 rounded-full py-2 pl-10 pr-4 text-sm text-gray-300 focus:outline-none focus:border-axiom-secondary/50 focus:ring-1 focus:ring-axiom-secondary/50 w-64 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg border border-axiom-secondary/30 text-axiom-secondary text-sm font-medium hover:bg-axiom-secondary/10 transition-colors shadow-[0_0_10px_rgba(0,217,255,0.1)]">
          <Send className="w-4 h-4" />
          <span>Connect Telegram</span>
        </button>

        <div className="relative">
          <button className="p-2 text-gray-400 hover:text-white transition-colors relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-axiom-danger rounded-full border border-[#0D0D0D]"></span>
          </button>
        </div>

        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-gray-700 to-gray-600 border border-white/20 overflow-hidden cursor-pointer hover:border-axiom-primary transition-colors">
            <img src="https://picsum.photos/100/100" alt="User" className="w-full h-full object-cover opacity-80 hover:opacity-100" />
        </div>
      </div>
    </header>
  );
};
