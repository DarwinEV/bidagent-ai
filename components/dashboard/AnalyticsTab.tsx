
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Clock, Target, Calendar } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

export const AnalyticsTab = () => {
  const [timeRange, setTimeRange] = useState("30d");

  // Mock analytics data
  const bidVolumeData = [
    { month: "Jan", discovered: 12, submitted: 8, won: 3 },
    { month: "Feb", discovered: 15, submitted: 10, won: 4 },
    { month: "Mar", discovered: 18, submitted: 14, won: 5 },
    { month: "Apr", discovered: 22, submitted: 16, won: 6 },
    { month: "May", discovered: 28, submitted: 20, won: 8 },
    { month: "Jun", discovered: 24, submitted: 18, won: 7 }
  ];

  const categoryData = [
    { name: "HVAC", value: 35, color: "#3B82F6" },
    { name: "Plumbing", value: 25, color: "#10B981" },
    { name: "Electrical", value: 20, color: "#F59E0B" },
    { name: "General", value: 15, color: "#EF4444" },
    { name: "Other", value: 5, color: "#8B5CF6" }
  ];

  const timeSavedData = [
    { week: "Week 1", hours: 8 },
    { week: "Week 2", hours: 12 },
    { week: "Week 3", hours: 15 },
    { week: "Week 4", hours: 18 }
  ];

  const stats = {
    totalBidsFound: 139,
    totalSubmitted: 86,
    winRate: 0.31,
    avgTimeSaved: 13.2,
    totalRevenue: 2400000,
    avgBidValue: 85000
  };

  return (
    <div className="space-y-6">
      {/* Analytics Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Analytics Dashboard
              </CardTitle>
              <CardDescription>
                Insights into your bidding performance and AI agent efficiency
              </CardDescription>
            </div>
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
                <SelectItem value="1y">Last year</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Bids Found</p>
                <p className="text-2xl font-bold">{stats.totalBidsFound}</p>
              </div>
              <Target className="w-8 h-8 text-blue-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +23% vs last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Submitted</p>
                <p className="text-2xl font-bold">{stats.totalSubmitted}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +18% vs last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Win Rate</p>
                <p className="text-2xl font-bold">{Math.round(stats.winRate * 100)}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-yellow-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +5% vs last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Time Saved/Week</p>
                <p className="text-2xl font-bold">{stats.avgTimeSaved}h</p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +2.3h vs last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold">${(stats.totalRevenue / 1000000).toFixed(1)}M</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +15% vs last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Bid Value</p>
                <p className="text-2xl font-bold">${(stats.avgBidValue / 1000).toFixed(0)}K</p>
              </div>
              <Target className="w-8 h-8 text-orange-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-red-600">
              <TrendingDown className="w-4 h-4 mr-1" />
              -3% vs last period
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Bid Volume Trends</CardTitle>
            <CardDescription>
              Monthly breakdown of discovered, submitted, and won bids
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={bidVolumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="discovered" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="submitted" stroke="#10B981" strokeWidth={2} />
                <Line type="monotone" dataKey="won" stroke="#F59E0B" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            <div className="flex justify-center space-x-6 mt-4 text-sm">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                Discovered
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                Submitted
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded mr-2"></div>
                Won
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bid Categories</CardTitle>
            <CardDescription>
              Distribution of opportunities by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Time Saved Per Week</CardTitle>
            <CardDescription>
              Hours saved through AI automation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={timeSavedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="hours" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Agent Performance</CardTitle>
            <CardDescription>
              Success rates and activity metrics for your agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <div>
                  <div className="font-medium">Discovery Agent</div>
                  <div className="text-sm text-gray-600">139 opportunities found</div>
                </div>
                <Badge className="bg-blue-100 text-blue-800">98% uptime</Badge>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <div>
                  <div className="font-medium">Analysis Agent</div>
                  <div className="text-sm text-gray-600">124 documents processed</div>
                </div>
                <Badge className="bg-green-100 text-green-800">95% accuracy</Badge>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <div>
                  <div className="font-medium">Pre-fill Agent</div>
                  <div className="text-sm text-gray-600">86 forms completed</div>
                </div>
                <Badge className="bg-purple-100 text-purple-800">99% success</Badge>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                <div>
                  <div className="font-medium">Notification Agent</div>
                  <div className="text-sm text-gray-600">204 alerts sent</div>
                </div>
                <Badge className="bg-yellow-100 text-yellow-800">100% delivery</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle>AI-Generated Insights</CardTitle>
          <CardDescription>
            Key observations and recommendations from your bidding data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2">🎯 Top Performing Category</h4>
              <p className="text-sm text-green-800">
                Your HVAC bids have a 42% win rate, significantly higher than your 31% average. 
                Consider focusing more resources on HVAC opportunities.
              </p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">⏰ Optimal Submission Timing</h4>
              <p className="text-sm text-blue-800">
                Bids submitted 5-7 days before deadline have a 15% higher win rate. 
                Your agents are helping you hit this sweet spot more consistently.
              </p>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <h4 className="font-semibold text-purple-900 mb-2">🚀 Efficiency Gains</h4>
              <p className="text-sm text-purple-800">
                AI automation has reduced your bid preparation time by 85%, 
                allowing you to pursue 60% more opportunities than before.
              </p>
            </div>
            
            <div className="p-4 bg-orange-50 rounded-lg">
              <h4 className="font-semibold text-orange-900 mb-2">📊 Geographic Opportunity</h4>
              <p className="text-sm text-orange-800">
                San Francisco Bay Area shows 40% more opportunities than your current focus areas. 
                Consider expanding your geographic scope.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};