import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Volume2, VolumeX, Play, Pause, Square, Languages } from "lucide-react";

import { Button } from "@/components/ui/button.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";

export default function VoiceInterface() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("en-US");
  const [audioLevel, setAudioLevel] = useState(0);
  const [isListening, setIsListening] = useState(false);

  // Speech recognition and synthesis refs
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesis | null>(null);

  const languages = [
    { code: "en-US", name: "English", flag: "🇺🇸" },
    { code: "ta-IN", name: "Tamil", flag: "🇮🇳" },
    { code: "hi-IN", name: "Hindi", flag: "🇮🇳" },
    { code: "ur-PK", name: "Urdu", flag: "🇵🇰" }
  ];

  const sampleCommands = [
    "Show me recent crop analyses",
    "What is tomato late blight?", 
    "How do I treat leaf spot disease organically?",
    "Upload image for analysis",
    "Switch to Tamil language"
  ];

  useEffect(() => {
    // Initialize speech recognition if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognitionClass = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = selectedLanguage;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscriptText(prev => prev + finalTranscript + " ");
        }
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsRecording(false);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [selectedLanguage]);

  const startRecording = () => {
    if (recognitionRef.current) {
      setIsRecording(true);
      recognitionRef.current.lang = selectedLanguage;
      recognitionRef.current.start();
    } else {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  const clearTranscript = () => {
    setTranscriptText("");
  };

  const speakText = (text: string) => {
    if (synthesisRef.current && text) {
      // Cancel any ongoing speech
      synthesisRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = selectedLanguage;
      utterance.rate = 0.9;
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      
      synthesisRef.current.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
      setIsPlaying(false);
    }
  };

  const processVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase();
    
    if (lowerCommand.includes("recent") || lowerCommand.includes("history")) {
      speakText("Showing your recent crop analyses.");
    } else if (lowerCommand.includes("blight") || lowerCommand.includes("disease")) {
      speakText("Late blight is a fungal disease that affects tomatoes and potatoes. I recommend organic treatments like neem oil and proper ventilation.");
    } else if (lowerCommand.includes("upload") || lowerCommand.includes("image")) {
      speakText("You can upload crop images by clicking the upload button in the disease detection tab.");
    } else if (lowerCommand.includes("language")) {
      speakText("You can change the language using the language selector.");
    } else {
      speakText("I'm here to help with crop disease detection and organic treatments. Please try asking about diseases, treatments, or uploading images.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Voice Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="size-5" />
            Voice Interface
          </CardTitle>
          <CardDescription>
            Use voice commands to navigate and get information about crop diseases
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Language Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Language</label>
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.code} value={lang.code}>
                    <div className="flex items-center gap-2">
                      <span>{lang.flag}</span>
                      <span>{lang.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Recording Controls */}
          <div className="flex items-center gap-4">
            <Button
              onClick={isRecording ? stopRecording : startRecording}
              size="lg"
              variant={isRecording ? "destructive" : "default"}
              className="flex-1"
            >
              {isRecording ? (
                <>
                  <MicOff className="size-5 mr-2" />
                  Stop Recording
                </>
              ) : (
                <>
                  <Mic className="size-5 mr-2" />
                  Start Recording
                </>
              )}
            </Button>

            <Button
              onClick={clearTranscript}
              variant="outline"
              disabled={!transcriptText}
            >
              Clear
            </Button>
          </div>

          {/* Recording Status */}
          {isListening && (
            <Alert>
              <Mic className="size-4" />
              <AlertDescription>
                <div className="flex items-center gap-2">
                  <span>Listening...</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Transcript Display */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Voice Transcript</label>
              <Badge variant="secondary">
                {transcriptText.split(' ').filter(word => word.length > 0).length} words
              </Badge>
            </div>
            <Textarea
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              placeholder="Your speech will appear here..."
              rows={6}
              className="resize-none"
            />
          </div>

          {/* Text-to-Speech Controls */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Button
                onClick={() => speakText(transcriptText)}
                disabled={!transcriptText || isPlaying}
                variant="outline"
                className="flex-1"
              >
                {isPlaying ? (
                  <>
                    <Pause className="size-4 mr-2" />
                    Speaking...
                  </>
                ) : (
                  <>
                    <Volume2 className="size-4 mr-2" />
                    Read Aloud
                  </>
                )}
              </Button>

              <Button
                onClick={stopSpeaking}
                disabled={!isPlaying}
                variant="outline"
              >
                <Square className="size-4" />
              </Button>
            </div>

            <Button
              onClick={() => processVoiceCommand(transcriptText)}
              disabled={!transcriptText}
              className="w-full"
            >
              Process Command
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Sample Commands */}
      <Card>
        <CardHeader>
          <CardTitle>Sample Voice Commands</CardTitle>
          <CardDescription>
            Try these example commands to interact with Croposcope
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sampleCommands.map((command, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => {
                  setTranscriptText(command);
                  speakText(command);
                }}
              >
                <span className="text-sm">{command}</span>
                <Button size="sm" variant="ghost">
                  <Play className="size-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Accessibility Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Volume2 className="size-5" />
            Accessibility Features
          </CardTitle>
          <CardDescription>
            Features designed for users with hearing impairments
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <Languages className="size-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">Visual Feedback</p>
                <ul className="list-disc list-inside text-sm space-y-1">
                  <li>Real-time transcript display during speech recognition</li>
                  <li>Visual indicators for recording status and audio levels</li>
                  <li>Text-to-speech with synchronized visual feedback</li>
                  <li>Multi-language support for global accessibility</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <Volume2 className="size-8 text-primary mx-auto mb-2" />
              <p className="text-sm font-medium">Audio to Text</p>
              <p className="text-xs text-muted-foreground">Convert speech to readable text</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Languages className="size-8 text-primary mx-auto mb-2" />
              <p className="text-sm font-medium">Multi-Language</p>
              <p className="text-xs text-muted-foreground">Support for 4 languages</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}