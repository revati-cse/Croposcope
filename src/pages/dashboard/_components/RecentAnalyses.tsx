import { useState } from "react";
import { Calendar, Download, Eye, Trash2, Filter, MoreHorizontal, TrendingUp, Camera } from "lucide-react";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Input } from "@/components/ui/input.tsx";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu.tsx";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";

type Analysis = {
  id: string;
  date: string;
  crop: string;
  disease: string;
  confidence: number;
  severity: "low" | "medium" | "high";
  fieldLocation: string;
  imageUrl: string;
  treatmentApplied: boolean;
  notes?: string;
};

export default function RecentAnalyses() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("all");

  const analyses: Analysis[] = [
    {
      id: "1",
      date: "2024-01-15T10:30:00",
      crop: "Tomato",
      disease: "Late Blight",
      confidence: 94.5,
      severity: "high",
      fieldLocation: "North Field Section A",
      imageUrl: "/api/placeholder/150/150",
      treatmentApplied: true,
      notes: "Applied neem oil spray treatment as recommended"
    },
    {
      id: "2", 
      date: "2024-01-14T15:45:00",
      crop: "Potato",
      disease: "Early Blight",
      confidence: 87.2,
      severity: "medium",
      fieldLocation: "South Field Section B",
      imageUrl: "/api/placeholder/150/150",
      treatmentApplied: true,
      notes: "Started crop rotation schedule"
    },
    {
      id: "3",
      date: "2024-01-13T09:15:00", 
      crop: "Corn",
      disease: "Northern Leaf Blight",
      confidence: 91.8,
      severity: "medium",
      fieldLocation: "East Field Section C",
      imageUrl: "/api/placeholder/150/150",
      treatmentApplied: false
    },
    {
      id: "4",
      date: "2024-01-12T14:20:00",
      crop: "Tomato",
      disease: "Bacterial Spot",
      confidence: 89.3,
      severity: "low",
      fieldLocation: "North Field Section A",
      imageUrl: "/api/placeholder/150/150", 
      treatmentApplied: true,
      notes: "Used copper soap spray - showing improvement"
    },
    {
      id: "5",
      date: "2024-01-11T11:30:00",
      crop: "Cucumber",
      disease: "Powdery Mildew",
      confidence: 96.1,
      severity: "high",
      fieldLocation: "Greenhouse Unit 2",
      imageUrl: "/api/placeholder/150/150",
      treatmentApplied: true,
      notes: "Improved ventilation and applied baking soda spray"
    },
    {
      id: "6",
      date: "2024-01-10T16:45:00",
      crop: "Potato",
      disease: "Healthy",
      confidence: 98.7,
      severity: "low",
      fieldLocation: "West Field Section D", 
      imageUrl: "/api/placeholder/150/150",
      treatmentApplied: false,
      notes: "Preventive monitoring - no issues detected"
    }
  ];

  const filteredAnalyses = analyses.filter(analysis => {
    const matchesSearch = 
      analysis.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.disease.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.fieldLocation.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesSeverity = filterSeverity === "all" || analysis.severity === filterSeverity;
    
    return matchesSearch && matchesSeverity;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low": return "bg-green-100 text-green-800 dark:bg-green-900/20";
      case "medium": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20"; 
      case "high": return "bg-red-100 text-red-800 dark:bg-red-900/20";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900/20";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-green-600";
    if (confidence >= 75) return "text-yellow-600";
    return "text-red-600";
  };

  const exportToCSV = () => {
    const headers = ["Date", "Crop", "Disease", "Confidence", "Severity", "Location", "Treatment Applied", "Notes"];
    const csvContent = [
      headers.join(","),
      ...filteredAnalyses.map(analysis => [
        analysis.date,
        analysis.crop,
        analysis.disease,
        analysis.confidence,
        analysis.severity,
        analysis.fieldLocation,
        analysis.treatmentApplied ? "Yes" : "No",
        analysis.notes || ""
      ].map(field => `"${field}"`).join(","))
    ].join("\n");
    
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "crop_analyses.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Calculate statistics
  const totalAnalyses = analyses.length;
  const diseaseDetected = analyses.filter(a => a.disease !== "Healthy").length;
  const averageConfidence = analyses.reduce((sum, a) => sum + a.confidence, 0) / analyses.length;
  const treatmentCompliance = analyses.filter(a => a.treatmentApplied).length / totalAnalyses * 100;

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Analyses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAnalyses}</div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Diseases Detected</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{diseaseDetected}</div>
            <p className="text-xs text-muted-foreground">{((diseaseDetected/totalAnalyses)*100).toFixed(1)}% detection rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{averageConfidence.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Model accuracy</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Treatment Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{treatmentCompliance.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Applied treatments</p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="size-5" />
            Analysis History
          </CardTitle>
          <CardDescription>
            View and manage your crop disease detection history
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <Input
                placeholder="Search by crop, disease, or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="flex gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    <Filter className="size-4 mr-2" />
                    Severity: {filterSeverity === "all" ? "All" : filterSeverity}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterSeverity("all")}>
                    All Severities
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterSeverity("high")}>
                    High Severity
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterSeverity("medium")}>
                    Medium Severity
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterSeverity("low")}>
                    Low Severity
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button onClick={exportToCSV} variant="outline">
                <Download className="size-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Desktop Table View */}
          <div className="hidden md:block border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Image</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Crop</TableHead>
                  <TableHead>Disease</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Treatment</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAnalyses.map((analysis) => (
                  <TableRow key={analysis.id}>
                    <TableCell>
                      <div className="size-12 bg-muted rounded-lg flex items-center justify-center">
                        <Camera className="size-6 text-muted-foreground" />
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">
                      {formatDate(analysis.date)}
                    </TableCell>
                    <TableCell>{analysis.crop}</TableCell>
                    <TableCell>
                      <div className="font-medium">{analysis.disease}</div>
                      {analysis.notes && (
                        <div className="text-xs text-muted-foreground max-w-32 truncate">
                          {analysis.notes}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className={`font-medium ${getConfidenceColor(analysis.confidence)}`}>
                        {analysis.confidence.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge className={getSeverityColor(analysis.severity)}>
                        {analysis.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-32 truncate">
                      {analysis.fieldLocation}
                    </TableCell>
                    <TableCell>
                      <Badge variant={analysis.treatmentApplied ? "default" : "secondary"}>
                        {analysis.treatmentApplied ? "Applied" : "Pending"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="size-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem>
                            <Eye className="size-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="size-4 mr-2" />
                            Download Image
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="size-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Mobile Card View */}
          <div className="md:hidden space-y-4">
            {filteredAnalyses.map((analysis) => (
              <Card key={analysis.id}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="size-12 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                      <Camera className="size-6 text-muted-foreground" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-medium">{analysis.crop}</h3>
                          <p className="text-sm text-muted-foreground">
                            {formatDate(analysis.date)}
                          </p>
                        </div>
                        <Badge className={getSeverityColor(analysis.severity)}>
                          {analysis.severity}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{analysis.disease}</span>
                          <span className={`text-sm font-medium ${getConfidenceColor(analysis.confidence)}`}>
                            {analysis.confidence.toFixed(1)}%
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">{analysis.fieldLocation}</span>
                          <Badge variant={analysis.treatmentApplied ? "default" : "secondary"}>
                            {analysis.treatmentApplied ? "Treated" : "Pending"}
                          </Badge>
                        </div>
                        
                        {analysis.notes && (
                          <p className="text-xs text-muted-foreground">{analysis.notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredAnalyses.length === 0 && (
            <div className="text-center py-12">
              <Calendar className="size-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No analyses found</h3>
              <p className="text-muted-foreground">
                {searchQuery || filterSeverity !== "all" 
                  ? "Try adjusting your search criteria"
                  : "Start by uploading crop images for analysis"
                }
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Insights Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="size-5" />
            Insights & Trends
          </CardTitle>
          <CardDescription>AI-powered analysis of your crop health patterns</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Alert>
              <TrendingUp className="size-4" />
              <AlertDescription>
                <strong>Pattern Detected:</strong> Late blight occurrences increased by 40% in North Field Section A. 
                Consider improving drainage and air circulation in this area.
              </AlertDescription>
            </Alert>

            <Alert>
              <AlertDescription>
                <strong>Recommendation:</strong> Your treatment compliance rate is {treatmentCompliance.toFixed(1)}%. 
                Applying treatments to all detected diseases could improve overall crop health by an estimated 25%.
              </AlertDescription>
            </Alert>

            <Alert>
              <AlertDescription>
                <strong>Success Story:</strong> Greenhouse Unit 2 showed 60% reduction in powdery mildew after 
                implementing improved ventilation protocols.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}