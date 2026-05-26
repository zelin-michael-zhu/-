import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ApplyPilot",
  description: "AI-powered Graduate Application OS"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
