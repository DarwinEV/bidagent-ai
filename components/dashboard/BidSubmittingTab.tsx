'use client'

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Mail, ExternalLink, Calendar, Clock, CheckCircle, Send } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import axios from 'axios'

interface Bid {
  id: string;
  title: string;
  agency: string;
  deadline: string;
  prefilledPath: string;
  submissionMethod: 'email' | 'portal';
  submissionEmail?: string;
  submissionPortal?: string;
  instructions: string;
  status: 'ready' | 'submitted';
}

export const BidSubmittingTab = () => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [preFilledBids, setPreFilledBids] = useState<Bid[]>([
    {
      id: "bid-001",
      title: "HVAC Replacement for Building 42",
      agency: "State University of California",
      deadline: "2025-07-15",
      prefilledPath: "/prefilled_bids/user123/bid-001.pdf",
      submissionMethod: "email",
      submissionEmail: "procurement@university.edu",
      submissionPortal: "https://portal.university.edu/bids",
      instructions: "Email pre-filled forms to procurement@university.edu with subject line 'Bid Response - Building 42 HVAC'",
      status: "ready"
    },
    {
      id: "bid-002",
      title: "Plumbing Maintenance Services", 
      agency: "City of San Francisco",
      deadline: "2025-06-30",
      prefilledPath: "/prefilled_bids/user123/bid-002.pdf",
      submissionMethod: "portal",
      submissionPortal: "https://sf.gov/bids/submit",
      instructions: "Upload documents via the SF Procurement Portal before 5:00 PM PST",
      status: "ready"
    },
    {
      id: "bid-003",
      title: "Electrical Infrastructure Upgrade",
      agency: "Regional Transit Authority", 
      deadline: "2025-08-01",
      prefilledPath: "/prefilled_bids/user123/bid-003.pdf",
      submissionMethod: "email",
      submissionEmail: "bids@transit.gov",
      instructions: "Email completed bid package including technical specifications",
      status: "submitted"
    }
  ])
  const { toast } = useToast()

  const handleEmailSubmission = async (bid: Bid) => {
    setIsSubmitting(true)
    try {
      await axios.post('/api/agents/submit', {
        bidId: bid.id,
        submissionMethod: 'email',
        submissionEmail: bid.submissionEmail
      })

      // Update local state
      setPreFilledBids(prev => 
        prev.map(b => 
          b.id === bid.id ? { ...b, status: 'submitted' } : b
        )
      )
      
      toast({
        title: "Bid Submitted Successfully!",
        description: `Your bid for "${bid.title}" has been emailed to ${bid.submissionEmail}`,
      })
    } catch (error) {
      toast({
        title: "Submission Failed",
        description: "Failed to submit bid. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getDaysUntilDeadline = (deadline: string) => {
    const deadlineDate = new Date(deadline)
    const today = new Date()
    const diffTime = deadlineDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const getDeadlineColor = (days: number) => {
    if (days <= 3) return "text-red-600"
    if (days <= 7) return "text-orange-600"
    return "text-green-600"
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Send className="w-5 h-5 mr-2" />
            Ready for Submission
          </CardTitle>
          <CardDescription>
            Pre-filled bids ready to be submitted to procurement portals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {preFilledBids.map((bid) => {
              const daysLeft = getDaysUntilDeadline(bid.deadline)
              
              return (
                <Card key={bid.id} className="border">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-semibold text-lg">{bid.title}</h3>
                          <Badge variant={bid.status === "submitted" ? "default" : "secondary"}>
                            {bid.status === "submitted" ? "Submitted" : "Ready"}
                          </Badge>
                        </div>
                        <p className="text-gray-600 mb-2">{bid.agency}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            Due: {new Date(bid.deadline).toLocaleDateString()}
                          </div>
                          <div className={`flex items-center ${getDeadlineColor(daysLeft)}`}>
                            <Clock className="w-4 h-4 mr-1" />
                            {daysLeft > 0 ? `${daysLeft} days left` : "Overdue"}
                          </div>
                        </div>
                      </div>
                      {bid.status === "submitted" && (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      )}
                    </div>

                    <div className="bg-gray-50 p-3 rounded-lg mb-4">
                      <h4 className="font-medium text-sm mb-2">Submission Instructions:</h4>
                      <p className="text-sm text-gray-700">{bid.instructions}</p>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <ExternalLink className="w-4 h-4 mr-1" />
                          View Pre-filled PDF
                        </Button>
                        {bid.submissionPortal && (
                          <Button size="sm" variant="outline">
                            <ExternalLink className="w-4 h-4 mr-1" />
                            Open Portal
                          </Button>
                        )}
                      </div>

                      {bid.status === "ready" && (
                        <div className="space-x-2">
                          {bid.submissionMethod === "email" && bid.submissionEmail && (
                            <Button 
                              size="sm"
                              onClick={() => handleEmailSubmission(bid)}
                              disabled={isSubmitting}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              {isSubmitting ? (
                                <div className="flex items-center">
                                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                                  Sending...
                                </div>
                              ) : (
                                <>
                                  <Mail className="w-4 h-4 mr-1" />
                                  Email Submission
                                </>
                              )}
                            </Button>
                          )}
                          <Button size="sm" variant="outline">
                            Mark as Submitted
                          </Button>
                        </div>
                      )}
                    </div>

                    {bid.status === "submitted" && (
                      <div className="mt-3 p-2 bg-green-50 rounded text-sm text-green-800">
                        ✓ Submitted successfully on {new Date().toLocaleDateString()}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Submission History */}
      <Card>
        <CardHeader>
          <CardTitle>Submission History</CardTitle>
          <CardDescription>
            Track your bid submission activity and outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <div className="font-medium">Electrical Infrastructure Upgrade</div>
                  <div className="text-sm text-gray-600">Submitted 2 hours ago</div>
                </div>
              </div>
              <Badge className="bg-green-100 text-green-800">Submitted</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="font-medium">Municipal Building Maintenance</div>
                  <div className="text-sm text-gray-600">Submitted yesterday</div>
                </div>
              </div>
              <Badge className="bg-blue-100 text-blue-800">Under Review</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-yellow-600" />
                <div>
                  <div className="font-medium">School District HVAC Project</div>
                  <div className="text-sm text-gray-600">Submitted 3 days ago</div>
                </div>
              </div>
              <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}