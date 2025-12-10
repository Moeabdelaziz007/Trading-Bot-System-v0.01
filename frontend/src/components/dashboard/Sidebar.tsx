import React from 'react';
import { LayoutDashboard, LineChart, Bot, Layers, Settings, Zap, X, Sword } from 'lucide-react';
import Link from 'next/link';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void; // Add onClose callback
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  // Add resize listener to handle responsive behavior safely
  React.useEffect(() => {
    const handleResize = () => {
      // Logic to auto-close sidebar on small screens could go here
      // This is primarily to demonstrate the cleanup pattern requested
      if (window.innerWidth < 1024 && isOpen && onClose) {
        // We don't auto-close here to avoid annoying state changes during resize
        // but we keep the listener to ensure no memory leaks occur if logic is added
      }
    };

    window.addEventListener('resize', handleResize);

    // cleanup function to prevent memory leaks
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [isOpen, onClose]);

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard', active: true },
    { icon: LineChart, label: 'Analytics', href: '/dashboard/analytics', active: false },
    { icon: Bot, label: 'AI Agents', href: '/dashboard/agents', active: false },
    { icon: Layers, label: 'Positions', href: '/dashboard/positions', active: false },
    { icon: Sword, label: 'War Room', href: '/dashboard/shadow-center', active: false },
    { icon: Zap, label: 'Automation', href: '/dashboard/automation', active: false },
    { icon: Settings, label: 'Settings', href: '/dashboard/settings', active: false },
  ];

  return (
    <aside className={`fixed top-0 left-0 h-full bg-[#0D0D0D] border-r border-white/5 z-40 transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-0 lg:w-20'} overflow-hidden`}>
      <div className="flex items-center justify-between h-16 border-b border-white/5 px-4">
        <div className="flex items-center">
          <div className={`w-8 h-8 rounded bg-gradient-to-br from-axiom-primary to-blue-600 flex items-center justify-center text-black font-bold text-xl shadow-[0_0_15px_rgba(0,255,136,0.4)] ${isOpen ? 'mr-3' : 'mr-0'}`}>
            A
          </div>
          {isOpen && <span className="font-bold text-xl tracking-tight text-white">AXIOM</span>}
        </div>
        {/* Close button - only visible when sidebar is open */}
        {isOpen && (
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <nav className="p-4 space-y-2 mt-4">
        {navItems.map((item) => (
          <Link key={item.label} href={item.href}>
            <button
              className={`w-full flex items-center p-3 rounded-xl transition-all duration-200 group ${
                item.active 
                  ? 'bg-axiom-surface text-axiom-secondary border border-axiom-secondary/20 shadow-[0_0_10px_rgba(0,217,255,0.1)]' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              } ${!isOpen ? 'justify-center' : ''}`}
            >
              <item.icon className={`w-5 h-5 ${item.active ? 'text-axiom-secondary' : 'group-hover:text-white'} ${isOpen ? 'mr-3' : ''}`} />
              {isOpen && <span className="font-medium text-sm">{item.label}</span>}
              {item.active && isOpen && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-axiom-secondary shadow-[0_0_5px_#00D9FF]"></div>}
            </button>
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-8 left-0 w-full px-4">
        <div className={`p-4 rounded-xl bg-gradient-to-br from-axiom-card to-[#000] border border-white/10 ${!isOpen ? 'hidden' : 'block'}`}>
          <div className="flex items-center gap-3 mb-3">
             <div className="w-8 h-8 rounded-full bg-axiom-tertiary/20 flex items-center justify-center text-axiom-tertiary">
               <Zap size={16} />
             </div>
             <div>
               <div className="text-xs text-gray-400">System Status</div>
               <div className="text-xs font-bold text-axiom-primary neon-text-primary">OPTIMAL</div>
             </div>
          </div>
        </div>
      </div>
    </aside>
  );
};