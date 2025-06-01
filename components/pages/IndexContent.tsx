
'use client'

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Bot, FileText, Search, Zap, CheckCircle, Users, Award } from "lucide-react"
import Link from "next/link"
import { SignInButton, SignUpButton, useUser } from "@clerk/nextjs"

export const IndexContent = () => {
  const [email, setEmail] = useState("")
  const [isSubscribed, setIsSubscribed] = useState(false)
  const { isSignedIn } = useUser()

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubscribed(true)
    setEmail("")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Bot className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">BidAgents AI</span>
            </div>
            <div className="flex items-center space-x-4">
              {isSignedIn ? (
                <Link href="/dashboard">
                  <Button variant="outline">Dashboard</Button>
                </Link>
              ) : (
                <>
                  <SignInButton>
                    <Button variant="outline">Sign In</Button>
                  </SignInButton>
                  <SignUpButton>
                    <Button>Get Started</Button>
                  </SignUpButton>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge className="mb-4 bg-blue-100 text-blue-800">
            🏆 Google Agent Development Kit Winner
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Stop Searching—
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Start Winning
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            BidAgents AI automates your entire procurement process. Our intelligent agents discover, 
            download, analyze, and pre-fill bid documents so you can focus on winning contracts.
          </p>
          
          {/* Email Capture */}
          <div className="max-w-md mx-auto mb-12">
            {!isSubscribed ? (
              <form onSubmit={handleEmailSubmit} className="flex gap-2">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="flex-1"
                />
                <Button type="submit" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  Get Early Access
                </Button>
              </form>
            ) : (
              <div className="flex items-center justify-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                Thanks! We'll be in touch soon.
              </div>
            )}
          </div>

          {/* Demo Video Placeholder */}
          <div className="relative max-w-4xl mx-auto">
            <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-2xl flex items-center justify-center">
              <div className="text-center text-white">
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <div className="w-6 h-6 bg-white rounded-full"></div>
                </div>
                <p className="text-xl font-semibold">Product Demo Coming Soon</p>
                <p className="text-gray-300">See BidAgents AI in action</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Powered by Advanced AI Agents
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our intelligent agent network works 24/7 to streamline your bidding process
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-blue-500">
              <CardHeader>
                <Search className="w-12 h-12 text-blue-600 mb-2" />
                <CardTitle>Smart Discovery</CardTitle>
                <CardDescription>
                  AI agents automatically scan 50+ procurement portals, finding relevant opportunities based on your profile
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• SAM.gov integration</li>
                  <li>• State/local portals</li>
                  <li>• Real-time notifications</li>
                  <li>• NAICS code filtering</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-purple-500">
              <CardHeader>
                <FileText className="w-12 h-12 text-purple-600 mb-2" />
                <CardTitle>Intelligent Analysis</CardTitle>
                <CardDescription>
                  Advanced document AI extracts key requirements and deadlines from complex bid documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Document AI parsing</li>
                  <li>• Requirement extraction</li>
                  <li>• Deadline tracking</li>
                  <li>• Compliance checking</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-green-500">
              <CardHeader>
                <Zap className="w-12 h-12 text-green-600 mb-2" />
                <CardTitle>Auto Pre-Fill</CardTitle>
                <CardDescription>
                  Automatically populate bid forms with your company data, saving hours of manual entry
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Smart form mapping</li>
                  <li>• Company data sync</li>
                  <li>• PDF generation</li>
                  <li>• Quality validation</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">95%</div>
              <div className="text-blue-100">Time Saved</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">50+</div>
              <div className="text-blue-100">Portals Monitored</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-blue-100">AI Monitoring</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">10x</div>
              <div className="text-blue-100">More Opportunities</div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Contractors Nationwide
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Users className="w-8 h-8 text-blue-600 mr-2" />
                  <div>
                    <div className="font-semibold">Sarah Johnson</div>
                    <div className="text-sm text-gray-600">General Contractor</div>
                  </div>
                </div>
                <p className="text-gray-700 italic">
                  "BidAgents AI found 40% more opportunities than we were finding manually. 
                  The pre-filled forms save us 10+ hours per week."
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Award className="w-8 h-8 text-purple-600 mr-2" />
                  <div>
                    <div className="font-semibold">Mike Chen</div>
                    <div className="text-sm text-gray-600">IT Consultant</div>
                  </div>
                </div>
                <p className="text-gray-700 italic">
                  "The AI agents are like having a dedicated procurement team. 
                  Our win rate increased 25% since using BidAgents."
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600 mr-2" />
                  <div>
                    <div className="font-semibold">David Martinez</div>
                    <div className="text-sm text-gray-600">Landscaping Corp</div>
                  </div>
                </div>
                <p className="text-gray-700 italic">
                  "Finally, a solution that understands the complexity of government bidding. 
                  The document analysis is incredibly accurate."
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Ready to Transform Your Bidding Process?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join hundreds of contractors already winning more bids with AI automation
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/onboarding">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                Start Free Trial
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <Button size="lg" variant="outline">
              Schedule Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Bot className="w-8 h-8 text-blue-400" />
                <span className="text-xl font-bold">BidAgents AI</span>
              </div>
              <p className="text-gray-400">
                Automating procurement processes with intelligent AI agents.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <div className="space-y-2 text-sm text-gray-400">
                <div>Features</div>
                <div>Pricing</div>
                <div>API</div>
                <div>Documentation</div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <div className="space-y-2 text-sm text-gray-400">
                <div>About</div>
                <div>Blog</div>
                <div>Careers</div>
                <div>Contact</div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <div className="space-y-2 text-sm text-gray-400">
                <div>Help Center</div>
                <div>Community</div>
                <div>Status</div>
                <div>Security</div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 BidAgents AI. Built for the Google Agent Development Kit Hackathon.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}