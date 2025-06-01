import './globals.css'
import React from 'react'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import { Toaster } from "@/components/ui/toaster"
import { Toaster as Sonner } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"
import { ClientProviders } from './client-providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'BidAgents AI',
  description: 'Automate your procurement process with AI agents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          <ClientProviders>
            <TooltipProvider>
              {children}
              <Toaster />
              <Sonner />
            </TooltipProvider>
          </ClientProviders>
        </body>
      </html>
    </ClerkProvider>
  )
}