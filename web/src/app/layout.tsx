import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { GamificationProvider } from "@/context/gamification-context";
import { Navbar } from "@/components/navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BPR&D Gameified",
  description: "Internal and public face of BPR&D",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <GamificationProvider>
          <div className="flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1">{children}</main>
          </div>
        </GamificationProvider>
      </body>
    </html>
  );
}
