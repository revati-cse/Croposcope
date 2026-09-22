class CameraManager {
  constructor() {
    this.stream = null;
    this.video = null;
    this.canvas = null;
    this.context = null;
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      // Check if camera is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported on this device');
      }

      // Create video element
      this.video = document.createElement('video');
      this.video.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 1000;
      `;
      this.video.autoplay = true;
      this.video.playsInline = true;

      // Create canvas for capturing
      this.canvas = document.createElement('canvas');
      this.context = this.canvas.getContext('2d');

      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize camera:', error);
      throw error;
    }
  }

  async startCamera(facingMode = 'environment') {
    await this.initialize();

    try {
      // Stop existing stream if any
      this.stopCamera();

      // Request camera access
      const constraints = {
        video: {
          facingMode: { ideal: facingMode },
          width: { ideal: 1920, max: 1920 },
          height: { ideal: 1080, max: 1080 }
        },
        audio: false
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;

      // Wait for video to be ready
      await new Promise((resolve, reject) => {
        this.video.onloadedmetadata = () => {
          this.video.play()
            .then(resolve)
            .catch(reject);
        };
        this.video.onerror = reject;
      });

      return this.video;

    } catch (error) {
      console.error('Failed to start camera:', error);
      throw new Error('Failed to access camera. Please check permissions.');
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
      });
      this.stream = null;
    }

    if (this.video) {
      this.video.srcObject = null;
    }
  }

  async capturePhoto() {
    if (!this.video || !this.stream) {
      throw new Error('Camera not started');
    }

    try {
      // Set canvas size to video dimensions
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;

      // Draw current video frame to canvas
      this.context.drawImage(this.video, 0, 0);

      // Convert to blob
      return new Promise((resolve, reject) => {
        this.canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to capture photo'));
            }
          },
          'image/jpeg',
          0.9
        );
      });

    } catch (error) {
      console.error('Failed to capture photo:', error);
      throw error;
    }
  }

  async switchCamera() {
    const currentFacingMode = this.getCurrentFacingMode();
    const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';
    
    return this.startCamera(newFacingMode);
  }

  getCurrentFacingMode() {
    if (!this.stream) return 'environment';
    
    const videoTrack = this.stream.getVideoTracks()[0];
    const settings = videoTrack.getSettings();
    return settings.facingMode || 'environment';
  }

  async getAvailableCameras() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'videoinput');
    } catch (error) {
      console.error('Failed to get available cameras:', error);
      return [];
    }
  }

  // Check camera permissions
  async checkCameraPermission() {
    try {
      if (!navigator.permissions) {
        // Try to access camera to check permission
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: true, 
          audio: false 
        });
        stream.getTracks().forEach(track => track.stop());
        return 'granted';
      }

      const permission = await navigator.permissions.query({ name: 'camera' });
      return permission.state;
    } catch (error) {
      console.error('Failed to check camera permission:', error);
      return 'denied';
    }
  }

  // Request camera permission
  async requestCameraPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: false 
      });
      
      // Stop the stream immediately - we just needed permission
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Camera permission denied:', error);
      return false;
    }
  }

  // Create camera UI overlay
  createCameraOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'camera-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1001;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: transparent;
      pointer-events: none;
    `;

    // Header with close button
    const header = document.createElement('div');
    header.style.cssText = `
      padding: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 100%);
    `;

    const closeButton = document.createElement('button');
    closeButton.innerHTML = '✕';
    closeButton.style.cssText = `
      background: rgba(0,0,0,0.5);
      border: none;
      color: white;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      font-size: 1.2rem;
      cursor: pointer;
      pointer-events: all;
    `;
    closeButton.onclick = () => this.closeCameraUI();

    // Camera viewfinder
    const viewfinder = document.createElement('div');
    viewfinder.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 280px;
      height: 280px;
      border: 2px solid rgba(255,255,255,0.8);
      border-radius: 12px;
      box-shadow: 0 0 0 9999px rgba(0,0,0,0.3);
    `;

    // Footer with controls
    const footer = document.createElement('div');
    footer.style.cssText = `
      padding: 2rem 1rem;
      display: flex;
      justify-content: center;
      align-items: center;
      background: linear-gradient(0deg, rgba(0,0,0,0.5) 0%, transparent 100%);
      gap: 2rem;
    `;

    // Capture button
    const captureButton = document.createElement('button');
    captureButton.style.cssText = `
      width: 70px;
      height: 70px;
      border-radius: 50%;
      background: white;
      border: 4px solid #22c55e;
      cursor: pointer;
      pointer-events: all;
      transition: transform 0.1s;
    `;
    captureButton.onclick = async () => {
      try {
        const photo = await this.capturePhoto();
        this.onPhotoCaptured(photo);
      } catch (error) {
        console.error('Failed to capture photo:', error);
      }
    };

    // Switch camera button
    const switchButton = document.createElement('button');
    switchButton.innerHTML = '🔄';
    switchButton.style.cssText = `
      background: rgba(0,0,0,0.5);
      border: none;
      color: white;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      font-size: 1.5rem;
      cursor: pointer;
      pointer-events: all;
    `;
    switchButton.onclick = () => this.switchCamera();

    header.appendChild(closeButton);
    footer.appendChild(switchButton);
    footer.appendChild(captureButton);
    overlay.appendChild(header);
    overlay.appendChild(viewfinder);
    overlay.appendChild(footer);

    return overlay;
  }

  openCameraUI() {
    // Add video and overlay to DOM
    document.body.appendChild(this.video);
    
    const overlay = this.createCameraOverlay();
    document.body.appendChild(overlay);

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    return this.startCamera();
  }

  closeCameraUI() {
    this.stopCamera();

    // Remove elements from DOM
    const overlay = document.getElementById('camera-overlay');
    if (overlay) {
      overlay.remove();
    }

    if (this.video && this.video.parentNode) {
      this.video.parentNode.removeChild(this.video);
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  onPhotoCaptured(photoBlob) {
    // Override this method to handle captured photos
    console.log('Photo captured:', photoBlob);
    
    // Convert blob to file
    const file = new File([photoBlob], 'camera-capture.jpg', {
      type: 'image/jpeg'
    });

    // Trigger custom event
    const event = new CustomEvent('photoCaptured', {
      detail: { file, blob: photoBlob }
    });
    
    document.dispatchEvent(event);

    // Close camera UI
    this.closeCameraUI();
  }
}

// Export singleton instance
export const cameraManager = new CameraManager();

// Global camera functions for easy access
window.openCamera = () => cameraManager.openCameraUI();
window.closeCamera = () => cameraManager.closeCameraUI();

export default CameraManager;