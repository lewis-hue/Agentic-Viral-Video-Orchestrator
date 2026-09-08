import React, { useState, useRef, useEffect } from 'react';
import Button from './Button';

interface VideoPlayerProps {
    src: string;
    title?: string;
    onDownload?: (videoId?: string) => void;
    className?: string;
    videoId?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
    src,
    title = "Video Preview",
    onDownload,
    className = "",
    videoId
}) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [showControls, setShowControls] = useState(true);
    const [trimStart, setTrimStart] = useState(0);
    const [trimEnd, setTrimEnd] = useState(0);
    const [showTrimControls, setShowTrimControls] = useState(false);
    const [filter, setFilter] = useState('none');
    const [hasError, setHasError] = useState(false);
    const [showSubtitles, setShowSubtitles] = useState(false);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const updateTime = () => setCurrentTime(video.currentTime);
        const updateDuration = () => setDuration(video.duration);
        const handleError = () => setHasError(true);
        const handleLoad = () => setHasError(false);

        video.addEventListener('timeupdate', updateTime);
        video.addEventListener('loadedmetadata', updateDuration);
        video.addEventListener('play', () => setIsPlaying(true));
        video.addEventListener('pause', () => setIsPlaying(false));
        video.addEventListener('error', handleError);
        video.addEventListener('loadstart', handleLoad);

        return () => {
            video.removeEventListener('timeupdate', updateTime);
            video.removeEventListener('loadedmetadata', updateDuration);
            video.removeEventListener('play', () => setIsPlaying(true));
            video.removeEventListener('pause', () => setIsPlaying(false));
            video.removeEventListener('error', handleError);
            video.removeEventListener('loadstart', handleLoad);
        };
    }, []);

    const togglePlay = () => {
        const video = videoRef.current;
        if (!video) return;

        if (isPlaying) {
            video.pause();
        } else {
            video.play();
        }
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        const video = videoRef.current;
        if (!video) return;

        const time = (parseFloat(e.target.value) / 100) * duration;
        video.currentTime = time;
    };

    const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const video = videoRef.current;
        if (!video) return;

        const newVolume = parseFloat(e.target.value);
        setVolume(newVolume);
        video.volume = newVolume;
    };

    const handleSpeedChange = (speed: number) => {
        const video = videoRef.current;
        if (!video) return;

        setPlaybackSpeed(speed);
        video.playbackRate = speed;
    };

    const skip = (seconds: number) => {
        const video = videoRef.current;
        if (!video) return;

        video.currentTime += seconds;
    };

    const toggleFullscreen = () => {
        const video = videoRef.current;
        if (!video) return;

        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            video.requestFullscreen();
        }
    };

    const handleTrimStartChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setTrimStart(parseFloat(e.target.value));
    };

    const handleTrimEndChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setTrimEnd(parseFloat(e.target.value));
    };

    const applyTrim = async () => {
        try {
            // Send trim request to backend
            const response = await fetch('http://localhost:8000/api/video/trim', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: JSON.stringify({
                    video_path: src,
                    start_time: trimStart,
                    end_time: trimEnd,
                    video_id: videoId
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to trim video');
            }

            const result = await response.json();
            alert(`Video trimmed successfully! New video: ${result.trimmed_video_path}`);
            console.log('Trim result:', result);
        } catch (error) {
            console.error('Trim error:', error);
            alert('Failed to trim video. Please try again.');
        }
    };

    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    if (hasError) {
        return (
            <div className={`bg-secondary rounded-lg overflow-hidden ${className} flex items-center justify-center h-64`}>
                <div className="text-center">
                    <p className="text-red-500 mb-2">Video failed to load</p>
                    <p className="text-sm text-gray-400">The video source may be invalid or unavailable.</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-secondary rounded-lg overflow-hidden ${className}`}>
            <div className="relative">
                <video
                    ref={videoRef}
                    src={src}
                    className="w-full h-auto"
                    style={{ filter: filter }}
                    onClick={() => setShowControls(!showControls)}
                >
                    {showSubtitles && (
                        <track
                            kind="subtitles"
                            srcLang="en"
                            label="English"
                            default
                        />
                    )}
                </video>

                {showControls && (
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                        {/* Progress Bar */}
                        <div className="mb-3">
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={duration ? (currentTime / duration) * 100 : 0}
                                onChange={handleSeek}
                                className="w-full h-1 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
                            />
                        </div>

                        {/* Main Controls */}
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Button variant="secondary" size="sm" onClick={togglePlay}>
                                    {isPlaying ? '⏸️' : '▶️'}
                                </Button>
                                <Button variant="secondary" size="sm" onClick={() => skip(-10)}>
                                    ⏪
                                </Button>
                                <Button variant="secondary" size="sm" onClick={() => skip(10)}>
                                    ⏩
                                </Button>
                                <span className="text-white text-sm">
                                    {formatTime(currentTime)} / {formatTime(duration)}
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Volume Control */}
                                <div className="flex items-center gap-1">
                                    <span className="text-white text-sm">🔊</span>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={volume}
                                        onChange={handleVolumeChange}
                                        className="w-16 h-1 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                </div>

                                {/* Speed Control */}
                                <select
                                    value={playbackSpeed}
                                    onChange={(e) => handleSpeedChange(Number(e.target.value))}
                                    className="bg-black/50 text-white text-sm px-2 py-1 rounded"
                                >
                                    <option value={0.5}>0.5x</option>
                                    <option value={1}>1x</option>
                                    <option value={1.5}>1.5x</option>
                                    <option value={2}>2x</option>
                                </select>

                                {/* Fullscreen */}
                                <Button variant="secondary" size="sm" onClick={toggleFullscreen}>
                                    ⛶
                                </Button>

                                {/* Download */}
                                {onDownload && (
                                    <Button variant="primary" size="sm" onClick={() => onDownload(videoId)}>
                                        📥 Download
                                    </Button>
                                )}

                                {/* Edit Controls */}
                                <Button variant="secondary" size="sm" onClick={() => setShowTrimControls(!showTrimControls)}>
                                    ✂️
                                </Button>

                                {/* CC Button */}
                                <Button variant="secondary" size="sm" onClick={() => setShowSubtitles(!showSubtitles)}>
                                    {showSubtitles ? 'CC On' : 'CC Off'}
                                </Button>
                            </div>
                        </div>

                        {/* Trim Controls */}
                        {showTrimControls && (
                            <div className="mt-4 p-4 bg-black/50 rounded-lg">
                                <h3 className="text-white text-sm mb-2">Trim Video</h3>
                                <div className="flex items-center gap-4">
                                    <div className="flex flex-col">
                                        <label className="text-white text-xs">Start Time</label>
                                        <input
                                            type="range"
                                            min="0"
                                            max={duration}
                                            value={trimStart}
                                            onChange={handleTrimStartChange}
                                            className="w-24 h-1 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
                                        />
                                        <span className="text-white text-xs">{formatTime(trimStart)}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <label className="text-white text-xs">End Time</label>
                                        <input
                                            type="range"
                                            min="0"
                                            max={duration}
                                            value={trimEnd}
                                            onChange={handleTrimEndChange}
                                            className="w-24 h-1 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
                                        />
                                        <span className="text-white text-xs">{formatTime(trimEnd)}</span>
                                    </div>
                                    <Button variant="primary" size="sm" onClick={applyTrim}>
                                        Apply Trim
                                    </Button>
                                </div>

                                {/* Filter Controls */}
                                <div className="mt-4">
                                    <h3 className="text-white text-sm mb-2">Filters</h3>
                                    <div className="flex gap-2">
                                        <Button variant="secondary" size="sm" onClick={() => setFilter('none')}>
                                            None
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={() => setFilter('grayscale(100%)')}>
                                            Grayscale
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={() => setFilter('sepia(100%)')}>
                                            Sepia
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={() => setFilter('brightness(1.2) contrast(1.1) saturate(1.2)')}>
                                            Sharpen
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default VideoPlayer;