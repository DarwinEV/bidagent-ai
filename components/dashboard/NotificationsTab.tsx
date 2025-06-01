
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bell, CheckCircle, AlertCircle, Clock, FileText, Mail, Eye } from "lucide-react";

export const NotificationsTab = () => {
  const [notifications] = useState([
    {
      id: "notif-001",
      type: "bid_found",
      title: "New Bid Discovered: HVAC Replacement for Building 42",
      message: "Discovery Agent found a new opportunity matching your criteria",
      timestamp: "2 hours ago",
      isRead: false,
      priority: "high",
      actionUrl: "/dashboard?tab=discovery&bid=bid-001"
    },
    {
      id: "notif-002", 
      type: "prefill_complete",
      title: "Pre-filled PDF Ready: Plumbing Maintenance Services",
      message: "Pre-fill Agent has completed form filling. Ready for review and submission.",
      timestamp: "4 hours ago",
      isRead: false,
      priority: "medium",
      actionUrl: "/dashboard?tab=filling&bid=bid-002"
    },
    {
      id: "notif-003",
      type: "deadline_reminder",
      title: "Deadline Approaching: Electrical Infrastructure Upgrade",
      message: "Bid deadline is in 3 days. Pre-filled documents are ready for submission.",
      timestamp: "6 hours ago", 
      isRead: true,
      priority: "urgent",
      actionUrl: "/dashboard?tab=submitting&bid=bid-003"
    },
    {
      id: "notif-004",
      type: "submission_success",
      title: "Bid Submitted Successfully",
      message: "Your bid for 'Municipal Building Maintenance' has been emailed to procurement@city.gov",
      timestamp: "1 day ago",
      isRead: true,
      priority: "low",
      actionUrl: null
    },
    {
      id: "notif-005",
      type: "agent_error",
      title: "Discovery Agent: Login Issue",
      message: "Unable to access SAM.gov portal. Please check credentials in settings.",
      timestamp: "2 days ago",
      isRead: false,
      priority: "urgent",
      actionUrl: "/settings/portals"
    }
  ]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "bid_found":
        return <FileText className="w-5 h-5 text-blue-600" />;
      case "prefill_complete":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "deadline_reminder":
        return <Clock className="w-5 h-5 text-orange-600" />;
      case "submission_success":
        return <Mail className="w-5 h-5 text-green-600" />;
      case "agent_error":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent":
        return "bg-red-100 text-red-800 border-red-200";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <div className="space-y-6">
      {/* Notification Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Bell className="w-5 h-5 mr-2" />
              Notifications
            </div>
            {unreadCount > 0 && (
              <Badge className="bg-red-100 text-red-800">
                {unreadCount} unread
              </Badge>
            )}
          </CardTitle>
          <CardDescription>
            Stay updated on your AI agents' activities and important deadlines
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {unreadCount > 0 ? `You have ${unreadCount} unread notifications` : "All caught up!"}
            </div>
            <Button size="sm" variant="outline">
              Mark All as Read
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {notifications.map((notification) => (
              <Card 
                key={notification.id} 
                className={`border transition-all hover:shadow-md ${
                  !notification.isRead ? 'border-l-4 border-l-blue-500 bg-blue-50/30' : ''
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-1">
                        <h4 className={`font-medium text-sm ${!notification.isRead ? 'text-gray-900' : 'text-gray-700'}`}>
                          {notification.title}
                        </h4>
                        <div className="flex items-center space-x-2 ml-4">
                          <Badge className={getPriorityColor(notification.priority)}>
                            {notification.priority}
                          </Badge>
                          {!notification.isRead && (
                            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-2">
                        {notification.message}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          {notification.timestamp}
                        </span>
                        
                        <div className="flex space-x-2">
                          {notification.actionUrl && (
                            <Button size="sm" variant="outline">
                              <Eye className="w-3 h-3 mr-1" />
                              View
                            </Button>
                          )}
                          {!notification.isRead && (
                            <Button size="sm" variant="ghost">
                              Mark as Read
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
          <CardDescription>
            Configure how and when you want to be notified
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">New Bid Discoveries</div>
                <div className="text-sm text-gray-600">Get notified when agents find new opportunities</div>
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm">Email</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">Deadline Reminders</div>
                <div className="text-sm text-gray-600">Alerts for approaching submission deadlines</div>
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm">Email</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">Agent Errors</div>
                <div className="text-sm text-gray-600">Immediate alerts when agents encounter issues</div>
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm">Email</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">Weekly Summary</div>
                <div className="text-sm text-gray-600">Weekly digest of all agent activities</div>
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm">Email</span>
              </div>
            </div>
          </div>
          
          <Button className="mt-4" size="sm">
            Save Preferences
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};