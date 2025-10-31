'use client';

import { ReactNode } from 'react';
import { SelectedAttractionsProvider } from '@/context/SelectedAttractionsContext';
import ReactQueryProvider from '@/context/QueryClientProvider';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ReactQueryProvider>
      <SelectedAttractionsProvider>
        {children}
      </SelectedAttractionsProvider>
    </ReactQueryProvider>
  );
}
