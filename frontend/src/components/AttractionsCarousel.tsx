'use client';

import type { Attraction } from '@/types/attractions';
import AttractionCard from './AttractionCard';

type Props = { attractions: Attraction[] };

export default function AttractionsCarousel({ attractions }: Props) {
  return (
    <div className="overflow-x-auto flex gap-4 pb-4 snap-x scroll-smooth">
      {attractions.map((a, index) => (
        <div key={`${a.id}-${index}`} className="snap-center shrink-0 w-72">
          <AttractionCard attraction={a} />
        </div>
      ))}
    </div>
  );
}
