# Voice Interview Feature - Quick Start Guide

## What's New?

The Voice Interview feature allows candidates to record verbal responses to interview questions. The system automatically transcribes their speech, analyzes communication skills, and generates a communication score (0-100) that appears on their profile.

## Quick Setup

### Backend Services
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Services
```bash
cd frontend
npm install
npm run dev
```

Both services should be running:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173

## Using the Voice Interview Feature

### Step 1: Start Candidate Interview
1. Open http://localhost:5173
2. Navigate to a candidate's profile
3. Click "Start Interview" button

### Step 2: Switch to Voice Tab
You'll see two tabs at the top:
- **Interview** - Traditional text-based with star ratings
- **🎤 Voice Interview** - New glowing voice recording tab (click this!)

The Voice Interview tab has a beautiful glowing effect that:
- Pulses with blue light when selected
- Shows a sparking microphone icon
- Has a shimmer effect on hover

### Step 3: Record Your Response
1. Click the **"🎤 Start Recording"** button
2. Speak your answer clearly
3. Click the **"⏹ Stop Recording"** button
4. Wait for processing (~1 second)

### Step 4: View Your Results
After recording, you'll see:
- **Transcript**: Your speech converted to text
- **Communication Score**: Overall score (0-100)
- **4 Metrics**:
  - 🎯 **Clarity** (0-100) - How clear your speech is
  - 💪 **Confidence** (0-100) - How confident you sound
  - ✅ **Relevance** (0-100) - How relevant to the question
  - ⏱️ **Speaking Pace** (0-100) - Speed of speech

Each metric shows:
- A progress bar
- Your score out of 100
- Color-coded feedback

### Step 5: Record Again or Move On
You can:
- Click **"Record Again"** to re-record the response
- Move to the next question
- Switch back to the Interview tab for traditional rating

## Microphone Setup

### First Time Using Voice Recording?

You need to give permission to use your microphone:

1. **When you click "Start Recording"**, your browser will ask:
   > "Allow screen-u.local to access your microphone?"

2. **Click "Allow"** (or "Allow once" depending on your browser)

3. **Done!** You can now record

### Microphone Permission Already Denied?

If you see this error:
> "Microphone permission denied. Please check your browser settings."

**Fix it:**
1. Look for the **camera/microphone icon** in your browser's address bar
2. Click it and select **"Microphone" → "Allow"**
3. **Reload the page**
4. Try recording again

### Don't Have a Microphone?

- Connect an external microphone to your computer
- Or use your laptop's built-in microphone
- Test it in your system settings first

## Viewing Communication Scores

After recording voice responses, candidates' profiles will show:

### On Interview Page
- Voice Interview responses listed under the Voice tab
- Each recording shows its transcript and score

### On Candidate Detail Page
- **Communication Score Ring** displays next to resume score
- Shows overall communication performance
- **Voice Profile Section** shows breakdown:
  - Clarity score
  - Confidence score
  - Relevance score
  - Speaking pace score

Example:
```
Overall Score: 95   |   Skills: 100   |   Experience: 84   |   Communication: 49
```

## Score Interpretation

| Score Range | Interpretation |
|------------|-----------------|
| 80-100 | Excellent communication skills |
| 60-79 | Good communication, room for improvement |
| 40-59 | Fair communication, needs development |
| 20-39 | Poor communication, significant gaps |
| 0-19 | Very poor communication |

### Individual Metrics
- **Clarity 75+**: Crystal clear speech
- **Confidence 70+**: Very confident delivery
- **Relevance 75+**: Highly relevant answer
- **Speaking Pace 70+**: Ideal speaking speed

## Supported Audio Formats

The system accepts:
- ✅ WebM (default from browser recording)
- ✅ WAV (standard uncompressed)
- ✅ MP3 (compressed audio)
- ✅ OGG (open format)

The browser will automatically record in WebM format, which is ideal for web use.

## Browser Compatibility

| Browser | Works? | Notes |
|---------|--------|-------|
| Chrome | ✅ | Full support, recommended |
| Firefox | ✅ | Full support, excellent |
| Edge | ✅ | Full support |
| Safari | ⚠️ | iOS 14.5+ required |
| Internet Explorer | ❌ | Not supported |

## Tips for Best Results

### Before Recording
1. **Test your microphone** - Use browser settings to verify it works
2. **Choose a quiet location** - Minimize background noise
3. **Check your internet** - Stable connection recommended
4. **Read the question** - Understand what you're answering

### While Recording
1. **Speak clearly** - Enunciate your words
2. **Use natural pace** - Not too fast or slow
3. **Answer fully** - 30-60 seconds is ideal
4. **Stay relevant** - Address the specific question

### After Recording
1. **Review transcript** - Check for accuracy
2. **Note your scores** - Understand where you're strong
3. **Re-record if needed** - You can record multiple times
4. **Check feedback** - Use the metrics to improve

## Troubleshooting

### "No microphone found" Error
**Solution**: 
- Ensure microphone is connected
- Check System Settings → Sound
- Refresh the browser page
- Try a different browser

### "Microphone access denied" Error
**Solution**:
1. Click the 🔒 icon in address bar
2. Find "Microphone" setting
3. Change from "Block" to "Allow"
4. Refresh the page
5. Try recording again

### Recording sounds weird/robotic
**Solution**:
- Close other applications using microphone
- Reduce background noise
- Adjust microphone position
- Try a different microphone
- Re-record with clearer speech

### Server returns error (500)
**Solution**:
- Restart backend: `python app.py`
- Check internet connection
- Try a shorter recording (1-2 minutes max)
- Contact support if issue persists

### Transcript is empty or gibberish
**Solution**:
- Speak more clearly
- Reduce background noise
- Record longer response (minimum 5-10 words)
- Check system microphone input levels

## Advanced: Installing Speech Models

The system uses mock transcription by default. To use real AI speech recognition:

```bash
cd backend
pip install transformers torch librosa
python app.py
```

Real transcription requires:
- ~2GB download (first time only)
- ~2-3 second load time (cached after)
- More accurate transcription
- Higher CPU usage during processing

## API Reference (for developers)

### Record Voice Response
```bash
POST /api/candidates/{candidate_id}/voice-interview
Content-Type: multipart/form-data

Fields:
- audio: [audio file]
- question_id: [integer]

Response:
{
  "success": true,
  "communication_score": 49,
  "transcript": "...",
  "metrics": {
    "clarity": 76,
    "confidence": 40,
    "relevance": 45,
    "speaking_pace": 39
  }
}
```

### Get Voice Profile
```bash
GET /api/candidates/{candidate_id}/voice-interviews

Response:
{
  "voice_interviews": [...],
  "voice_profile": {
    "communication_score": 49,
    "clarity": 76,
    "confidence": 40,
    "relevance": 45,
    "speaking_pace": 39
  }
}
```

## Support

For issues or questions:
1. Check VOICE_INTERVIEW_FEATURE.md for detailed documentation
2. Review browser console for error messages
3. Check backend logs: `/tmp/backend.log`
4. Ensure both services are running (backend + frontend)

## Summary

✅ **Feature Ready!**

- Record voice responses to interview questions
- Get instant communication scores
- See communication metrics breakdown
- Integration with candidate profiles
- Beautiful glowing UI with animations
- Comprehensive error handling

**Start using it now** - Open http://localhost:5173 and click the glowing Voice Interview tab! 🎤
