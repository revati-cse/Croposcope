import { useState } from "react";
import { 
  Camera, 
  Upload, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Leaf, 
  History, 
  Settings,
  FileText,
  BarChart3,
  Users,
  Globe
} from "lucide-react";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Label } from "@/components/ui/label.tsx";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Progress } from "@/components/ui/progress.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import { useAuth, useUser } from "@/hooks/use-auth.ts";
import { SignInButton } from "@/components/ui/signin.tsx";

import DiseaseDetection from "../pages/dashboard/_components/DiseaseDetection.tsx";
import VoiceInterface from "../pages/dashboard/_components/VoiceInterface.tsx";
import TreatmentRecommendations from "../pages/dashboard/_components/TreatmentRecommendations.tsx";
import RecentAnalyses from "../pages/dashboard/_components/RecentAnalyses.tsx";

export default function Dashboard() {
  const { isAuthenticated } = useAuth();
  const { name, email, isLoading } = useUser({ shouldRedirect: true });
  const [selectedTab, setSelectedTab] = useState("detect");

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <Leaf className="size-12 text-primary mx-auto mb-4" />
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please sign in to access the Croposcope dashboard
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <SignInButton />
          </CardContent>
        </Card>
      </div>
    );
  }

  const stats = [
    {
      title: "Total Analyses",
      value: "127",
      change: "+12%",
      icon: <BarChart3 className="size-4" />
    },
    {
      title: "Diseases Detected",
      value: "15",
      change: "+3",
      icon: <FileText className="size-4" />
    },
    {
      title: "Accuracy Rate",
      value: "96.2%",
      change: "+1.2%",
      icon: <Users className="size-4" />
    },
    {
      title: "Fields Monitored",
      value: "8",
      change: "+2",
      icon: <Globe className="size-4" />
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Leaf className="size-8 text-primary" />
                <h1 className="text-2xl font-bold">Croposcope</h1>
              </div>
              <Badge variant="secondary">Dashboard</Badge>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-medium">{name}</p>
                <p className="text-sm text-muted-foreground">{email}</p>
              </div>
              <SignInButton />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Welcome back, {name?.split(' ')[0] || 'User'}!</h2>
          <p className="text-muted-foreground">
            Ready to analyze your crops and detect diseases using our AI-powered system.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                {stat.icon}
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">{stat.change}</span> from last month
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="detect" className="flex items-center gap-2">
              <Camera className="size-4" />
              Detect
            </TabsTrigger>
            <TabsTrigger value="voice" className="flex items-center gap-2">
              <Mic className="size-4" />
              Voice
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="size-4" />
              History
            </TabsTrigger>
            <TabsTrigger value="treatments" className="flex items-center gap-2">
              <Leaf className="size-4" />
              Treatments
            </TabsTrigger>
          </TabsList>

          <TabsContent value="detect">
            <DiseaseDetection />
          </TabsContent>

          <TabsContent value="voice">
            <VoiceInterface />
          </TabsContent>

          <TabsContent value="history">
            <RecentAnalyses />
          </TabsContent>

          <TabsContent value="treatments">
            <TreatmentRecommendations />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}