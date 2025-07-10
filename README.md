# AI Radiology Assistant

A professional AI-powered radiology assistant that analyzes chest X-ray images and provides detailed, structured radiological reports using Google's Gemini AI.

## Features

- **Chest X-ray Analysis**: Specialized in analyzing chest X-ray images (PA, AP, and Lateral views)
- **Structured Reports**: Provides comprehensive radiological reports with standardized sections
- **WhatsApp Integration**: Receives images via WhatsApp webhook and responds with analysis
- **Professional Format**: Medical-grade reporting with proper terminology and structure
- **Image Quality Assessment**: Evaluates technical adequacy of submitted images

## Report Structure

The AI generates structured reports containing:

1. **Clinical Information**: View type and image quality assessment
2. **Findings**: 
   - Lungs and Pleura
   - Heart and Mediastinum
   - Bones and Soft Tissues
3. **Impression**: Summary of key findings
4. **Recommendations**: Clinical correlation and follow-up suggestions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
META_PHONE_ID=your_phone_id
META_ACCESS_TOKEN=your_access_token
GEMINI_API_KEY=your_gemini_api_key
```

3. Run the application:
```bash
python App.py
```

## API Endpoints

- `GET /webhook` - Webhook verification for Meta/WhatsApp
- `POST /webhook` - Receives messages and images from WhatsApp
- `GET /health` - Health check endpoint

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)

## Image Quality Requirements

- Adequate penetration
- Proper positioning
- Full inspiration
- No motion artifacts

## Important Disclaimer

**This AI analysis is for educational purposes only and should not replace professional medical diagnosis. For urgent medical concerns, please contact your healthcare provider immediately.**

## Usage Flow

1. User sends greeting or message to WhatsApp bot
2. Bot responds with instructions to upload chest X-ray image
3. User uploads chest X-ray image
4. Bot processes image using Gemini AI
5. Bot returns detailed radiological analysis report
6. User can upload additional images or end conversation

## Technical Details

- **Framework**: Flask
- **AI Model**: Google Gemini 1.5 Flash
- **Image Processing**: Direct integration with Gemini Vision API
- **Messaging**: WhatsApp Business API via Meta Graph API

## Error Handling

The system includes robust error handling for:
- Invalid image formats
- Image download failures
- API communication errors
- Image analysis errors

## Security

- Environment variable configuration
- Access token validation
- Webhook verification
- Request logging and monitoring
