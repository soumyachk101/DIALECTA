import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DIALECTA — Decision Log",
  description: "Review the debates that ran before each decision you made.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
