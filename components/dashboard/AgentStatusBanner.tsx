
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Bot, Play, Pause, CheckCircle, AlertCircle, Clock } from "lucide-react";

interface Agent {
  name: string;
  status: "idle" | "running" | "completed" | "error";
  lastActivity: string;
  message?: string;
}

interface AgentStatusBannerProps {
  agents: Agent[];
}

export const AgentStatusBanner = ({ agents }: AgentStatusBannerProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "running":
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: Agent["status"]) => {
    switch (status) {
      case "running":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "completed":
        return "bg-green-100 text-green-800 border-green-200";
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const runningAgent = agents.find(agent => agent.status === "running");
  const hasErrors = agents.some(agent => agent.status === "error");

  return (
    <div className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Bot className="w-5 h-5 text-blue-600" />
            {runningAgent ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                <span className="text-sm font-medium">
                  {runningAgent.name} is running...
                </span>
                {runningAgent.message && (
                  <span className="text-sm text-gray-600">({runningAgent.message})</span>
                )}
              </div>
            ) : hasErrors ? (
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-800">
                  Some agents need attention
                </span>
              </div>
            ) : (
              <span className="text-sm text-gray-600">All agents ready</span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? "Hide" : "Show"} Agent Details
            </Button>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            {agents.map((agent, index) => (
              <Card key={index} className="border">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(agent.status)}
                      <span className="text-sm font-medium">{agent.name}</span>
                    </div>
                    <Badge className={getStatusColor(agent.status)}>
                      {agent.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-600">
                    Last activity: {agent.lastActivity}
                  </div>
                  {agent.message && (
                    <div className="text-xs text-gray-800 mt-1 font-medium">
                      {agent.message}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};