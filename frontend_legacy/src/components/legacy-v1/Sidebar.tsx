import React, { useState, useEffect } from 'react';
import { LayoutDashboard, LineChart, Bot, Layers, Settings, Zap, X, Sword, ChevronRight, LogOut } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = false, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const pathname = usePathname();

  // Combined: My mobile detection + Jules' cleanup pattern
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    // Cleanup to prevent memory leaks (from Jules)
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Sync external isOpen prop with internal expanded state on mobile
  useEffect(() => {
    if (isMobile) {
      setIsExpanded(isOpen);
    }
  }, [isMobile, isOpen]);

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: LineChart, label: 'Analytics', href: '/dashboard/analytics' },
    { icon: Bot, label: 'AI Agents', href: '/dashboard/agents' },
    { icon: Layers, label: 'Positions', href: '/dashboard/positions' },
    { icon: Sword, label: 'War Room', href: '/dashboard/shadow-center' },
    { icon: Zap, label: 'Automation', href: '/dashboard/automation' },
    { icon: Settings, label: 'Settings', href: '/settings' },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-full bg-[#050505]/95 backdrop-blur-md border-r border-white/5 z-50 transition-all duration-300 ease-in-out flex flex-col justify-between overflow-hidden
        ${isMobile ? (isExpanded ? 'w-64' : 'w-0') : (isExpanded ? 'w-64' : 'w-20')}
      `}
      onMouseEnter={() => !isMobile && setIsExpanded(true)}
      onMouseLeave={() => !isMobile && setIsExpanded(false)}
    >
      {/* Logo Section */}
      <div className="h-20 flex items-center justify-center border-b border-white/5 relative">
        <div className={`transition-all duration-300 flex items-center gap-3 ${isExpanded ? 'px-6 w-full' : ''}`}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-axiom-primary to-blue-600 flex items-center justify-center text-black font-bold text-xl shadow-[0_0_15px_rgba(0,255,136,0.3)] shrink-0">
            A
          </div>
          <div className={`overflow-hidden transition-all duration-300 ${isExpanded ? 'w-auto opacity-100' : 'w-0 opacity-0'}`}>
            <h1 className="font-bold text-lg tracking-wider text-white whitespace-nowrap">AXIOM</h1>
            <p className="text-[10px] text-gray-400 tracking-[0.2em] whitespace-nowrap">ANTIGRAVITY</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 py-6 flex flex-col gap-2 px-3 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.label} href={item.href}>
              <div className={`
                flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all duration-200 group relative
                ${isActive
                  ? 'bg-axiom-primary/10 text-axiom-primary border border-axiom-primary/20 shadow-[0_0_10px_rgba(0,255,136,0.1)]'
                  : 'hover:bg-white/5 text-gray-400 hover:text-white'}
              `}>
                <item.icon className={`w-5 h-5 shrink-0 transition-colors ${isActive ? 'text-axiom-primary' : 'group-hover:text-white'}`} />
                <span className={`text-sm font-medium whitespace-nowrap transition-all duration-200 ${isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 absolute left-12'}`}>
                  {item.label}
                </span>

                {/* Active Indicator (Dot) */}
                {isActive && isExpanded && (
                  <div className="absolute right-3 w-1.5 h-1.5 rounded-full bg-axiom-primary shadow-[0_0_4px_var(--neon-green)]"></div>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="p-3 border-t border-white/5">
        <button className={`
          w-full flex items-center gap-3 p-3 rounded-xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 group
        `}>
          <LogOut className="w-5 h-5 shrink-0 group-hover:text-red-400" />
          <span className={`text-sm font-medium whitespace-nowrap transition-all duration-200 ${isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 absolute'}`}>
            Logout
          </span>
        </button>
      </div>

      {/* Mobile Close Button */}
      {isMobile && isExpanded && (
        <button
          onClick={onClose}
          className="absolute top-6 right-4 p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      )}

      {/* Mobile Toggle */}
      {isMobile && !isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="fixed top-6 left-4 p-3 rounded-xl bg-[#050505]/90 backdrop-blur-md border border-white/10 text-white shadow-lg z-50"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      )}
    </aside>
  );
};

export default Sidebar;