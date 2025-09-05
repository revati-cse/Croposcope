# 🌾 Croposcope - AI-Powered Crop Disease Detection

Croposcope is an advanced crop disease detection platform that uses AI-powered image analysis to identify plant diseases and provides organic, chemical-free treatment recommendations. Built for farmers who want sustainable, eco-friendly solutions for crop health management.

## 🚀 Features

### Core Functionality
- **AI Disease Detection**: EfficientNetV2-powered CNN model for accurate crop disease identification
- **Image Analysis**: Upload or capture crop images for instant AI analysis
- **Organic Treatments**: Chemical-free, eco-friendly treatment recommendations
- **Multi-crop Support**: Supports various crops including tomatoes, potatoes, corn, and more

### Accessibility & Usability
- **Voice Recognition**: Voice-to-text conversion for hands-free operation
- **Multilingual Support**: Available in English, Tamil, Hindi, and Urdu
- **Accessibility Features**: Designed for deaf and hearing-impaired users with visual feedback
- **Mobile Responsive**: Optimized for both desktop and mobile devices
- **Dark/Light Mode**: Theme switching for comfortable viewing

### Advanced Features
- **Treatment Library**: Comprehensive database of organic treatment methods
- **Analysis History**: Track and manage crop disease detection history
- **Voice Interface**: Speak commands and get audio responses
- **Field Management**: Organize analyses by field locations
- **Analytics Dashboard**: Insights and trends about crop health patterns

## 🛠️ Technology Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for development and building
- **Tailwind CSS 4** for styling
- **shadcn/ui** for UI components
- **React Router v7** for navigation
- **Web Speech API** for voice features

### Backend & Database
- **Convex** for backend functions and real-time database
- **Authentication** via OIDC (managed by Hercules)
- **File Storage** for crop images

### AI & ML (Conceptual Implementation)
- **EfficientNetV2** CNN architecture
- **Advanced RAG** for treatment recommendations
- **PlantVillage Dataset** integration
- **Kaggle Datasets** for training

## 📁 Project Structure

```
croposcope/
├── src/
│   ├── components/
│   │   ├── providers/          # App providers (Auth, Theme, etc.)
│   │   └── ui/                 # Reusable UI components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility functions
│   ├── pages/                  # Page components
│   │   ├── dashboard/          # Dashboard-specific components
│   │   │   └── _components/    # Dashboard sub-components
│   │   ├── Index.tsx           # Landing page
│   │   ├── Login.tsx           # Authentication page
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   └── NotFound.tsx        # 404 page
│   ├── App.tsx                 # Root application component
│   ├── main.tsx               # Application entry point
│   └── index.css              # Global styles
├── convex/
│   ├── _generated/            # Auto-generated Convex files
│   ├── analyses.ts            # Crop analysis functions
│   ├── auth.config.js         # Authentication configuration
│   ├── schema.ts              # Database schema
│   ├── treatments.ts          # Treatment recommendation functions
│   ├── uploads.ts             # File upload functions
│   └── users.ts               # User management functions
└── public/                    # Static assets
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm, yarn, or pnpm package manager
- Modern web browser with Web Speech API support (Chrome, Edge)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd croposcope
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   # or
   yarn install
   ```

3. **Start the development servers**
   ```bash
   # Start both Vite and Convex in development mode
   npm run dev
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5173`
   - The Convex backend will be automatically configured

### 🎮 Using the Application

1. **Authentication**: Click "Sign In" to authenticate via the Hercules OIDC system
2. **Disease Detection**: 
   - Navigate to the Dashboard
   - Upload a crop image or use the camera
   - Get AI-powered disease analysis results
3. **Voice Features**:
   - Use the Voice tab for hands-free interaction
   - Switch between supported languages
   - Speak commands and receive audio responses
4. **Treatment Recommendations**: Browse organic treatment options for detected diseases
5. **Analysis History**: Review past analyses and track treatment progress

## 🔧 Configuration

### Environment Variables
The application uses Convex for backend services. Environment variables are automatically configured by the Hercules platform:

- `VITE_HERCULES_OIDC_AUTHORITY`: OIDC authentication endpoint
- `VITE_HERCULES_OIDC_CLIENT_ID`: OIDC client identifier
- `CONVEX_DEPLOYMENT`: Convex deployment URL

### Language Support
Supported languages with their codes:
- English (en-US)
- Tamil (ta-IN) 
- Hindi (hi-IN)
- Urdu (ur-PK)

## 📱 Mobile Usage

Croposcope is fully responsive and optimized for mobile devices:

- **Touch-friendly interface**: Large buttons and touch targets
- **Camera integration**: Use device camera to capture crop images
- **Voice recognition**: Works on mobile browsers supporting Web Speech API
- **Offline-ready**: Core features work without internet connectivity (planned feature)

## 🧪 For Hackathons & Competitions

### Key Differentiators
1. **Organic Focus**: Exclusively chemical-free treatment recommendations
2. **Accessibility**: Voice features and multilingual support for inclusivity  
3. **Real-world Impact**: Addresses actual farmer needs with practical solutions
4. **Technology Integration**: Combines AI, voice recognition, and modern web technologies
5. **User Experience**: Intuitive interface designed for non-technical users

### Demo Script
1. Show multilingual landing page
2. Demonstrate voice navigation
3. Upload crop image for AI analysis
4. Display organic treatment recommendations
5. Show analysis history and insights
6. Highlight accessibility features

## 🚀 Deployment

### Hercules Platform (Current)
The app is designed to run on the Hercules platform with:
- Automatic deployment via "Publish" button
- Managed hosting on `.onhercules.com` domains
- Integrated Convex backend
- Built-in authentication system

### Self-Hosting (Alternative)
For self-hosting, you would need:
1. Convex deployment for backend
2. Vite build for frontend
3. OIDC provider configuration
4. Environment variable setup

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

### AI/ML Improvements
- Train actual EfficientNetV2 model with crop disease datasets
- Implement real-time disease detection API
- Add more crop types and diseases
- Improve accuracy with data augmentation

### Features
- Offline functionality with service workers
- GPS integration for field mapping
- Weather data integration
- Community features for farmers
- Advanced analytics and reporting

### Accessibility
- Screen reader optimization
- High contrast themes
- Keyboard navigation improvements
- Sign language support

## 📚 Educational Resources

### Crop Disease Information
- Organic treatment methods
- Integrated pest management
- Sustainable farming practices
- Disease prevention strategies

### Technology Learning
- React development patterns
- Convex backend integration
- Web Speech API usage
- Responsive design principles

## 📄 License

This project is part of a hackathon submission and educational resource. 

## 🙏 Acknowledgments

- **PlantVillage**: Disease image datasets
- **Kaggle**: Machine learning datasets and community
- **Hercules Platform**: Development and hosting infrastructure
- **Convex**: Backend-as-a-service platform
- **shadcn/ui**: Beautiful and accessible UI components

## 📞 Support

For questions about this hackathon project:
- Check the code comments for implementation details
- Review the component structure for understanding the architecture
- Examine the Convex schema for database design patterns

---

**Built with ❤️ for sustainable agriculture and hackathon excellence!** 🌱