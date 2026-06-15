"use client";

import { Search, Bell, User, X, Check, Info, LogOut } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/utils/supabase/client";

export function TopAppBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/companies?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between px-8 backdrop-blur-md bg-surface-lowest/80 border-b border-surface-bright/30">
      <div className="flex flex-1 items-center gap-4">
        <form onSubmit={handleSearch} className="relative w-full max-w-md">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-4 w-4 text-on-surface-variant" />
          </div>
          <input
            type="text"
            className="w-full bg-surface-low border border-surface-bright/30 rounded-full pl-10 pr-12 py-1.5 text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
            placeholder="Search entities, signals, or topics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <span className="text-xs font-mono text-on-surface-variant/50 border border-surface-bright/30 rounded px-1.5 py-0.5">⌘K</span>
          </div>
        </form>
      </div>

      <div className="flex items-center gap-4 relative">
        <div className="relative" ref={profileRef}>
          <button 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="h-8 w-8 rounded-full bg-surface-bright/30 border border-surface-bright/50 flex items-center justify-center text-on-surface hover:border-primary/50 transition-colors"
          >
            <User className="h-4 w-4" />
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-surface border border-surface-bright/30 rounded-xl shadow-lg shadow-black/50 overflow-hidden z-50 animate-slide-up origin-top-right">
              <div className="px-4 py-3 border-b border-surface-bright/20">
                <p className="text-sm font-medium text-on-surface">Operator Session</p>
              </div>
              <div className="p-2">
                <button 
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-status-danger hover:bg-status-danger/10 rounded-lg transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  Terminate Session
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}