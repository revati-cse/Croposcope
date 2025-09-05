import { useState } from "react";
import { Leaf, Search, Filter, ExternalLink, CheckCircle, Clock, Sprout, Droplets, Sun, Wind } from "lucide-react";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";

type Treatment = {
  id: string;
  name: string;
  disease: string;
  crop: string;
  type: "organic" | "biological" | "cultural" | "preventive";
  effectiveness: number;
  duration: string;
  difficulty: "easy" | "medium" | "hard";
  ingredients: string[];
  instructions: string[];
  benefits: string[];
  precautions: string[];
  cost: "low" | "medium" | "high";
  season: string[];
};

export default function TreatmentRecommendations() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedCrop, setSelectedCrop] = useState("all");

  const treatments: Treatment[] = [
    {
      id: "1",
      name: "Neem Oil Spray",
      disease: "Aphids, Powdery Mildew, Leaf Spot",
      crop: "Tomato, Potato, Corn",
      type: "organic",
      effectiveness: 85,
      duration: "7-14 days",
      difficulty: "easy",
      ingredients: ["Neem oil (2-3 tbsp)", "Liquid soap (1 tsp)", "Water (1 liter)"],
      instructions: [
        "Mix neem oil and liquid soap in warm water",
        "Stir thoroughly until well combined", 
        "Spray on affected areas in early morning or evening",
        "Reapply every 7-10 days or after rain"
      ],
      benefits: [
        "100% organic and safe for humans",
        "Effective against multiple pests and diseases",
        "Doesn't harm beneficial insects",
        "Biodegradable and eco-friendly"
      ],
      precautions: [
        "Don't spray in direct sunlight",
        "Test on small area first",
        "Avoid during flowering for pollinator safety"
      ],
      cost: "low",
      season: ["Spring", "Summer", "Fall"]
    },
    {
      id: "2", 
      name: "Baking Soda Fungicide",
      disease: "Powdery Mildew, Black Spot, Rust",
      crop: "Tomato, Cucumber, Rose",
      type: "organic",
      effectiveness: 78,
      duration: "5-7 days",
      difficulty: "easy",
      ingredients: ["Baking soda (1 tbsp)", "Liquid soap (1/2 tsp)", "Water (1 liter)"],
      instructions: [
        "Dissolve baking soda in water",
        "Add liquid soap and mix gently",
        "Spray on both sides of leaves",
        "Apply weekly during humid conditions"
      ],
      benefits: [
        "Readily available household item",
        "Safe for edible crops",
        "Changes leaf surface pH to prevent fungal growth",
        "Very cost-effective"
      ],
      precautions: [
        "Don't exceed recommended concentration",
        "May cause leaf burn if overused",
        "Best used as prevention"
      ],
      cost: "low",
      season: ["Summer", "Fall"]
    },
    {
      id: "3",
      name: "Companion Planting",
      disease: "Various Pests and Diseases", 
      crop: "All crops",
      type: "cultural",
      effectiveness: 70,
      duration: "Full growing season",
      difficulty: "medium",
      ingredients: ["Marigold seeds", "Basil plants", "Nasturtium seeds", "Garlic bulbs"],
      instructions: [
        "Plant marigolds around tomato beds",
        "Interplant basil with tomatoes and peppers",
        "Use nasturtiums as trap crops for aphids",
        "Plant garlic around roses and fruit trees"
      ],
      benefits: [
        "Natural pest deterrent",
        "Attracts beneficial insects",
        "Improves soil health",
        "Provides additional harvest (herbs, flowers)"
      ],
      precautions: [
        "Research plant compatibility",
        "Consider space requirements",
        "Plan for different growing seasons"
      ],
      cost: "medium",
      season: ["Spring", "Summer"]
    },
    {
      id: "4",
      name: "Copper Soap Spray",
      disease: "Late Blight, Bacterial Spot, Fire Blight",
      crop: "Tomato, Potato, Apple",
      type: "organic", 
      effectiveness: 88,
      duration: "10-14 days",
      difficulty: "medium",
      ingredients: ["Copper sulfate (1 tsp)", "Liquid soap (1 tsp)", "Water (1 liter)"],
      instructions: [
        "Dissolve copper sulfate in small amount of water",
        "Add remaining water and soap",
        "Spray thoroughly on all plant surfaces",
        "Apply before rain events for prevention"
      ],
      benefits: [
        "Highly effective against bacterial diseases",
        "Long-lasting protection",
        "OMRI approved for organic farming",
        "Works in cool, wet conditions"
      ],
      precautions: [
        "Can accumulate in soil over time",
        "May cause phytotoxicity if overused",
        "Wear protective equipment when mixing"
      ],
      cost: "medium", 
      season: ["Spring", "Fall"]
    },
    {
      id: "5",
      name: "Beneficial Bacteria Application",
      disease: "Root Rot, Damping Off, Soil Pathogens",
      crop: "All seedlings and transplants",
      type: "biological",
      effectiveness: 82,
      duration: "4-6 weeks",
      difficulty: "medium",
      ingredients: ["Bacillus subtilis culture", "Mycorrhizal fungi", "Organic matter", "Water"],
      instructions: [
        "Mix beneficial bacteria according to package directions",
        "Apply to soil around plant base",
        "Water gently to activate microorganisms", 
        "Reapply monthly during growing season"
      ],
      benefits: [
        "Establishes healthy soil microbiome",
        "Suppresses harmful pathogens naturally",
        "Improves nutrient uptake",
        "Long-term soil health improvement"
      ],
      precautions: [
        "Store cultures properly",
        "Don't mix with fungicides",
        "Apply in suitable weather conditions"
      ],
      cost: "high",
      season: ["Spring", "Summer", "Fall"]
    },
    {
      id: "6",
      name: "Crop Rotation Schedule",
      disease: "Soil-borne Diseases, Pest Cycles",
      crop: "All annual crops",
      type: "preventive",
      effectiveness: 75,
      duration: "Multi-year cycle",
      difficulty: "hard",
      ingredients: ["Planning calendar", "Different crop families", "Cover crop seeds"],
      instructions: [
        "Group crops by botanical families",
        "Plan 3-4 year rotation cycles",
        "Include legumes to fix nitrogen",
        "Use cover crops between seasons"
      ],
      benefits: [
        "Breaks disease and pest cycles",
        "Improves soil fertility naturally",
        "Reduces need for external inputs",
        "Maintains biodiversity"
      ],
      precautions: [
        "Requires long-term planning",
        "Need adequate space for rotation",
        "Consider market demands"
      ],
      cost: "low",
      season: ["Year-round planning"]
    }
  ];

  const filteredTreatments = treatments.filter(treatment => {
    const matchesSearch = treatment.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         treatment.disease.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         treatment.crop.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === "all" || treatment.type === selectedCategory;
    const matchesCrop = selectedCrop === "all" || treatment.crop.toLowerCase().includes(selectedCrop);
    
    return matchesSearch && matchesCategory && matchesCrop;
  });

  const getTypeColor = (type: string) => {
    switch (type) {
      case "organic": return "bg-green-100 text-green-800 dark:bg-green-900/20";
      case "biological": return "bg-blue-100 text-blue-800 dark:bg-blue-900/20";
      case "cultural": return "bg-purple-100 text-purple-800 dark:bg-purple-900/20";
      case "preventive": return "bg-orange-100 text-orange-800 dark:bg-orange-900/20";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900/20";
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy": return "text-green-600";
      case "medium": return "text-yellow-600";  
      case "hard": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  const getCostColor = (cost: string) => {
    switch (cost) {
      case "low": return "text-green-600";
      case "medium": return "text-yellow-600";
      case "high": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filter Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Leaf className="size-5" />
            Organic Treatment Library
          </CardTitle>
          <CardDescription>
            Chemical-free solutions for sustainable crop disease management
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
                <Input
                  placeholder="Search treatments, diseases, or crops..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="sm:w-48">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="organic">Organic</SelectItem>
                <SelectItem value="biological">Biological</SelectItem>
                <SelectItem value="cultural">Cultural</SelectItem>
                <SelectItem value="preventive">Preventive</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedCrop} onValueChange={setSelectedCrop}>
              <SelectTrigger className="sm:w-48">
                <SelectValue placeholder="Crop Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Crops</SelectItem>
                <SelectItem value="tomato">Tomato</SelectItem>
                <SelectItem value="potato">Potato</SelectItem>
                <SelectItem value="corn">Corn</SelectItem>
                <SelectItem value="cucumber">Cucumber</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Treatment Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredTreatments.map((treatment) => (
          <Card key={treatment.id} className="h-full">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="text-xl">{treatment.name}</CardTitle>
                  <div className="flex flex-wrap gap-2">
                    <Badge className={getTypeColor(treatment.type)}>
                      {treatment.type}
                    </Badge>
                    <Badge variant="outline">
                      {treatment.effectiveness}% effective
                    </Badge>
                  </div>
                </div>
              </div>
              
              <CardDescription>
                <div className="space-y-1">
                  <p><strong>Target:</strong> {treatment.disease}</p>
                  <p><strong>Crops:</strong> {treatment.crop}</p>
                </div>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="instructions">Method</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4 mt-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <Clock className="size-4 mx-auto mb-1" />
                      <p className="font-medium">Duration</p>
                      <p className="text-muted-foreground">{treatment.duration}</p>
                    </div>
                    <div className="text-center">
                      <div className={`font-medium ${getDifficultyColor(treatment.difficulty)}`}>
                        Difficulty: {treatment.difficulty}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className={`font-medium ${getCostColor(treatment.cost)}`}>
                        Cost: {treatment.cost}
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Key Benefits:</h4>
                    <ul className="space-y-1">
                      {treatment.benefits.slice(0, 3).map((benefit, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </TabsContent>

                <TabsContent value="instructions" className="space-y-4 mt-4">
                  <div>
                    <h4 className="font-medium mb-2">Ingredients:</h4>
                    <ul className="space-y-1">
                      {treatment.ingredients.map((ingredient, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm">
                          <Sprout className="size-4 text-green-600 flex-shrink-0" />
                          <span>{ingredient}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Instructions:</h4>
                    <ol className="space-y-1">
                      {treatment.instructions.map((instruction, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <span className="bg-primary text-primary-foreground size-5 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                            {index + 1}
                          </span>
                          <span>{instruction}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                </TabsContent>

                <TabsContent value="details" className="space-y-4 mt-4">
                  <div>
                    <h4 className="font-medium mb-2 text-yellow-600">Precautions:</h4>
                    <ul className="space-y-1">
                      {treatment.precautions.map((precaution, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <span className="text-yellow-600 font-bold flex-shrink-0">⚠</span>
                          <span>{precaution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Seasonal Application:</h4>
                    <div className="flex flex-wrap gap-1">
                      {treatment.season.map((season, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {season}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <Button className="w-full" variant="outline">
                    <ExternalLink className="size-4 mr-2" />
                    View Full Guide
                  </Button>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTreatments.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Search className="size-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No treatments found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search criteria or browse all treatments.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Quick Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Organic Treatment Tips</CardTitle>
          <CardDescription>Best practices for chemical-free crop management</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Sun className="size-5 text-yellow-500" />
                <div>
                  <p className="font-medium">Timing Matters</p>
                  <p className="text-sm text-muted-foreground">Apply treatments early morning or late evening</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <Droplets className="size-5 text-blue-500" />
                <div>
                  <p className="font-medium">Weather Awareness</p>
                  <p className="text-sm text-muted-foreground">Avoid spraying before rain or in windy conditions</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Wind className="size-5 text-green-500" />
                <div>
                  <p className="font-medium">Prevention First</p>
                  <p className="text-sm text-muted-foreground">Good air circulation prevents many fungal diseases</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <Leaf className="size-5 text-green-600" />
                <div>
                  <p className="font-medium">Rotate Treatments</p>
                  <p className="text-sm text-muted-foreground">Alternate different organic methods to prevent resistance</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}