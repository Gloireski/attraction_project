'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, User } from 'lucide-react';
import { useLogoutUser, useUserSession } from '@/hooks/useUserSession';

const navLinks = [
  { name: 'Home', href: '/home' },
  { name: 'Search', href: '/search'},
  // { name: 'Attractions', href: '/attractions' },
  { name: 'Compilations', href: '/compilations' },
];

export default function Header() {
  const [open, setOpen] = useState(false);
  const { data: user } = useUserSession(); // <-- your hook returning user session data
  const { mutateAsync: logout, isLoading: isLoggingOut } = useLogoutUser();

  console.log("session: ", user?.session_key)

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold text-blue-600">
          🌍 ExploreNow
        </Link>

        {/* Desktop Menu */}
        <ul className="hidden md:flex space-x-8 text-gray-700 font-medium">
          {navLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="hover:text-blue-600 transition-colors duration-200"
              >
                {link.name}
              </Link>
            </li>
          ))}

          {/* User Profile */}
          {user ? (
            <li className="flex items-center space-x-3 border-l pl-4 border-gray-300">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold">
                  <User size={18} />
                </div>
                <div className="flex flex-col leading-tight">
                  <span className="font-semibold text-gray-800">{user.profile_type}</span>
                  {user.country && (
                    <span className="text-sm text-gray-500">{user.country}</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => logout()}
                disabled={isLoggingOut}
                className="ml-4 px-3 py-1.5 text-sm font-medium bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition"
              >
                {isLoggingOut ? '...' : 'Logout'}
              </button>
            </li>
          ) : (
            <li>
              <Link
                href="/"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Login
              </Link>
            </li>
          )}

        </ul>
        

        {/* Mobile Menu Button */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden p-2 rounded-md hover:bg-gray-100 transition"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {/* Mobile Dropdown */}
      {open && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <ul className="flex flex-col p-4 space-y-3 text-gray-700 font-medium">
            {navLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block hover:text-blue-600 transition-colors"
                >
                  {link.name}
                </Link>
              </li>
            ))}

            {/* Mobile User Section */}
            {user ? (
              <li className="pt-3 border-t border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold">
                    <User size={18} />
                  </div>
                  <div className="flex flex-col">
                    <span className="font-semibold text-gray-800">{user.profile_type}</span>
                    {user.country && (
                      <span className="text-sm text-gray-500">{user.country}</span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setOpen(false);
                  }}
                  disabled={isLoggingOut}
                  className="mt-3 w-full py-2 bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition"
                >
                  {isLoggingOut ? '...' : 'Logout'}
                </button>
              </li>
            ) : (
              <li>
                <Link
                  href="/"
                  onClick={() => setOpen(false)}
                  className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  Login
                </Link>
              </li>
            )}

          </ul>
        </div>
      )}
    </header>
  );
}