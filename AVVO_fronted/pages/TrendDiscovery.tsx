import React, { useState, useEffect, useRef } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Page, Trend } from '../types';

interface TrendDiscoveryProps {
    setActivePage: (page: Page) => void;
}

const TrendDiscovery: React.FC<TrendDiscoveryProps> = ({ setActivePage }) => {
    const { addLog, setCurrentTrends, setGeneratedScript } = useApp();
    const { token } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [progressText, setProgressText] = useState('');
    const [trends, setTrends] = useState<Trend[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [voiceText, setVoiceText] = useState('');
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [links, setLinks] = useState<string>('');
    const [jobId, setJobId] = useState<string | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    useEffect(() => {
        if (jobId) {
            const pollStatus = async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/agents/trend-discovery/status/${jobId}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });
                    const data = await response.json();
                    if (data.status === 'completed') {
                        setTrends(data.result);
                        setCurrentTrends(data.result);
                        addLog('SUCCESS', `Trend Discovery Agent found ${data.result.length} new trends.`);
                        setIsLoading(false);
                        setProgress(100);
                        setProgressText('Scan Complete');
                        setJobId(null);
                    } else {
                        setProgress(50);
                        setProgressText('Processing...');
                        setTimeout(pollStatus, 2000);
                    }
                } catch (error) {
                    addLog('ERROR', 'Failed to check status.');
                    setIsLoading(false);
                    setJobId(null);
                }
            };
            pollStatus();
        }
    }, [jobId, addLog, setCurrentTrends, token]);

    const startVoiceRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                // Here you would typically send to a speech-to-text API
                // For now, we'll simulate the transcription
                setVoiceText('Voice input: "I want to find trends about cooking and food hacks"');
                addLog('SUCCESS', 'Voice recording completed and transcribed.');
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            addLog('INFO', 'Voice recording started.');
        } catch (error) {
            addLog('ERROR', 'Failed to start voice recording.');
            console.error('Voice recording error:', error);
        }
    };

    const stopVoiceRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            addLog('INFO', 'Voice recording stopped.');
        }
    };

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);
        setAttachedFiles(prev => [...prev, ...files]);
        addLog('SUCCESS', `${files.length} file(s) attached for trend analysis.`);
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
        addLog('INFO', 'File removed from trend analysis.');
    };

    const handleDiscover = async () => {
        addLog('INFO', 'Starting AI-powered trend discovery process...');
        setIsLoading(true);
        setProgress(0);
        setTrends([]);
        setProgressText('Discovering trends...');
        try {
            const response = await fetch('http://localhost:8000/api/agents/trend-discovery', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    links: links.split(',').map(l => l.trim()).filter(l => l),
                    voiceInput: voiceText,
                    files: attachedFiles.map(f => f.name),
                }),
            });
            if (!response.ok) throw new Error('Failed to start trend discovery');
            const data = await response.json();
            setJobId(data.job_id);
            setProgress(10);
            setProgressText('Job started, processing...');
        } catch (error) {
            addLog('ERROR', 'Failed to start trend discovery.');
            setIsLoading(false);
        }
    };
    
    const useTrend = (trend: Trend) => {
        setGeneratedScript(JSON.stringify(trend));
        addLog('INFO', `Selected trend "${trend.theme}" for story ideation.`);
        alert(`Trend "${trend.theme}" has been set as the topic for the Story Ideation page.`);
    };

    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Trend Discovery Agent</h1>
            <Card title="Scan Social Platforms" className="mb-8">
                <p className="text-text-light mb-6 leading-relaxed">AI-powered trend discovery that scans TikTok, YouTube Shorts, X, and Instagram to identify viral themes, sounds, and formats.</p>
                <div className="space-y-6">
                    <div>
                        <label htmlFor="trendLinks" className="block text-sm font-medium text-text-light mb-2">Input Links/URLs (Optional)</label>
                        <input type="text" id="trendLinks" value={links} onChange={(e) => setLinks(e.target.value)} placeholder="https://tiktok.com/@user/video/123, https://youtube.com/shorts/456" className="w-full p-4 border border-border rounded-lg" />
                    </div>

                    <div>
                        <label htmlFor="voiceInput" className="block text-sm font-medium text-text-light mb-2">Voice Input (Optional)</label>
                        <div className="flex gap-4">
                            <Button
                                variant={isRecording ? "secondary" : "primary"}
                                onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                                className="flex items-center gap-2"
                                id="voiceInput"
                            >
                                {isRecording ? '⏹️ Stop Recording' : '🎤 Start Voice Input'}
                            </Button>
                        </div>
                        {voiceText && (
                            <div className="mt-4 p-4 bg-secondary rounded-lg">
                                <p className="text-sm text-text-light leading-relaxed">{voiceText}</p>
                            </div>
                        )}
                    </div>

                    <div>
                        <label htmlFor="attachFiles" className="block text-sm font-medium text-text-light mb-2">Attach Files (Optional)</label>
                        <input
                            type="file"
                            id="attachFiles"
                            multiple
                            accept=".txt,.pdf,.doc,.docx,.mp4,.mov"
                            onChange={handleFileUpload}
                            className="w-full p-3 border border-dashed border-border rounded-lg"
                        />
                        {attachedFiles.length > 0 && (
                            <div className="mt-4 space-y-3">
                                {attachedFiles.map((file, index) => (
                                    <div key={index} className="flex justify-between items-center p-3 bg-secondary rounded-lg">
                                        <span className="text-sm text-text-light">{file.name}</span>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            onClick={() => removeFile(index)}
                                        >
                                            Remove
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
                <Button onClick={handleDiscover} isLoading={isLoading} className="mt-8">
                    Discover Top 5 Trends
                </Button>
            </Card>

            {(isLoading || progress === 100) && (
                <Card title={isLoading ? "Discovering Trends..." : "Scan Complete"} className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-full bg-secondary rounded-full h-2.5">
                            <div className="bg-primary h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                        <span className="font-bold text-primary">{Math.round(progress)}%</span>
                    </div>
                    <p className="text-sm text-text-light leading-relaxed">{progressText}</p>
                </Card>
            )}

            {trends.length > 0 && (
                  <Card title="Current Viral Trends">
                     <ul className="space-y-4">
                         {trends.map((trend, index) => (
                             <li key={index} className="p-4 bg-secondary rounded-lg">
                                 <div className="flex justify-between items-start mb-2">
                                     <span className="font-medium leading-relaxed">{trend.theme}</span>
                                     <Button variant="secondary" onClick={() => useTrend(trend)} className="py-1 px-3 text-sm">Use Trend</Button>
                                 </div>
                                 <p className="text-sm text-text-light mb-2">{trend.description}</p>
                                 <p className="text-xs text-text-light mb-1">Key Elements: {trend.key_elements.join(', ')}</p>
                                 <p className="text-xs text-text-light mb-1">Virality Score: {trend.virality_score}</p>
                                 <p className="text-xs text-text-light mb-2">Reasoning: {trend.reasoning}</p>
                                 <div className="text-xs text-text-light">
                                     <p>Hook: {trend.additional_instructions.hook}</p>
                                     <p>Style: {trend.additional_instructions.style}</p>
                                     <p>Tone: {trend.additional_instructions.tone}</p>
                                 </div>
                             </li>
                         ))}
                     </ul>
                  </Card>
             )}
        </div>
    );
};

export default TrendDiscovery;