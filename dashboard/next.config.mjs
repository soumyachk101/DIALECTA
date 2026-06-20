/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/v1/:path*", destination: `${process.env.BACKEND_URL ?? "http://localhost:8000"}/v1/:path*` },
    ];
  },
};
export default nextConfig;
