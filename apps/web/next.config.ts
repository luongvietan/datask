import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API proxy to FastAPI backend in dev
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/v1/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "api.datask.run" },
    ],
  },
};

export default nextConfig;
