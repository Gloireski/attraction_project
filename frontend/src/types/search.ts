export type SearchFilters = {
  country?: string;
  city?: string;
  profile_type?: string;
  category?: string;
  days?: string;
  radius: number;
  minReviews?: number;
  minPhotos?: number;
  priceLevel?: string;
  openNow?: boolean; // pour filtrer les attractions actuellement ouvertes
};

