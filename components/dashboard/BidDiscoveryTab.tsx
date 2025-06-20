'use client';
// Connect frontend and pass bid search request to backend ✅
// Test whether the connection is working ⌛
// TO DO: Update firebase storage paths in this file below to use Clerk User Details. ⌛

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Search, MapPin, Calendar, Building, ExternalLink, Eye } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { db } from "@/lib/firebase";
import { collection, doc, setDoc } from "firebase/firestore";

type Bid = {
  id: string;
  title: string;
  status: string;
  agency: string;
  location: string;
  deadline: string;
  description: string;
  relevanceScore: number;
  portal: string;
};

export const BidDiscoveryTab = () => {
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [searchParams, setSearchParams] = useState({
    keywords: "",
    naicsCodes: "",
    geography: "",
    portals: [] as string[]
  });
  const [discoveredBids, setDiscoveredBids] = useState<Bid[]>([]);
  const { toast } = useToast();

  const portals = [
    { id: "sam", name: "SAM.gov (Federal)", checked: true },
    { id: "ca-state", name: "California State Portal", checked: true },
    { id: "sf-city", name: "San Francisco City Portal", checked: false },
    { id: "la-city", name: "Los Angeles City Portal", checked: false },
    { id: "private", name: "Private Sector RFPs", checked: false }
  ];

  const handleStartDiscovery = async () => {
    setIsDiscovering(true);
    toast({
      title: "Discovery In Progress...",
      description: "Sending request to the server...",
    });

    try {
      // update the url to use next public api url 
      const response = await fetch('http://127.0.0.1:5000/api/start_discovery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'user-123', // Replace with actual user ID
          ...searchParams
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setDiscoveredBids(data.bids || []);

      toast({
        title: "Discovery Started!",
        description: "AI agents found new opportunities.",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: `Discovery failed: ${error.message}`,
        variant: "destructive",
      });
    } finally {
      setIsDiscovering(false);
    }
  };
  const saveBid = async (bid: Bid) => {
    try {
      toast({
        title: "Saving Bid...",
        description: `Saving "${bid.title}" to your dashboard.`,
      });

      await setDoc(
        doc(collection(db, "users", "user-123", "savedBids"), bid.id),
        bid
      );

      toast({
        title: "Bid Saved!",
        description: `Bid "${bid.title}" has been saved successfully.`
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: `Failed to save bid: ${error.message}`,
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "new":
        return <Badge className="bg-blue-100 text-blue-800">New</Badge>;
      case "analyzed":
        return <Badge className="bg-yellow-100 text-yellow-800">Analyzed</Badge>;
      case "pre-filled":
        return <Badge className="bg-green-100 text-green-800">Pre-filled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return "text-green-600";
    if (score >= 0.8) return "text-yellow-600";
    return "text-gray-600";
  };

  return (
    <div className="space-y-6">
      {/* Discovery Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Search className="w-5 h-5 mr-2" />
            Start New Discovery
          </CardTitle>
          <CardDescription>
            Configure search parameters for your AI discovery agents
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="keywords">Keywords / Services</Label>
              <Input
                id="keywords"
                value={searchParams.keywords}
                onChange={(e) => setSearchParams(prev => ({ ...prev, keywords: e.target.value }))}
                placeholder="HVAC, plumbing, electrical, construction"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="naics">NAICS Codes</Label>
              <Input
                id="naics"
                value={searchParams.naicsCodes}
                onChange={(e) => setSearchParams(prev => ({ ...prev, naicsCodes: e.target.value }))}
                placeholder="236220, 238210, 238220"
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <Label>Geographic Focus</Label>
            <Select onValueChange={(value) => setSearchParams(prev => ({ ...prev, geography: value }))}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select target region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="california">California</SelectItem>
                <SelectItem value="san-francisco-bay">San Francisco Bay Area</SelectItem>
                <SelectItem value="los-angeles">Los Angeles Metro</SelectItem>
                <SelectItem value="national">National</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label className="text-base font-medium">Portal Selection</Label>
            <div className="mt-2 space-y-2">
              {portals.map((portal) => (
                <div key={portal.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={portal.id}
                    defaultChecked={portal.checked}
                    onChange={(e) => {
                      const checked = (e.target as HTMLInputElement).checked;
                      const updatedPortals = checked
                        ? [...searchParams.portals, portal.id]
                        : searchParams.portals.filter(p => p !== portal.id);
                      setSearchParams(prev => ({ ...prev, portals: updatedPortals }));
                    }}
                  />
                  <Label htmlFor={portal.id} className="cursor-pointer">{portal.name}</Label>
                </div>
              ))}
            </div>
          </div>

          <Button
            onClick={handleStartDiscovery}
            disabled={isDiscovering}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            {isDiscovering ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Agents Discovering...
              </div>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                Start Discovery
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Discovered Bids */}
      {discoveredBids.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Discovered Opportunities</CardTitle>
            <CardDescription>
              Recent opportunities found by your discovery agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {discoveredBids.map((bid) => (
                <Card key={bid.id} className="border hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold text-lg">{bid.title}</h3>
                          {getStatusBadge(bid.status)}
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                          <div className="flex items-center">
                            <Building className="w-4 h-4 mr-1" />
                            {bid.agency}
                          </div>
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {bid.location}
                          </div>
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            Due: {new Date(bid.deadline).toLocaleDateString()}
                          </div>
                        </div>
                        <p className="text-gray-700 text-sm">{bid.description}</p>
                      </div>
                      <div className="text-right ml-4">
                        <div className={`text-sm font-medium ${getRelevanceColor(bid.relevanceScore)}`}>
                          {Math.round(bid.relevanceScore * 100)}% match
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          via {bid.portal}
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-between items-center pt-3 border-t">
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="w-4 h-4 mr-1" />
                          View Details
                        </Button>
                        <Button size="sm" variant="outline">
                          <ExternalLink className="w-4 h-4 mr-1" />
                          Original Portal
                        </Button>
                      </div>
                      <Button size="sm" onClick={() => saveBid(bid)} className="bg-green-600 hover:bg-green-700">
                        Save
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
