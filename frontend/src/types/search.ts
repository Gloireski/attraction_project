export type SearchFilters = {
  country?: string;
  city?: string;
  profile_type?: string;
  capital?: string;
  categories?: string[];
  category?: string;
  minReviews?: number;
  minPhotos?: number;
  priceLevel?: string;
  openNow?: boolean; // pour filtrer les attractions actuellement ouvertes
};

