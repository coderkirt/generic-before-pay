import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  allowedDevOrigins: ["127.0.0.1"],
  async rewrites() {
    return [
      {
        source: "/v1/:path*",
        destination: "http://127.0.0.1:8000/v1/:path*",
      },
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/healthz",
        destination: "http://127.0.0.1:8000/healthz",
      },
      {
        source: "/readyz",
        destination: "http://127.0.0.1:8000/readyz",
      },
    ];
  },
};

export default nextConfig;
