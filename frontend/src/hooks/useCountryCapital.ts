import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const countryTranslations: Record<string, string> = {
  "Maroc": "Morocco",
  "France": "France",
  "Espagne": "Spain",
  "Italie": "Italy",
  "Allemagne": "Germany",
  "États-Unis": "United States",
  "Canada": "Canada",
  "Tunisie": "Tunisia",
  "Sénégal": "Senegal",
  "Côte d'Ivoire": "Ivory Coast",
  "Tchad": "Chad",
};

const getEnglishCountryName = (country: string): string =>
  countryTranslations[country] || country;

export const fetchCapital = async (countryName: string) => {
  const englishName = getEnglishCountryName(countryName);
  const res = await axios.get(
    `https://restcountries.com/v3.1/name/${englishName}?fullText=true`
  );
  const data = res.data[0];
  return {
    capital: data.capital?.[0] || "Inconnue",
    region: data.region,
    flag: data.flags?.png,
    latlng: data.latlng,
  };
};

export const useCountryCapital = (countryName: string) => {
  const englishName = getEnglishCountryName(countryName);
  return useQuery({
    queryKey: ["countryCapital", englishName],
    queryFn: () => fetchCapital(englishName),
    enabled: !!countryName,
  });
};

// 🧩 Ajout de la méthode statique
useCountryCapital.fetchCapital = fetchCapital;
