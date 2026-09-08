const express = require('express');
const axios = require('axios');
const ffmpeg = require('fluent-ffmpeg');
const multer = require('multer');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const textToSpeech = require('@google-cloud/text-to-speech');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3001;

app.use(express.json());

const upload = multer({ dest: 'uploads/' });

// Ensure generated directory exists
if (!fs.existsSync('generated')) {
    fs.mkdirSync('generated');
}

// Initialize Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-pro' });

// Initialize Google TTS
const ttsClient = new textToSpeech.TextToSpeechClient();

async function generateVideoWithGemini(script) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error('GEMINI_API_KEY not set');

    // Use Gemini to generate a detailed video prompt
    const prompt = `Generate a detailed video generation prompt for the following script: "${script}". Include visual style, camera movements, and key scenes.`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const videoPrompt = response.text();

    // Simulate video generation using the prompt
    // In a real implementation, you would use a video synthesis API like Runway or Pika with the generated prompt
    const videoPath = `generated/video_${Date.now()}.mp4`;
    // Placeholder: create a dummy video file
    fs.writeFileSync(videoPath, `Generated video based on prompt: ${videoPrompt}`);
    return videoPath;
}

async function generateVoice(script) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error('GEMINI_API_KEY not set');

    // Use Google TTS
    const request = {
        input: { text: script },
        voice: { languageCode: 'en-US', ssmlGender: 'NEUTRAL' },
        audioConfig: { audioEncoding: 'MP3' },
    };

    const [response] = await ttsClient.synthesizeSpeech(request);
    const audioPath = `generated/audio_${Date.now()}.mp3`;
    fs.writeFileSync(audioPath, response.audioContent, 'binary');
    return audioPath;
}

async function generateMusic() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error('GEMINI_API_KEY not set');

    // Use Gemini to generate a music description
    const prompt = 'Generate a description for upbeat viral music suitable for a short video.';
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const musicDescription = response.text();

    // Simulate music generation
    const musicPath = `generated/music_${Date.now()}.mp3`;
    fs.writeFileSync(musicPath, `Generated music based on: ${musicDescription}`);
    return musicPath;
}

async function mergeAssets(videoPath, audioPath, musicPath) {
    // Use FFmpeg to merge
    return new Promise((resolve, reject) => {
        const outputPath = `output_${Date.now()}.mp4`;
        ffmpeg()
            .input(videoPath)
            .input(audioPath)
            .input(musicPath)
            .complexFilter([
                '[0:v]scale=1080:1920[v0]',
                '[1:a]volume=1.0[a1]',
                '[2:a]volume=0.5[a2]',
                '[a1][a2]amix=inputs=2[a]'
            ])
            .map('[v0]')
            .map('[a]')
            .output(outputPath)
            .on('end', () => resolve(outputPath))
            .on('error', reject)
            .run();
    });
}

app.post('/generate', upload.single('script'), async (req, res) => {
    const script = req.body.script;
    try {
        const videoPath = await generateVideoWithGemini(script);
        const audioPath = await generateVoice(script);
        const musicPath = await generateMusic();
        const outputPath = await mergeAssets(videoPath, audioPath, musicPath);
        res.json({ video_path: outputPath });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Video Generation Agent listening at http://localhost:${port}`);
});