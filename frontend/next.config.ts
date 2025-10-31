import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        hostname: "media-cdn.tripadvisor.com"
      }
    ]
  }
};

export default nextConfig;
