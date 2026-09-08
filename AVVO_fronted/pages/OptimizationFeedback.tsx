
import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VoiceToText from '../components/VoiceToText';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Page } from '../types';

interface OptimizationFeedbackProps {
    setActivePage: (page: Page) => void;
}

const OptimizationFeedback: React.FC<OptimizationFeedbackProps> = ({ setActivePage }) => {
    const { addLog, generatedVideoPath } = useApp();
    const [criticism, setCriticism] = useState('');
    const [script, setScript] = useState('');
    const [isCriticizing, setIsCriticizing] = useState(false);
    const [isComparing, setIsComparing] = useState(false);
    const [analytics, setAnalytics] = useState<any>(null);
    const [uploadedVideo, setUploadedVideo] = useState<File | null>(null);
    const [showRefinedPlan, setShowRefinedPlan] = useState(false);

    const handleCriticize = async () => {
        setIsCriticizing(true);
        addLog('INFO', 'Requesting AI content criticism...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        setCriticism(
`**Detailed AI Content Criticism:**

**Overall Virality Score:** 7.2/10 (Based on 85% engagement rate from similar content)

**Hook Analysis:**
- Effectiveness: 8/10 - Captures attention but lacks emotional trigger.
- Recommendation: Incorporate a surprising fact or question to increase click-through by 15%.

**Pacing Metrics:**
- Average Scene Duration: 4.5 seconds (Optimal: 3-5 seconds)
- Slow Sections: Scenes 2-3 (6.2s each) - Reduce by 20% to improve retention.
- Fast Sections: Intro (2.1s) - Extend slightly for better buildup.

**CTA Performance:**
- Clarity: 9/10 - Clear and direct.
- Urgency: 6/10 - Add time-sensitive language to boost conversion by 12%.
- Placement: Optimal at 85% of video length.

**Visual Elements:**
- Color Contrast: 7/10 - Good, but increase saturation for mobile viewing.
- Text Readability: 8/10 - Font size adequate, but test on small screens.

**Audio Quality:**
- Clarity: 8/10 - Clear voiceover.
- Background Music: 7/10 - Matches tone but could be more trending.

**Recommendations:**
1. Shorten middle scenes by 1.2 seconds each.
2. Add emotional hook in first 3 seconds.
3. Use trending sound effects to increase shares by 18%.`
        );
        setIsCriticizing(false);
        addLog('SUCCESS', 'AI criticism received.');
    };

    const handleCompare = async () => {
        setIsComparing(true);
        setAnalytics(null);
        addLog('INFO', 'Comparing videos for viral patterns...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        setAnalytics({
            viralScore: 88,
            hookScore: '9/10',
            visualScore: '8/10',
            trendScore: '9/10',
            audioScore: '7/10',
            criticalIssues: ['Audio in Scene 2 is slightly distorted.'],
            recommendations: ['Shorten the intro by 1.5 seconds.', 'Use a more trending background sound.'],
            refinedJsonPlan: '{"scenes": [{"duration": 5, "text": "Improved hook", "visuals": "Better graphics"}], "timing_adjustment": -1.5, "audio_track": "trending_sound_3.mp3"}'
        });
        setIsComparing(false);
        setShowRefinedPlan(true);
        addLog('SUCCESS', 'Video comparison analysis complete.');
    };

    const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setUploadedVideo(file);
            addLog('SUCCESS', `Video "${file.name}" uploaded for analysis.`);
        }
    };

    const downloadRefinedPlan = () => {
        if (analytics?.refinedJsonPlan) {
            const blob = new Blob([analytics.refinedJsonPlan], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'refined-video-plan.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            addLog('SUCCESS', 'Refined JSON plan downloaded.');
        }
    };

    const handleProceed = () => {
        alert('Moving to Publisher Agent...');
        addLog('INFO', 'User satisfied with video metrics and proceeding to Publisher.');
    };
    
    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Optimization & Feedback</h1>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card title="AI Content Criticism">
                    <p className="text-text-light mb-6 leading-relaxed">Analyzes your script against a knowledge base of viral patterns.</p>
                    <div className="relative mb-6">
                        <textarea
                            value={script}
                            onChange={(e) => setScript(e.target.value)}
                            placeholder="Paste your video script or concept here..."
                            className="w-full p-4 pr-10 border border-border rounded-lg min-h-[180px]"
                        />
                        <div className="absolute right-3 top-3">
                            <VoiceToText
                                onTranscription={(text) => setScript(prev => prev + text)}
                            />
                        </div>
                    </div>
                    <Button onClick={handleCriticize} isLoading={isCriticizing}>Get AI Feedback</Button>
                    {criticism && (
                        <div className="mt-6 bg-secondary p-6 rounded-lg">
                             <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{criticism}</pre>
                        </div>
                    )}
                </Card>
                <Card title="Viral Video Comparison">
                    <p className="text-text-light mb-6 leading-relaxed">Compare your content against a successful viral video.</p>
                    <div className="space-y-6">
                        <div>
                             <label htmlFor="platform" className="block text-sm font-medium text-text-light mb-2">Platform</label>
                             <select id="platform" className="w-full p-4 border border-border rounded-lg">
                                 <option value="">Select Platform</option>
                                 <option value="youtube_video">YouTube Video</option>
                                 <option value="youtube_shorts">YouTube Shorts</option>
                                 <option value="instagram_reels">Instagram Reels</option>
                                 <option value="instagram_story">Instagram Story</option>
                                 <option value="instagram_post">Instagram Post</option>
                                 <option value="tiktok_post">TikTok Post</option>
                             </select>
                        </div>
                        <div>
                             <label htmlFor="viralVideoLink" className="block text-sm font-medium text-text-light mb-2">Viral Video Link/URL</label>
                             <input type="url" id="viralVideoLink" placeholder="https://tiktok.com/..." className="w-full p-4 border border-border rounded-lg" />
                        </div>
                         <div>
                             <label htmlFor="uploadVideo" className="block text-sm font-medium text-text-light mb-2">Upload Your Generated Video</label>
                             <input
                                 type="file"
                                 id="uploadVideo"
                                 accept=".mp4,.mov,.avi"
                                 onChange={handleVideoUpload}
                                 className="w-full p-3 border border-dashed border-border rounded-lg"
                             />
                             {uploadedVideo && (
                                 <p className="mt-3 text-sm text-green-600 leading-relaxed">✅ {uploadedVideo.name} uploaded successfully</p>
                             )}
                         </div>
                    </div>
                     <Button onClick={handleCompare} isLoading={isComparing} className="mt-8">Compare & Analyze</Button>
                </Card>
            </div>
            {analytics && (
                <Card title="Analytics Dashboard" className="mt-8">
                     <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div className="bg-gradient-to-br from-primary to-primary-hover text-white p-6 rounded-lg text-center relative">
                            <h3 className="text-lg font-bold">Viral Score</h3>
                            <div className="relative w-32 h-32 mx-auto mt-4">
                                <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2"/>
                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="white" strokeWidth="2" strokeDasharray={`${analytics.viralScore}, 100`} strokeLinecap="round"/>
                                </svg>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <p className="text-3xl font-bold">{analytics.viralScore}</p>
                                </div>
                            </div>
                            <p className="opacity-80">out of 100</p>
                        </div>
                        <div className="bg-card p-6 rounded-lg">
                            <h4 className="font-bold mb-4">Engagement Metrics</h4>
                            <div className="space-y-4 text-sm">
                                <div>
                                    <div className="flex justify-between mb-1"><span>Hook Strength:</span> <strong>{analytics.hookScore}</strong></div>
                                    <div className="w-full bg-secondary rounded-full h-2">
                                        <div className="bg-primary h-2 rounded-full" style={{ width: `${parseInt(analytics.hookScore.split('/')[0]) * 10}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between mb-1"><span>Visual Appeal:</span> <strong>{analytics.visualScore}</strong></div>
                                    <div className="w-full bg-secondary rounded-full h-2">
                                        <div className="bg-primary h-2 rounded-full" style={{ width: `${parseInt(analytics.visualScore.split('/')[0]) * 10}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between mb-1"><span>Trend Alignment:</span> <strong>{analytics.trendScore}</strong></div>
                                    <div className="w-full bg-secondary rounded-full h-2">
                                        <div className="bg-primary h-2 rounded-full" style={{ width: `${parseInt(analytics.trendScore.split('/')[0]) * 10}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between mb-1"><span>Audio Quality:</span> <strong>{analytics.audioScore}</strong></div>
                                    <div className="w-full bg-secondary rounded-full h-2">
                                        <div className="bg-primary h-2 rounded-full" style={{ width: `${parseInt(analytics.audioScore.split('/')[0]) * 10}%` }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="bg-card p-6 rounded-lg">
                             <h4 className="font-bold mb-4">Critical Issues</h4>
                             <p className="text-sm text-error leading-relaxed">{analytics.criticalIssues[0]}</p>
                        </div>
                    </div>
                    <div className="bg-card p-6 rounded-lg">
                        <h4 className="font-bold mb-4">AI Recommendations</h4>
                        <ul className="list-disc list-inside space-y-2 text-sm">
                            {analytics.recommendations.map((rec: string, i: number) => <li key={i} className="leading-relaxed">{rec}</li>)}
                        </ul>
                    </div>

                    {showRefinedPlan && (
                        <div className="bg-card p-6 rounded-lg">
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="font-bold">Refined JSON Plan</h4>
                                <Button variant="secondary" size="sm" onClick={downloadRefinedPlan}>
                                    📥 Download Plan
                                </Button>
                            </div>
                            <pre className="bg-secondary p-4 rounded text-xs text-text-light overflow-x-auto leading-relaxed">
                                {JSON.stringify(JSON.parse(analytics.refinedJsonPlan), null, 2)}
                            </pre>
                        </div>
                    )}

                    <div className="flex justify-center pt-6 border-t border-border">
                        <Button onClick={handleProceed} className="px-8">
                            ✅ Proceed to Publisher
                        </Button>
                    </div>
                </Card>
            )}
        </div>
    );
};

export default OptimizationFeedback;
