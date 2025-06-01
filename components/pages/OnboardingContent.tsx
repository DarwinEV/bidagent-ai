
'use client'

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Upload, FileText, Building, User } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useUser } from "@clerk/nextjs"
import { db } from "@/lib/firebase"
import { collection, addDoc } from "firebase/firestore"

export const OnboardingContent = () => {
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()
  const router = useRouter()
  const { user } = useUser()
  
  const [formData, setFormData] = useState({
    role: "",
    companyName: "",
    businessType: "",
    naicsCodes: "",
    geography: "",
    companyFile: null as File | null,
    pastBids: null as FileList | null,
    keywords: "",
    portalPreferences: [] as string[]
  })

  const businessTypes = [
    "General Contractor",
    "IT Consultant", 
    "Landscaping Services",
    "Professional Services",
    "Construction",
    "Engineering",
    "Maintenance Services",
    "Other"
  ]

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'company' | 'bids') => {
    const files = e.target.files
    if (files) {
      if (type === 'company') {
        setFormData(prev => ({ ...prev, companyFile: files[0] }))
      } else {
        setFormData(prev => ({ ...prev, pastBids: files }))
      }
    }
  }

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      handleSubmit()
    }
  }

  const handleSubmit = async () => {
    setIsLoading(true)
    try {
      // Save onboarding data to Firestore
      await addDoc(collection(db, 'userProfiles'), {
        userId: user?.id,
        ...formData,
        createdAt: new Date(),
        hasCompletedOnboarding: true
      })
      
      toast({
        title: "Onboarding Complete!",
        description: "Your BidAgents AI profile has been created successfully.",
      })
      
      router.push('/dashboard')
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to complete onboarding. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-4">
            <span className="text-2xl font-bold text-blue-600">← BidAgents AI</span>
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Setup Your AI Agents</h1>
          <p className="text-xl text-gray-600">Let's configure your intelligent bidding assistant</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            {[1, 2, 3].map((i) => (
              <div key={i} className={`flex items-center ${i < 3 ? 'flex-1' : ''}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold
                  ${step >= i ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
                  {i}
                </div>
                {i < 3 && (
                  <div className={`flex-1 h-1 mx-4 ${step > i ? 'bg-blue-600' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>Business Profile</span>
            <span>Company Data</span>
            <span>Preferences</span>
          </div>
        </div>

        {/* Step 1: Business Profile */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Building className="w-6 h-6 mr-2 text-blue-600" />
                Business Profile
              </CardTitle>
              <CardDescription>
                Tell us about your business so our AI agents can find relevant opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-semibold">What type of business are you?</Label>
                <RadioGroup 
                  value={formData.businessType} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, businessType: value }))}
                  className="grid grid-cols-2 gap-4 mt-2"
                >
                  {businessTypes.map((type) => (
                    <div key={type} className="flex items-center space-x-2">
                      <RadioGroupItem value={type} id={type} />
                      <Label htmlFor={type} className="cursor-pointer">{type}</Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="companyName">Company Name</Label>
                  <Input
                    id="companyName"
                    value={formData.companyName}
                    onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                    placeholder="Acme Contractors, LLC"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="naicsCodes">Primary NAICS Codes</Label>
                  <Input
                    id="naicsCodes"
                    value={formData.naicsCodes}
                    onChange={(e) => setFormData(prev => ({ ...prev, naicsCodes: e.target.value }))}
                    placeholder="236220, 238210"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="geography">Geographic Focus</Label>
                <Select onValueChange={(value) => setFormData(prev => ({ ...prev, geography: value }))}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select your primary region" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="california">California</SelectItem>
                    <SelectItem value="texas">Texas</SelectItem>
                    <SelectItem value="florida">Florida</SelectItem>
                    <SelectItem value="new-york">New York</SelectItem>
                    <SelectItem value="national">National</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Company Data Upload */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="w-6 h-6 mr-2 text-purple-600" />
                Company Data Upload
              </CardTitle>
              <CardDescription>
                Upload your company information to enable automatic form pre-filling
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-semibold">Company Data File (JSON/CSV)</Label>
                <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <div className="text-sm text-gray-600 mb-2">
                    Upload a JSON or CSV file with your company details
                  </div>
                  <input
                    type="file"
                    accept=".json,.csv"
                    onChange={(e) => handleFileUpload(e, 'company')}
                    className="hidden"
                    id="company-upload"
                  />
                  <Label htmlFor="company-upload">
                    <Button variant="outline" className="cursor-pointer">
                      Choose File
                    </Button>
                  </Label>
                  {formData.companyFile && (
                    <div className="mt-2 text-sm text-green-600">
                      ✓ {formData.companyFile.name}
                    </div>
                  )}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Include: company name, address, contact info, license numbers, insurance details
                </div>
              </div>

              <div>
                <Label className="text-base font-semibold">Past Bid Documents (Optional)</Label>
                <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition-colors">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <div className="text-sm text-gray-600 mb-2">
                    Upload previous bid documents to train our AI
                  </div>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc"
                    multiple
                    onChange={(e) => handleFileUpload(e, 'bids')}
                    className="hidden"
                    id="bids-upload"
                  />
                  <Label htmlFor="bids-upload">
                    <Button variant="outline" className="cursor-pointer">
                      Choose Files
                    </Button>
                  </Label>
                  {formData.pastBids && (
                    <div className="mt-2 text-sm text-green-600">
                      ✓ {formData.pastBids.length} file(s) selected
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Preferences */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="w-6 h-6 mr-2 text-green-600" />
                Agent Preferences
              </CardTitle>
              <CardDescription>
                Configure how your AI agents should search and filter opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="keywords">Search Keywords</Label>
                <Textarea
                  id="keywords"
                  value={formData.keywords}
                  onChange={(e) => setFormData(prev => ({ ...prev, keywords: e.target.value }))}
                  placeholder="HVAC, plumbing, electrical, maintenance, construction, renovation"
                  className="mt-1"
                  rows={3}
                />
                <div className="mt-1 text-xs text-gray-500">
                  Keywords help our discovery agent find relevant opportunities
                </div>
              </div>

              <div>
                <Label className="text-base font-semibold">Portal Preferences</Label>
                <div className="mt-2 space-y-2">
                  {[
                    { id: 'sam', name: 'SAM.gov (Federal)', checked: true },
                    { id: 'ca-state', name: 'California State Portal', checked: true },
                    { id: 'tx-state', name: 'Texas State Portal', checked: false },
                    { id: 'local', name: 'Local Government Portals', checked: true },
                    { id: 'private', name: 'Private Sector RFPs', checked: false }
                  ].map((portal) => (
                    <div key={portal.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={portal.id}
                        defaultChecked={portal.checked}
                        className="rounded"
                      />
                      <Label htmlFor={portal.id} className="cursor-pointer">{portal.name}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">🤖 Your AI Agent Team</h4>
                <div className="space-y-1 text-sm text-blue-800">
                  <div>• <strong>Discovery Agent:</strong> Monitors portals 24/7</div>
                  <div>• <strong>Analysis Agent:</strong> Extracts requirements from documents</div>
                  <div>• <strong>Pre-fill Agent:</strong> Automatically fills forms with your data</div>
                  <div>• <strong>Notification Agent:</strong> Alerts you of new opportunities</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button 
            variant="outline" 
            onClick={() => setStep(step - 1)}
            disabled={step === 1}
          >
            Previous
          </Button>
          <Button 
            onClick={handleNext}
            disabled={isLoading || (step === 1 && !formData.businessType)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Setting up agents...
              </div>
            ) : step === 3 ? 'Complete Setup' : 'Next'}
          </Button>
        </div>
      </div>
    </div>
  )
}