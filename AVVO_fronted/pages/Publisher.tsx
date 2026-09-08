
import React, { useState, useEffect } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VoiceToText from '../components/VoiceToText';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Page } from '../types';

const Publisher: React.FC = () => {
    const { addLog, generatedVideoPath } = useApp();
    const { token } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [attachedVideos, setAttachedVideos] = useState<File[]>([]);
    const [jsonPlan, setJsonPlan] = useState('');
    const [caption, setCaption] = useState('');
    const [showAdditionalSettings, setShowAdditionalSettings] = useState(false);
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);


    const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);
        if (attachedVideos.length + files.length > 5) {
            alert('Maximum 5 videos allowed per task.');
            return;
        }
        setAttachedVideos(prev => [...prev, ...files]);
        addLog('SUCCESS', `${files.length} video(s) attached for publishing.`);
    };

    const removeVideo = (index: number) => {
        setAttachedVideos(prev => prev.filter((_, i) => i !== index));
        addLog('INFO', 'Video removed from publishing queue.');
    };

    const revisePlan = () => {
        window.open('https://multi-agent-1070255625225.us-central1.run.app', '_blank');
        addLog('INFO', 'Opened AI Assistant for publishing plan revision.');
    };

    const handlePlatformChange = (platform: string, checked: boolean) => {
        setSelectedPlatforms(prev =>
            checked ? [...prev, platform] : prev.filter(p => p !== platform)
        );
    };

    const handlePublish = async () => {
        if (selectedPlatforms.length === 0) {
            alert('Please select at least one platform.');
            return;
        }

        const videoPaths = [];
        if (generatedVideoPath) {
            videoPaths.push(generatedVideoPath);
        }
        for (const file of attachedVideos) {
            const formData = new FormData();
            formData.append('file', file);
            const uploadResponse = await fetch('/video-uploader/api/videos/upload', {
                method: 'POST',
                body: formData,
            });
            const uploadData = await uploadResponse.json();
            videoPaths.push(uploadData.file_path);
        }
        if (videoPaths.length === 0) {
            alert('Please generate or upload a video.');
            return;
        }

        setIsLoading(true);
        setStatus('Publishing...');
        addLog('INFO', 'Publishing process started.');

        // Build JSON payload for Zapier
        let payload;
        if (jsonPlan && jsonPlan.trim()) {
            try {
                payload = JSON.parse(jsonPlan);
                // Validate basic structure
                if (!payload.video || !payload.video.platforms) {
                    throw new Error('Invalid JSON plan structure');
                }
            } catch (e) {
                alert('Invalid JSON plan. Please check the format.');
                setIsLoading(false);
                return;
            }
        } else {
            // Generate JSON from manual inputs
            const postingTimeInput = document.getElementById('postingTime') as HTMLInputElement;
            const schedule = postingTimeInput.value ? new Date(postingTimeInput.value).toISOString() : null;

            // Extract hashtags from caption
            const hashtags = caption.match(/#\w+/g)?.map(tag => tag.substring(1)) || [];

            payload = {
                video: {
                    url: '', // Will be set after upload in backend
                    title: caption || 'Published Video',
                    description: caption || 'Check out this video!',
                    hashtags: hashtags,
                    duration: 0, // Optional, can be set later
                    platforms: {}
                },
                global_settings: {
                    default_schedule_offset: {
                        tiktok_offset_minutes: 0,
                        instagram_offset_minutes: 5,
                        youtube_offset_minutes: 10
                    }
                }
            };

            // Add platforms
            selectedPlatforms.forEach(platform => {
                let platformKey = '';
                let contentType = '';
                let additionalSettings = {};

                if (platform === 'YouTube Video' || platform === 'YouTube Shorts') {
                    platformKey = 'youtube';
                    contentType = 'video';
                    additionalSettings = {
                        yt_category: '24',
                        yt_visibility: 'public'
                    };
                } else if (platform === 'Instagram Reels') {
                    platformKey = 'instagram';
                    contentType = 'reels';
                    additionalSettings = {
                        ig_share_to_feed: true
                    };
                } else if (platform === 'Instagram Story') {
                    platformKey = 'instagram';
                    contentType = 'story';
                    additionalSettings = {
                        ig_share_to_feed: false
                    };
                } else if (platform === 'Instagram Post') {
                    platformKey = 'instagram';
                    contentType = 'post';
                    additionalSettings = {
                        ig_share_to_feed: true
                    };
                } else if (platform === 'TikTok Post') {
                    platformKey = 'tiktok';
                    contentType = 'video_post';
                }

                if (platformKey) {
                    payload.video.platforms[platformKey] = {
                        enabled: true,
                        content_type: contentType,
                        ...additionalSettings
                    };
                }
            });
        }

        try {
            const response = await fetch('/api/publisher/publish', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    videos: videoPaths,
                    platforms: selectedPlatforms.map(p => {
                        if (p.includes('YouTube')) return 'youtube';
                        if (p.includes('Instagram')) return 'instagram';
                        if (p.includes('TikTok')) return 'tiktok';
                        return p.toLowerCase().replace(' ', '');
                    }),
                    caption: caption,
                    jsonPayload: payload,
                }),
            });
            if (!response.ok) throw new Error('Failed to publish');
            const data = await response.json();
            setStatus('Publishing queued successfully!');
            addLog('SUCCESS', 'Publishing queued.');
        } catch (error) {
            setStatus('Failed to publish.');
            addLog('ERROR', 'Publishing failed.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <BackButton />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Publisher Agent</h1>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                    <Card title="Select Platforms" className="mb-8">
                        <div className="flex flex-wrap gap-6">
                            {[
                                'YouTube Video',
                                'YouTube Shorts',
                                'Instagram Reels',
                                'Instagram Story',
                                'Instagram Post',
                                'TikTok Post'
                            ].map(platform => (
                                <label key={platform} htmlFor={`platform-${platform.toLowerCase().replace(' ', '-')}`} className={`flex items-center gap-2 p-4 border rounded-lg cursor-pointer transition-colors ${selectedPlatforms.includes(platform) ? 'border-primary bg-primary/10' : 'border-border hover:bg-secondary'}`}>
                                    <input
                                        type="checkbox"
                                        id={`platform-${platform.toLowerCase().replace(' ', '-')}`}
                                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                        checked={selectedPlatforms.includes(platform)}
                                        onChange={(e) => handlePlatformChange(platform, e.target.checked)}
                                    />
                                    <span className="font-medium">{platform}</span>
                                </label>
                            ))}
                        </div>
                    </Card>
                    <Card title="Upload Videos">
                        <p className="text-text-light mb-6 leading-relaxed">Upload up to 5 videos for publishing (supports multiple videos per task).</p>
                        <input
                            type="file"
                            multiple
                            accept=".mp4,.mov,.avi"
                            onChange={handleVideoUpload}
                            className="w-full p-3 border border-dashed border-border rounded-lg"
                        />
                        {attachedVideos.length > 0 && (
                            <div className="mt-6 space-y-3">
                                {attachedVideos.map((video, index) => (
                                    <div key={index} className="flex justify-between items-center p-4 bg-secondary rounded-lg">
                                        <div>
                                            <span className="font-medium text-sm">{video.name}</span>
                                            <span className="text-xs text-text-light ml-2">({(video.size / 1024 / 1024).toFixed(2)} MB)</span>
                                        </div>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            onClick={() => removeVideo(index)}
                                        >
                                            Remove
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                </div>
                <Card title="Scheduling & Details">
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="postingTime" className="block text-sm font-medium text-text-light mb-2">Posting Time (Optional)</label>
                            <input type="datetime-local" id="postingTime" className="w-full p-4 border border-border rounded-lg" />
                        </div>
                        <div>
                            <label htmlFor="caption" className="block text-sm font-medium text-text-light mb-2">Caption & Hashtags</label>
                            <div className="relative">
                                <textarea
                                    id="caption"
                                    value={caption}
                                    onChange={(e) => setCaption(e.target.value)}
                                    placeholder="My new viral video! #AI #Tech #Viral"
                                    className="w-full p-4 pr-10 border border-border rounded-lg min-h-[150px]"
                                />
                                <div className="absolute right-3 top-3">
                                    <VoiceToText
                                        onTranscription={(text) => setCaption(prev => prev + text)}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="pt-6 border-t border-border">
                            <Button
                                variant="secondary"
                                onClick={() => setShowAdditionalSettings(!showAdditionalSettings)}
                                className="w-full mb-6"
                            >
                                {showAdditionalSettings ? 'Hide' : 'Show'} Additional Settings
                            </Button>

                            {showAdditionalSettings && (
                                <div className="space-y-6">
                                    <div>
                                        <label htmlFor="jsonPlan" className="block text-sm font-medium text-text-light mb-2">Publishing JSON Plan</label>
                                        <textarea
                                            id="jsonPlan"
                                            value={jsonPlan}
                                            onChange={e => setJsonPlan(e.target.value)}
                                            placeholder={`{
 "video": {
   "url": "https://example.com/video.mp4",
   "title": "Your Video Title",
   "description": "Video description",
   "hashtags": ["hashtag1", "hashtag2"],
   "platforms": {
     "youtube": {
       "enabled": true,
       "content_type": "video",
       "yt_category": "24",
       "yt_visibility": "public"
     },
     "instagram": {
       "enabled": true,
       "ig_post_type": "reels",
       "ig_share_to_feed": true
     },
     "tiktok": {
       "enabled": true,
       "content_type": "video_post"
     }
   }
 }
}`}
                                            className="w-full p-4 border border-border rounded-lg min-h-[200px] font-mono text-sm"
                                        />
                                        {jsonPlan && (() => {
                                            try {
                                                JSON.parse(jsonPlan);
                                                return <p className="text-green-600 text-sm mt-1">Valid JSON</p>;
                                            } catch {
                                                return <p className="text-red-600 text-sm mt-1">Invalid JSON format</p>;
                                            }
                                        })()}
                                    </div>
                                    <Button variant="secondary" onClick={revisePlan} className="w-full flex items-center gap-2">
                                        🤖 Revise Plan (AI Assistant)
                                    </Button>
                                </div>
                            )}
                        </div>

                        <Button onClick={handlePublish} isLoading={isLoading} className="w-full">
                            Publish Video{attachedVideos.length > 1 ? 's' : ''}
                        </Button>
                        {status && (
                            <div className="mt-6 p-4 bg-secondary rounded-lg">
                                <p className={`text-center font-semibold leading-relaxed ${status.includes('completed') ? 'text-green-600' : status.includes('failed') || status.includes('Error') ? 'text-red-600' : 'text-blue-600'}`}>
                                    {status}
                                </p>
                            </div>
                        )}
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default Publisher;
