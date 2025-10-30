import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-10 border-t border-gray-200 bg-gray-50 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-3">
        <p className="text-gray-600 text-sm">
          © {new Date().getFullYear()} <span className="font-semibold">ExploreNow</span>. All rights reserved.
        </p>

        <div className="flex space-x-6 text-sm text-gray-600">
          <Link href="/privacy" className="hover:text-blue-600">Privacy</Link>
          <Link href="/terms" className="hover:text-blue-600">Terms</Link>
          <Link href="/contact" className="hover:text-blue-600">Contact</Link>
        </div>
      </div>
    </footer>
  );
}
