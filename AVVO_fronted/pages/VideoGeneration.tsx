
import React, { useState, useEffect, useRef } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VideoPlayer from '../components/VideoPlayer';
import VoiceToText from '../components/VoiceToText';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Page } from '../types';
import { apiService } from '../services/apiService';

interface VideoGenerationProps {
    setActivePage: (page: Page) => void;
}

const VideoGeneration: React.FC<VideoGenerationProps> = ({ setActivePage }) => {
    const { addLog, generatedScript, setGeneratedVideoPath } = useApp();
    const { token } = useAuth();
    const [script, setScript] = useState('Create a viral video about the benefits of using AI in daily tasks.');
    const [jsonPlan, setJsonPlan] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [progressText, setProgressText] = useState('');
    const [videoUrl, setVideoUrl] = useState('');
    const [generationStatus, setGenerationStatus] = useState<'success' | 'failed' | null>(null);
    const [showVideoActions, setShowVideoActions] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [jobId, setJobId] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        if (generatedScript) {
            setScript(generatedScript);
        }
    }, [generatedScript]);

    const openAIAssistant = () => {
        window.open('https://multi-agent-1070255625225.us-central1.run.app', '_blank');
        addLog('INFO', 'Opened AI Assistant in new tab for JSON plan refinement.');
    };

    useEffect(() => {
        if (jobId) {
            const pollStatus = async () => {
                try {
                    const data = await apiService.getVideoGenerationStatus(token, jobId);
                    if (data.status === 'completed') {
                        setVideoUrl(data.video_path);
                        setGeneratedVideoPath(data.video_path);
                        setGenerationStatus('success');
                        setShowVideoActions(true);
                        addLog('SUCCESS', `Video Generation Agent created: ${data.video_path}`);
                        setIsLoading(false);
                        setProgress(100);
                        setProgressText('Video Generation Complete');
                        setJobId(null);
                    } else if (data.status === 'failed') {
                        addLog('ERROR', `Video generation failed: ${data.error || 'Unknown error'}`);
                        setGenerationStatus('failed');
                        setIsLoading(false);
                        setJobId(null);
                    } else {
                        setProgress(data.progress || 0);
                        setProgressText('Generating video...');
                        setTimeout(pollStatus, 2000);
                    }
                } catch (error) {
                    addLog('ERROR', 'Failed to check video generation status.');
                    setIsLoading(false);
                    setJobId(null);
                }
            };
            pollStatus();
        }
    }, [jobId, addLog, setGeneratedVideoPath, token]);

    const handleGenerate = async () => {
        if (!script.trim()) {
            alert('Please provide a script.');
            return;
        }
        addLog('INFO', 'AI-powered video generation process started.');
        setIsLoading(true);
        setProgress(0);
        setVideoUrl('');
        setGenerationStatus(null);
        setShowVideoActions(false);
        setProgressText('Starting video generation...');

        try {
            const data = await apiService.generateVideoFromScript(token, {
                script: script,
                json_plan: jsonPlan,
            });
            setJobId(data.job_id);
            setProgress(10);
            setProgressText('Job started, processing...');
        } catch (error) {
            addLog('ERROR', 'Video generation failed. Please check your script and try again.');
            setIsLoading(false);
        }
    };

    const handleProceed = () => {
        alert('Moving to Optimization & Feedback Agent...');
        addLog('INFO', 'User proceeded to Optimization & Feedback Agent.');
    };

    const handleRefine = () => {
        setScript('');
        setJsonPlan('');
        setVideoUrl('');
        setShowVideoActions(false);
        setGenerationStatus(null);
        addLog('INFO', 'User chose to refine the script and regenerate video.');
    };

    const handlePlaybackSpeed = (speed: number) => {
        if (videoRef.current) {
            videoRef.current.playbackRate = speed;
            setPlaybackSpeed(speed);
        }
    };

    const handleFastForward = () => {
        if (videoRef.current) {
            videoRef.current.currentTime += 10;
        }
    };

    const handleBackForward = () => {
        if (videoRef.current) {
            videoRef.current.currentTime -= 10;
        }
    };

    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Video Generation Agent</h1>
            <Card title="Produce Video from Script" className="mb-8">
                <div className="space-y-6">
                    <div>
                        <label htmlFor="videoGenScript" className="block text-sm font-medium text-text-light mb-2">Final Script / Prompt</label>
                        <div className="relative">
                            <textarea id="videoGenScript" value={script} onChange={e => setScript(e.target.value)} className="w-full p-4 pr-10 border border-border rounded-lg min-h-[180px]"></textarea>
                            <div className="absolute right-3 top-3">
                                <VoiceToText
                                    onTranscription={(text) => setScript(prev => prev + text)}
                                />
                            </div>
                        </div>
                    </div>
                    <div>
                        <label htmlFor="jsonPlan" className="block text-sm font-medium text-text-light mb-2">JSON Plan (Optional)</label>
                        <div className="flex gap-2 mb-2">
                            <Button variant="secondary" size="sm" onClick={() => setJsonPlan(`{
 "scenes": [
   {
     "duration": 5,
     "text": "Your script text here",
     "visuals": "Describe visuals here"
   }
 ]
}`)}>Use Template</Button>
                        </div>
                        <textarea id="jsonPlan" value={jsonPlan} onChange={e => setJsonPlan(e.target.value)} placeholder='{"scenes": [{"duration": 5, "text": "...", "visuals": "..."}]}' className="w-full p-4 border border-border rounded-lg min-h-[180px] font-mono text-sm"></textarea>
                    </div>
                </div>
                <div className="flex gap-6 mt-8">
                    <Button onClick={handleGenerate} isLoading={isLoading} className="flex-1">
                        Generate Video
                    </Button>
                    <Button variant="secondary" onClick={openAIAssistant} className="flex items-center gap-2">
                        🤖 AI ASSISTANT
                    </Button>
                </div>
            </Card>

            {(isLoading || progress === 100) && (
                <Card title={isLoading ? "Generating Video..." : "Video Generation Complete"} className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-full bg-secondary rounded-full h-2.5">
                            <div className="bg-primary h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                        <span className="font-bold text-primary">{Math.round(progress)}%</span>
                    </div>
                    <p className="text-sm text-text-light leading-relaxed">{progressText}</p>
                </Card>
            )}

            {generationStatus === 'success' && videoUrl && (
                <Card title="Generated Video Preview">
                    <VideoPlayer
                        src={videoUrl}
                        title="Generated Video"
                        videoId={jobId || undefined}
                        onDownload={(videoId) => {
                            window.open(videoUrl, '_blank');
                        }}
                    />
                    <div className="mt-6 flex gap-4">
                        <Button onClick={handleProceed} className="flex-1">✅ Proceed to Optimization</Button>
                        <Button variant="secondary" onClick={handleRefine} className="flex-1">🔄 Refine & Regenerate</Button>
                    </div>
                </Card>
            )}

            {generationStatus === 'failed' && (
                <Card title="Video Generation Failed">
                    <p className="text-error mb-6 leading-relaxed">The video generation process failed. Please check your script and try again.</p>
                    <div className="flex gap-4">
                        <Button onClick={handleRefine} className="flex-1">🔄 Try Again</Button>
                        <Button variant="secondary" onClick={openAIAssistant} className="flex-1">🤖 Get AI Help</Button>
                    </div>
                </Card>
            )}
        </div>
    );
};

export default VideoGeneration;
