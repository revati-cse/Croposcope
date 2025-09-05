import { useState, useRef } from "react";
import { Camera, Upload, Loader2, CheckCircle, AlertTriangle, Info } from "lucide-react";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Label } from "@/components/ui/label.tsx";
import { Progress } from "@/components/ui/progress.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import { Badge } from "@/components/ui/badge.tsx";

type AnalysisResult = {
  disease: string;
  confidence: number;
  severity: "low" | "medium" | "high";
  description: string;
  treatments: string[];
};

export default function DiseaseDetection() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Mock diseases data for demonstration
  const mockResults: AnalysisResult[] = [
    {
      disease: "Tomato Late Blight",
      confidence: 94.5,
      severity: "high",
      description: "A serious fungal disease affecting tomato plants, causing dark spots on leaves and fruit.",
      treatments: ["Remove affected leaves", "Apply neem oil spray", "Improve air circulation", "Use copper-based fungicide"]
    },
    {
      disease: "Potato Early Blight",
      confidence: 87.2,
      severity: "medium", 
      description: "Common fungal disease causing brown spots with concentric rings on potato leaves.",
      treatments: ["Crop rotation", "Mulching", "Baking soda spray", "Remove infected debris"]
    },
    {
      disease: "Corn Northern Leaf Blight",
      confidence: 91.8,
      severity: "medium",
      description: "Fungal disease creating cigar-shaped lesions on corn leaves.",
      treatments: ["Plant resistant varieties", "Proper spacing", "Organic fungicide spray", "Balanced nutrition"]
    }
  ];

  const handleImageUpload = (file: File) => {
    setSelectedImage(file);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    setAnalysisResult(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    
    // Simulate AI analysis with random result
    setTimeout(() => {
      const randomResult = mockResults[Math.floor(Math.random() * mockResults.length)];
      setAnalysisResult({
        ...randomResult,
        confidence: Math.random() * 15 + 85 // Random confidence between 85-100%
      });
      setIsAnalyzing(false);
    }, 3000);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low": return "text-green-600 bg-green-100 dark:bg-green-900/20";
      case "medium": return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20";
      case "high": return "text-red-600 bg-red-100 dark:bg-red-900/20";
      default: return "text-gray-600 bg-gray-100 dark:bg-gray-900/20";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "low": return <CheckCircle className="size-4" />;
      case "medium": return <AlertTriangle className="size-4" />;
      case "high": return <AlertTriangle className="size-4" />;
      default: return <Info className="size-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Crop Image</CardTitle>
            <CardDescription>
              Take or upload a clear photo of the affected crop for AI analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
              {imagePreview ? (
                <div className="space-y-4">
                  <img 
                    src={imagePreview} 
                    alt="Selected crop" 
                    className="max-h-64 mx-auto rounded-lg object-cover"
                  />
                  <p className="text-sm text-muted-foreground">{selectedImage?.name}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Camera className="size-12 text-muted-foreground mx-auto" />
                  <div>
                    <p className="text-lg font-medium">No image selected</p>
                    <p className="text-sm text-muted-foreground">
                      Upload JPG, PNG or WEBP (max 10MB)
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="flex-1"
                variant="outline"
              >
                <Upload className="size-4 mr-2" />
                Choose File
              </Button>
              <Button
                onClick={() => {
                  // Camera functionality would go here
                  alert("Camera functionality would be implemented with device camera API");
                }}
                className="flex-1"
                variant="outline"
              >
                <Camera className="size-4 mr-2" />
                Take Photo
              </Button>
            </div>

            <Input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />

            <Button 
              onClick={handleAnalyze}
              disabled={!selectedImage || isAnalyzing}
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Analyze Disease"
              )}
            </Button>

            {isAnalyzing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Processing image...</span>
                  <span>Processing</span>
                </div>
                <Progress value={75} className="w-full" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Analysis Results */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
            <CardDescription>
              AI-powered disease detection using EfficientNetV2 CNN model
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!analysisResult && !isAnalyzing && (
              <div className="text-center py-12 text-muted-foreground">
                <Info className="size-12 mx-auto mb-4" />
                <p>Upload an image and click analyze to get results</p>
              </div>
            )}

            {isAnalyzing && (
              <div className="space-y-4 py-8">
                <div className="flex items-center gap-3">
                  <Loader2 className="size-5 animate-spin" />
                  <span>Running AI analysis...</span>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div>• Image preprocessing complete</div>
                  <div>• Feature extraction in progress</div>
                  <div>• Disease classification running</div>
                </div>
              </div>
            )}

            {analysisResult && (
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">{analysisResult.disease}</h3>
                    <Badge className={getSeverityColor(analysisResult.severity)}>
                      {getSeverityIcon(analysisResult.severity)}
                      <span className="ml-1 capitalize">{analysisResult.severity}</span>
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Confidence</span>
                      <span>{analysisResult.confidence.toFixed(1)}%</span>
                    </div>
                    <Progress value={analysisResult.confidence} className="w-full" />
                  </div>
                </div>

                <Alert>
                  <Info className="size-4" />
                  <AlertDescription>
                    {analysisResult.description}
                  </AlertDescription>
                </Alert>

                <div className="space-y-3">
                  <h4 className="font-medium">Recommended Organic Treatments:</h4>
                  <ul className="space-y-2">
                    {analysisResult.treatments.map((treatment, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span>{treatment}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Button className="w-full" variant="outline">
                  View Detailed Treatment Guide
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Detection History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Detections</CardTitle>
          <CardDescription>Your latest crop disease analyses</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockResults.map((result, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="size-12 bg-muted rounded-lg flex items-center justify-center">
                    <Camera className="size-6 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-medium">{result.disease}</p>
                    <p className="text-sm text-muted-foreground">
                      Confidence: {result.confidence.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <Badge className={getSeverityColor(result.severity)}>
                  {result.severity}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}