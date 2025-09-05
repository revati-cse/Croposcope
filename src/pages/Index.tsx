import { useState } from "react";
import { Link } from "react-router-dom";
import { Leaf, Camera, Mic, Globe, Moon, Sun, Volume2, Users } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";

export default function Index() {
  const { theme, setTheme } = useTheme();
  const [currentLang, setCurrentLang] = useState("en");

  const translations = {
    en: {
      title: "Croposcope",
      subtitle: "AI-Powered Crop Disease Detection & Organic Treatment Solutions",
      description: "Advanced machine learning technology to identify crop diseases and provide chemical-free treatment recommendations for sustainable farming.",
      getStarted: "Get Started",
      learnMore: "Learn More",
      features: "Key Features",
      aiDetection: "AI Disease Detection",
      aiDetectionDesc: "EfficientNetV2-powered CNN model for accurate crop disease identification",
      voiceSupport: "Voice Recognition",
      voiceSupportDesc: "Voice-to-text conversion for hands-free operation in the field",
      multilingual: "Multilingual Support",
      multilingualDesc: "Available in English, Tamil, Hindi, and Urdu languages",
      accessibility: "Accessibility Features",
      accessibilityDesc: "Designed for deaf and hearing-impaired users with visual cues",
      organicTreatment: "Organic Treatment",
      organicTreatmentDesc: "Chemical-free, eco-friendly treatment recommendations",
      offlineReady: "Mobile & Offline Ready",
      offlineReadyDesc: "Works on mobile devices with offline capabilities"
    },
    ta: {
      title: "க்ரோபோஸ்கோப்",
      subtitle: "செயற்கை நுண்ணறிவு-இயங்கும் பயிர் நோய் கண்டறிதல் & இயற்கை சிகிச்சை தீர்வுகள்",
      description: "நிலையான விவசாயத்திற்கான பயிர் நோய்களை அடையாளம் காணவும் இரசாயன-இல்லாத சிகிச்சை பரிந்துரைகளை வழங்கவும் மேம்பட்ட இயந்திர கற்றல் தொழில்நுட்பம்.",
      getStarted: "தொடங்கவும்",
      learnMore: "மேலும் அறிக",
      features: "முக்கிய அம்சங்கள்",
      aiDetection: "செயற்கை நுண்ணறிவு நோய் கண்டறிதல்",
      aiDetectionDesc: "துல்லியமான பயிர் நோய் அடையாளத்திற்கான EfficientNetV2-இயங்கும் CNN மாதிரி",
      voiceSupport: "குரல் அங்கீகாரம்",
      voiceSupportDesc: "வயலில் கைகள்-இல்லாத செயல்பாட்டிற்கான குரல்-இருந்து-உரை மாற்றம்",
      multilingual: "பல மொழி ஆதரவு",
      multilingualDesc: "ஆங்கிலம், தமிழ், ஹிந்தி மற்றும் உருது மொழிகளில் கிடைக்கும்",
      accessibility: "அணுகல் அம்சங்கள்",
      accessibilityDesc: "காது கேளாத மற்றும் செவித்திறன் குறைபாடுள்ள பயனர்களுக்கு காட்சி குறிப்புகளுடன் வடிவமைக்கப்பட்டுள்ளது",
      organicTreatment: "இயற்கை சிகிச்சை",
      organicTreatmentDesc: "இரசாயன-இல்லாத, சுற்றுச்சூழல் நட்பு சிகிச்சை பரிந்துரைகள்",
      offlineReady: "மொபைல் & ஆஃப்லைன் தயார்",
      offlineReadyDesc: "ஆஃப்லைன் திறன்களுடன் மொபைல் சாதனங்களில் வேலை செய்கிறது"
    },
    hi: {
      title: "क्रोपोस्कोप",
      subtitle: "एआई-संचालित फसल रोग का पता लगाना और जैविक उपचार समाधान",
      description: "टिकाऊ खेती के लिए फसल की बीमारियों की पहचान करने और रसायन-मुक्त उपचार की सिफारिश प्रदान करने के लिए उन्नत मशीन लर्निंग तकनीक।",
      getStarted: "शुरू करें",
      learnMore: "और जानें",
      features: "मुख्य विशेषताएं",
      aiDetection: "एआई रोग का पता लगाना",
      aiDetectionDesc: "सटीक फसल रोग की पहचान के लिए EfficientNetV2-संचालित CNN मॉडल",
      voiceSupport: "आवाज की पहचान",
      voiceSupportDesc: "खेत में हाथों-मुक्त संचालन के लिए आवाज-से-टेक्स्ट रूपांतरण",
      multilingual: "बहुभाषी समर्थन",
      multilingualDesc: "अंग्रेजी, तमिल, हिंदी और उर्दू भाषाओं में उपलब्ध",
      accessibility: "पहुंच सुविधाएं",
      accessibilityDesc: "बधिर और सुनने में अक्षम उपयोगकर्ताओं के लिए दृश्य संकेतों के साथ डिज़ाइन किया गया",
      organicTreatment: "जैविक उपचार",
      organicTreatmentDesc: "रसायन-मुक्त, पर्यावरण-अनुकूल उपचार की सिफारिशें",
      offlineReady: "मोबाइल और ऑफ़लाइन तैयार",
      offlineReadyDesc: "ऑफ़लाइन क्षमताओं के साथ मोबाइल डिवाइस पर काम करता है"
    },
    ur: {
      title: "کروپوسکوپ",
      subtitle: "AI-طاقت سے چلنے والا فصل کی بیماری کی تشخیص اور نامیاتی علاج کے حل",
      description: "پائیدار کاشتکاری کے لیے فصل کی بیماریوں کی شناخت اور کیمیکل فری علاج کی سفارشات فراہم کرنے کے لیے جدید مشین لرننگ ٹیکنالوجی۔",
      getStarted: "شروع کریں",
      learnMore: "مزید جانیں",
      features: "اہم خصوصیات",
      aiDetection: "AI بیماری کی تشخیص",
      aiDetectionDesc: "درست فصل کی بیماری کی شناخت کے لیے EfficientNetV2-طاقت سے چلنے والا CNN ماڈل",
      voiceSupport: "آواز کی پہچان",
      voiceSupportDesc: "کھیت میں ہاتھوں سے آزاد آپریشن کے لیے آواز سے ٹیکسٹ تبدیلی",
      multilingual: "کثیر لسانی سپورٹ",
      multilingualDesc: "انگریزی، تمل، ہندی اور اردو زبانوں میں دستیاب",
      accessibility: "رسائی کی سہولات",
      accessibilityDesc: "بہرے اور سننے میں معذور صارفین کے لیے بصری اشاروں کے ساتھ ڈیزائن کیا گیا",
      organicTreatment: "نامیاتی علاج",
      organicTreatmentDesc: "کیمیکل فری، ماحول دوست علاج کی سفارشات",
      offlineReady: "موبائل اور آف لائن تیار",
      offlineReadyDesc: "آف لائن صلاحیات کے ساتھ موبائل ڈیوائسز پر کام کرتا ہے"
    }
  };

  const t = translations[currentLang as keyof typeof translations];

  const features = [
    {
      icon: <Camera className="size-8 text-primary" />,
      title: t.aiDetection,
      description: t.aiDetectionDesc
    },
    {
      icon: <Mic className="size-8 text-primary" />,
      title: t.voiceSupport,
      description: t.voiceSupportDesc
    },
    {
      icon: <Globe className="size-8 text-primary" />,
      title: t.multilingual,
      description: t.multilingualDesc
    },
    {
      icon: <Volume2 className="size-8 text-primary" />,
      title: t.accessibility,
      description: t.accessibilityDesc
    },
    {
      icon: <Leaf className="size-8 text-primary" />,
      title: t.organicTreatment,
      description: t.organicTreatmentDesc
    },
    {
      icon: <Users className="size-8 text-primary" />,
      title: t.offlineReady,
      description: t.offlineReadyDesc
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="size-8 text-primary" />
            <h1 className="text-2xl font-bold">{t.title}</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Language Selector */}
            <select 
              value={currentLang}
              onChange={(e) => setCurrentLang(e.target.value)}
              className="bg-background border border-border rounded-md px-3 py-1 text-sm"
            >
              <option value="en">English</option>
              <option value="ta">தமிழ்</option>
              <option value="hi">हिंदी</option>
              <option value="ur">اردو</option>
            </select>
            
            {/* Theme Toggle */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>
            
            {/* Sign In Button */}
            <Button asChild>
              <Link to="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <Badge variant="secondary" className="mb-4">
            Powered by EfficientNetV2 & Advanced RAG
          </Badge>
          
          <h2 className="text-5xl font-bold tracking-tight mb-6 text-balance">
            {t.subtitle}
          </h2>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            {t.description}
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Button size="lg" asChild>
              <Link to="/dashboard">{t.getStarted}</Link>
            </Button>
            <Button variant="outline" size="lg">
              {t.learnMore}
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-muted/50">
        <div className="container mx-auto max-w-6xl">
          <h3 className="text-3xl font-bold text-center mb-12">{t.features}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="h-full">
                <CardHeader>
                  <div className="mb-4">{feature.icon}</div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-4xl font-bold text-primary mb-2">95%</h4>
              <p className="text-muted-foreground">Accuracy Rate</p>
            </div>
            <div>
              <h4 className="text-4xl font-bold text-primary mb-2">50+</h4>
              <p className="text-muted-foreground">Crop Diseases Detected</p>
            </div>
            <div>
              <h4 className="text-4xl font-bold text-primary mb-2">4</h4>
              <p className="text-muted-foreground">Languages Supported</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Leaf className="size-6 text-primary" />
              <span className="font-semibold">{t.title}</span>
            </div>
            
            <div className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Croposcope. Empowering sustainable agriculture.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}