import AuthWrapper from "@/components/AuthWrapper";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TourWithEase AI",
  description: "GKE Turns 10 Hackathon - Travel AI Demo",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        <AuthWrapper>{children}</AuthWrapper>
      </body>
    </html>
  );
}
