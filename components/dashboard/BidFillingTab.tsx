
'use client'

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { FileText, Edit, Download, Save, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import axios from 'axios'

export const BidFillingTab = () => {
  const [selectedBid, setSelectedBid] = useState("")
  const [isFilling, setIsFilling] = useState(false)
  const [showPDFInterface, setShowPDFInterface] = useState(false)
  const [formFields, setFormFields] = useState([
    { id: "companyName", label: "Company Name", value: "Acme Contractors, LLC", required: true },
    { id: "address", label: "Business Address", value: "123 Main St, Sacramento, CA 95814", required: true },
    { id: "contactName", label: "Primary Contact", value: "Sarah Johnson", required: true },
    { id: "contactEmail", label: "Contact Email", value: "sarah@acmecontractors.com", required: true },
    { id: "contactPhone", label: "Phone Number", value: "(916) 555-0123", required: true },
    { id: "licenseNumber", label: "License Number", value: "CA-123456", required: true },
    { id: "insurancePolicy", label: "Insurance Policy", value: "INS-789012", required: false },
    { id: "bondingCapacity", label: "Bonding Capacity", value: "$2,000,000", required: false }
  ])
  const { toast } = useToast()

  const availableBids = [
    { id: "bid-001", title: "HVAC Replacement for Building 42", status: "analyzed" },
    { id: "bid-002", title: "Plumbing Maintenance Services", status: "analyzed" },
    { id: "bid-003", title: "Electrical Infrastructure Upgrade", status: "pre-filled" }
  ]

  const handleFieldUpdate = (fieldId: string, newValue: string) => {
    setFormFields(prev => 
      prev.map(field => 
        field.id === fieldId ? { ...field, value: newValue } : field
      )
    )
  }

  const handlePreFill = async () => {
    setIsFilling(true)
    try {
      const companyData = formFields.reduce((acc, field) => {
        acc[field.id] = field.value
        return acc
      }, {} as Record<string, string>)

      await axios.post('/api/agents/prefill', {
        bidId: selectedBid,
        companyData
      })
      
      toast({
        title: "Pre-fill Complete!",
        description: "Bid forms have been automatically filled with your company data.",
      })

      setShowPDFInterface(true)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to pre-fill forms. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsFilling(false)
    }
  }

  const handlePDFSave = (fields: any[]) => {
    toast({
      title: "PDF Saved!",
      description: "Your pre-filled PDF has been saved successfully.",
    })
  }

  if (showPDFInterface && selectedBid) {
    const companyData = formFields.reduce((acc, field) => {
      acc[field.id] = field.value
      return acc
    }, {} as Record<string, string>)

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Interactive PDF Form Filling</h3>
          <Button
            variant="outline"
            onClick={() => setShowPDFInterface(false)}
          >
            Back to Form Editor
          </Button>
        </div>
        
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Bid Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Select Bid to Fill
          </CardTitle>
          <CardDescription>
            Choose a bid that has been analyzed by the AI agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select onValueChange={setSelectedBid}>
            <SelectTrigger>
              <SelectValue placeholder="Select a bid to pre-fill" />
            </SelectTrigger>
            <SelectContent>
              {availableBids.map((bid) => (
                <SelectItem key={bid.id} value={bid.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{bid.title}</span>
                    <Badge variant={bid.status === "pre-filled" ? "default" : "secondary"}>
                      {bid.status}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {selectedBid && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Form Fields Editor */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Edit className="w-5 h-5 mr-2" />
                Company Data Fields
              </CardTitle>
              <CardDescription>
                Review and edit the data that will be used to pre-fill forms
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 max-h-96 overflow-y-auto">
              {formFields.map((field) => (
                <div key={field.id} className="space-y-2">
                  <Label htmlFor={field.id} className="flex items-center">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </Label>
                  <Input
                    id={field.id}
                    value={field.value}
                    onChange={(e) => handleFieldUpdate(field.id, e.target.value)}
                    className="w-full"
                  />
                </div>
              ))}
              
              <div className="pt-4 border-t">
                <Button variant="outline" size="sm" className="w-full">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reset to Saved Data
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* PDF Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Document Preview</CardTitle>
              <CardDescription>
                Preview of the bid document with highlighted fillable fields
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg h-96 bg-gray-50 flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium">PDF Viewer</p>
                  <p className="text-sm">Interactive PDF preview will appear here</p>
                  <div className="mt-4 space-y-2 text-xs">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-3 h-3 bg-blue-200 border border-blue-400 rounded"></div>
                      <span>Fillable Fields</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-3 h-3 bg-green-200 border border-green-400 rounded"></div>
                      <span>Pre-filled Fields</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                <Button 
                  onClick={handlePreFill}
                  disabled={isFilling}
                  className="w-full"
                >
                  {isFilling ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Pre-filling Forms...
                    </div>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Auto Pre-Fill Forms
                    </>
                  )}
                </Button>
                
                <div className="grid grid-cols-2 gap-2">
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Download Original
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Download Pre-filled
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!selectedBid && (
        <Card>
          <CardContent className="p-8 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Bid Selected</h3>
            <p className="text-gray-600">
              Please select a bid from the dropdown above to start pre-filling forms
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}