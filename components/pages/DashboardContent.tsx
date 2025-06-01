
'use client'

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Bot, 
  Search, 
  FileText, 
  Send, 
  Bell, 
  BarChart3,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp
} from "lucide-react"
import { UserButton } from "@clerk/nextjs"
import Link from "next/link"
import { BidDiscoveryTab } from "@/components/dashboard/BidDiscoveryTab"
import { BidFillingTab } from "@/components/dashboard/BidFillingTab"
import { BidSubmittingTab } from "@/components/dashboard/BidSubmittingTab"
import { NotificationsTab } from "@/components/dashboard/NotificationsTab"
import { AnalyticsTab } from "@/components/dashboard/AnalyticsTab"
import { AgentStatusBanner } from "@/components/dashboard/AgentStatusBanner"

export const DashboardContent = () => {
  const [activeAgents, setActiveAgents] = useState([
    { name: "Discovery Agent", status: "idle" as const, lastActivity: "2 hours ago" },
    { name: "Analysis Agent", status: "idle" as const, lastActivity: "1 hour ago" },
    { name: "Pre-fill Agent", status: "idle" as const, lastActivity: "30 minutes ago" },
    { name: "Notification Agent", status: "idle" as const, lastActivity: "10 minutes ago" }
  ])

  const [dashboardStats, setDashboardStats] = useState({
    totalBids: 24,
    activeBids: 8,
    completedPreFills: 15,
    upcomingDeadlines: 3
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-2">
                <Bot className="w-8 h-8 text-blue-600" />
                <span className="text-2xl font-bold text-gray-900">BidAgents AI</span>
              </Link>
              <Badge variant="outline" className="text-green-600 border-green-600">
                Pro Plan
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Welcome back, <span className="font-semibold">User</span>
              </div>
              <UserButton />
            </div>
          </div>
        </div>
      </header>

      {/* Agent Status Banner */}
      <AgentStatusBanner agents={activeAgents} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Bids Found</p>
                  <p className="text-3xl font-bold text-gray-900">{dashboardStats.totalBids}</p>
                </div>
                <Search className="w-8 h-8 text-blue-600" />
              </div>
              <div className="mt-2 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                +12% this week
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Opportunities</p>
                  <p className="text-3xl font-bold text-gray-900">{dashboardStats.activeBids}</p>
                </div>
                <Clock className="w-8 h-8 text-orange-600" />
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Avg. deadline: 18 days
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pre-filled Ready</p>
                  <p className="text-3xl font-bold text-gray-900">{dashboardStats.completedPreFills}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Ready for submission
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Urgent Deadlines</p>
                  <p className="text-3xl font-bold text-gray-900">{dashboardStats.upcomingDeadlines}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <div className="mt-2 text-sm text-red-600">
                Due within 7 days
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="discovery" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="discovery" className="flex items-center space-x-2">
              <Search className="w-4 h-4" />
              <span>Discovery</span>
            </TabsTrigger>
            <TabsTrigger value="filling" className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Filling</span>
            </TabsTrigger>
            <TabsTrigger value="submitting" className="flex items-center space-x-2">
              <Send className="w-4 h-4" />
              <span>Submitting</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center space-x-2">
              <Bell className="w-4 h-4" />
              <span>Notifications</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="discovery">
            <BidDiscoveryTab />
          </TabsContent>

          <TabsContent value="filling">
            <BidFillingTab />
          </TabsContent>

          <TabsContent value="submitting">
            <BidSubmittingTab />
          </TabsContent>

          <TabsContent value="notifications">
            <NotificationsTab />
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}