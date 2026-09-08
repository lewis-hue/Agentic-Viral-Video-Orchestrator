import React, { useState, useEffect, useRef, useCallback } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VoiceToText from '../components/VoiceToText';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Page } from '../types';

interface StoryIdeationProps {
    setActivePage: (page: Page) => void;
}

const StoryIdeation: React.FC<StoryIdeationProps> = ({ setActivePage }) => {
    const { addLog, generatedScript, setGeneratedScript } = useApp();
    const { token } = useAuth();
    const [topic, setTopic] = useState('');
    const [instructions, setInstructions] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [progressText, setProgressText] = useState('');
    const [scriptResult, setScriptResult] = useState('');
    const [showActions, setShowActions] = useState(false);
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [jobId, setJobId] = useState<string | null>(null);
    
    const handleTopicTranscription = useCallback((text: string) => {
        setTopic(prev => prev + text);
    }, []);

    const handleInstructionsTranscription = useCallback((text: string) => {
        setInstructions(prev => prev + text);
    }, []);

    useEffect(() => {
        if(generatedScript && !topic) {
              try {
                  const trend = JSON.parse(generatedScript);
                  setTopic(trend.theme);
                  setInstructions(`Hook: ${trend.additional_instructions.hook}, Style: ${trend.additional_instructions.style}, Tone: ${trend.additional_instructions.tone}`);
              } catch {
                  const trendMatch = generatedScript.match(/Based on the trend: "([^"]+)"/);
                  if (trendMatch && trendMatch[1]) {
                      setTopic(trendMatch[1]);
                  }
              }
         }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [generatedScript]);


    useEffect(() => {
        if (jobId) {
            const pollStatus = async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/agents/story-ideation/status/${jobId}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });
                    const data = await response.json();
                    if (data.status === 'completed') {
                        const script = data.result;
                        const formattedScript = `Title: ${script.title}

Hook: ${script.hook}

${script.scenes.map(scene => `Scene ${scene.scene_number}: ${scene.visual_description}
VO: "${scene.voiceover_script}"`).join('\n\n')}

CTA: ${script.cta}`;
                        setScriptResult(formattedScript);
                        setGeneratedScript(formattedScript);
                        setShowActions(true);
                        addLog('SUCCESS', 'Story Ideation Agent generated a new script.');
                        setIsLoading(false);
                        setProgress(100);
                        setProgressText('Script Generation Complete');
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
    }, [jobId, addLog, setGeneratedScript, token]);


    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);
        setAttachedFiles(prev => [...prev, ...files]);
        addLog('SUCCESS', `${files.length} file(s) attached for script generation.`);
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
        addLog('INFO', 'File removed from script generation.');
    };

    const handleGenerate = async () => {
        if (!topic.trim()) {
            alert('Please enter a topic or trend');
            return;
        }
        addLog('INFO', 'Starting AI-powered script generation process...');
        setIsLoading(true);
        setProgress(0);
        setScriptResult('');
        setShowActions(false);
        try {
            const response = await fetch('http://localhost:8000/api/agents/story-ideation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    topic: topic,
                    instructions: instructions,
                    voiceInput: '',
                    files: attachedFiles.map(f => f.name),
                }),
            });
            if (!response.ok) throw new Error('Failed to start script generation');
            const data = await response.json();
            setJobId(data.job_id);
            setProgress(10);
            setProgressText('Job started, processing...');
        } catch (error) {
            addLog('ERROR', 'Failed to start script generation.');
            setIsLoading(false);
        }
    };
    
    const acceptScript = () => {
        // Copy script to Video Generation page automatically
        setGeneratedScript(scriptResult);
        alert("Script accepted! It has been automatically copied to the Video Generation page.");
        addLog('SUCCESS', 'User accepted generated script and moved to video generation.');
    };

    const rejectScript = () => {
        setShowActions(false);
        setScriptResult('');
        setInstructions(''); // Clear instructions for revision
        addLog('INFO', 'User rejected script for revision.');
    };

    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Story Ideation Agent</h1>
            <Card title="Generate Script from Topic" className="mb-8">
                 <div className="space-y-6">
                     <div>
                         <label htmlFor="topic" className="block text-sm font-medium text-text-light mb-2">Topic or Trend</label>
                         <div className="relative">
                             <input type="text" id="topic" value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g., 'The AI chrome extension everyone is talking about'" className="w-full p-4 pr-10 border border-border rounded-lg" />
                             <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                 <VoiceToText
                                     onTranscription={handleTopicTranscription}
                                 />
                             </div>
                         </div>
                     </div>


                     <div>
                         <label htmlFor="promptVoiceInput" className="block text-sm font-medium text-text-light mb-2">Additional Instructions (Hook, Style, Tone)</label>
                         <div className="relative">
                             <textarea id="promptVoiceInput" value={instructions} onChange={e => setInstructions(e.target.value)} placeholder="e.g., 'Start with a strong hook, make the tone humorous...'" className="w-full p-4 pr-10 border border-border rounded-lg min-h-[120px]"></textarea>
                             <div className="absolute right-3 top-3">
                                 <VoiceToText
                                     onTranscription={handleInstructionsTranscription}
                                 />
                             </div>
                         </div>
                     </div>

                     <div>
                         <label htmlFor="attachFilesIdeation" className="block text-sm font-medium text-text-light mb-2">Attach Files (Optional)</label>
                         <input
                             type="file"
                             id="attachFilesIdeation"
                             multiple
                             accept=".txt,.pdf,.doc,.docx,.mp4,.mov,.jpg,.png"
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
                <Button onClick={handleGenerate} isLoading={isLoading} className="mt-8">
                    Generate Script
                </Button>
            </Card>
            
            {(isLoading || progress === 100) && (
                <Card title={isLoading ? "Generating Script..." : "Script Generation Complete"} className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-full bg-secondary rounded-full h-2.5">
                            <div className="bg-primary h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                        <span className="font-bold text-primary">{Math.round(progress)}%</span>
                    </div>
                    <p className="text-sm text-text-light leading-relaxed">{progressText}</p>
                </Card>
            )}

            {scriptResult && (
                <Card title="Generated Script">
                    <pre className="whitespace-pre-wrap font-mono bg-secondary p-6 rounded-lg text-sm text-text-light leading-relaxed">{scriptResult}</pre>
                    {showActions && (
                         <div className="mt-6 pt-6 border-t border-border space-x-6">
                            <Button onClick={acceptScript}>Accept & Continue</Button>
                            <Button variant="secondary" onClick={rejectScript}>Reject & Revise</Button>
                        </div>
                    )}
                </Card>
            )}
        </div>
    );
};

export default StoryIdeation;