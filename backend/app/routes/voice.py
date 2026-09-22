from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import VoiceInteraction
import speech_recognition as sr
import pyttsx3
import threading
import os
import tempfile
import wave

voice_bp = Blueprint('voice', __name__)

# Initialize speech recognition and synthesis
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en-US': 'English (US)',
    'ta-IN': 'Tamil (India)',
    'hi-IN': 'Hindi (India)',
    'ur-PK': 'Urdu (Pakistan)'
}

def process_voice_command(transcript, language='en-US'):
    """Process voice command and return appropriate response"""
    command_lower = transcript.lower().strip()
    
    # Define command patterns and responses
    commands = {
        'navigation': {
            'patterns': ['show', 'go to', 'navigate', 'open'],
            'responses': {
                'en-US': 'Navigating to the requested section.',
                'ta-IN': 'கோரிய பிரிவுக்கு செல்கிறது.',
                'hi-IN': 'अनुरोधित अनुभाग पर जा रहे हैं।',
                'ur-PK': 'درخواست کردہ سیکشن پر جا رہے ہیں۔'
            }
        },
        'analysis': {
            'patterns': ['analyze', 'detect', 'disease', 'crop', 'upload'],
            'responses': {
                'en-US': 'I can help you analyze crop images for disease detection.',
                'ta-IN': 'நோய் கண்டறிதலுக்காக பயிர் படங்களை பகுப்பாய்வு செய்ய உதவ முடியும்.',
                'hi-IN': 'मैं रोग का पता लगाने के लिए फसल की तस्वीरों का विश्लेषण करने में आपकी मदद कर सकता हूं।',
                'ur-PK': 'میں بیماری کی تشخیص کے لیے فصل کی تصاویر کا تجزیہ کرنے میں آپ کی مدد کر سکتا ہوں۔'
            }
        },
        'treatment': {
            'patterns': ['treatment', 'cure', 'organic', 'remedy', 'help'],
            'responses': {
                'en-US': 'I can suggest organic treatments based on detected diseases.',
                'ta-IN': 'கண்டறியப்பட்ட நோய்களின் அடிப்படையில் இயற்கை சிகிச்சைகளை பரிந்துரைக்க முடியும்.',
                'hi-IN': 'मैं पाई गई बीमारियों के आधार पर जैविक उपचार सुझा सकता हूं।',
                'ur-PK': 'میں دریافت شدہ بیماریوں کی بنیاد پر نامیاتی علاج تجویز کر سکتا ہوں۔'
            }
        },
        'history': {
            'patterns': ['history', 'past', 'previous', 'recent'],
            'responses': {
                'en-US': 'Showing your recent crop analysis history.',
                'ta-IN': 'உங்கள் சமீபத்திய பயிர் பகுப்பாய்வு வரலாறு காட்டப்படுகிறது.',
                'hi-IN': 'आपका हालिया फसल विश्लेषण इतिहास दिखा रहे हैं।',
                'ur-PK': 'آپ کی حالیہ فصل کے تجزیے کی تاریخ دکھا رہے ہیں۔'
            }
        }
    }
    
    # Find matching command
    for command_type, command_data in commands.items():
        for pattern in command_data['patterns']:
            if pattern in command_lower:
                response = command_data['responses'].get(language, command_data['responses']['en-US'])
                return command_type, response
    
    # Default response
    default_responses = {
        'en-US': 'I can help you with crop disease detection, treatments, and analysis history.',
        'ta-IN': 'பயிர் நோய் கண்டறிதல், சிகிச்சைகள் மற்றும் பகுப்பாய்வு வரலாறு ஆகியவற்றில் உதவ முடியும்.',
        'hi-IN': 'मैं फसल रोग की पहचान, उपचार और विश्लेषण इतिहास में आपकी मदद कर सकता हूं।',
        'ur-PK': 'میں فصل کی بیماری کی تشخیص، علاج اور تجزیے کی تاریخ میں آپ کی مدد کر سکتا ہوں۔'
    }
    
    return 'general', default_responses.get(language, default_responses['en-US'])

@voice_bp.route('/process', methods=['POST'])
@jwt_required()
def process_command():
    """Process voice command and return response"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        transcript = data.get('transcript', '').strip()
        language = data.get('language', 'en-US')
        
        if not transcript:
            return jsonify({'error': 'Transcript is required'}), 400
        
        if language not in SUPPORTED_LANGUAGES:
            language = 'en-US'  # Default to English
        
        # Process the command
        command_type, response_text = process_voice_command(transcript, language)
        
        # Save interaction to database
        interaction = VoiceInteraction(
            user_id=user_id,
            transcript=transcript,
            language_code=language,
            command_type=command_type,
            response_text=response_text
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'command_type': command_type,
            'response_text': response_text,
            'language': language,
            'success': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/synthesize', methods=['POST'])
@jwt_required()
def synthesize_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en-US')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
        
        # Configure TTS engine
        tts_engine.setProperty('rate', 150)  # Speed of speech
        tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Set voice based on language (if available)
        voices = tts_engine.getProperty('voices')
        for voice in voices:
            if language.startswith('en') and 'english' in voice.name.lower():
                tts_engine.setProperty('voice', voice.id)
                break
            # Add other language voice selection logic here
        
        # Generate speech
        tts_engine.save_to_file(text, temp_path)
        tts_engine.runAndWait()
        
        # Read the audio file
        try:
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return audio_data, 200, {
                'Content-Type': 'audio/wav',
                'Content-Disposition': 'attachment; filename="speech.wav"'
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/interactions', methods=['GET'])
@jwt_required()
def get_interactions():
    """Get user's voice interaction history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        interactions = VoiceInteraction.query.filter_by(user_id=user_id)\
                                          .order_by(VoiceInteraction.created_at.desc())\
                                          .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'interactions': [{
                'id': interaction.id,
                'transcript': interaction.transcript,
                'language_code': interaction.language_code,
                'command_type': interaction.command_type,
                'response_text': interaction.response_text,
                'created_at': interaction.created_at.isoformat()
            } for interaction in interactions.items],
            'total': interactions.total,
            'pages': interactions.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'languages': [
            {
                'code': code,
                'name': name,
                'display_name': name
            }
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    })

@voice_bp.route('/commands', methods=['GET'])
def get_voice_commands():
    """Get list of available voice commands"""
    commands = {
        'navigation': [
            'Show dashboard',
            'Go to analysis',
            'Open treatments',
            'Show history'
        ],
        'analysis': [
            'Analyze crop image',
            'Detect disease',
            'Upload image for analysis',
            'Show recent analyses'
        ],
        'treatment': [
            'Show organic treatments',
            'How to treat leaf spot',
            'Organic remedies for blight',
            'Prevention methods'
        ],
        'general': [
            'Help me with crops',
            'What can you do',
            'Show available options',
            'Voice commands'
        ]
    }
    
    return jsonify({'commands': commands})