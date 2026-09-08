import React, { useState, useEffect, useRef } from 'react';
import Button from './Button';

interface VoiceToTextProps {
    onTranscription: (text: string) => void;
    placeholder?: string;
    className?: string;
    disabled?: boolean;
}

declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

const VoiceToText: React.FC<VoiceToTextProps> = ({
    onTranscription,
    placeholder = "Click microphone to start recording...",
    className = "",
    disabled = false
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        // Check for browser support
        if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
            setError('Speech recognition is not supported in this browser');
            return;
        }

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();

        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onstart = () => {
            setError(null);
        };

        recognitionRef.current.onresult = (event: any) => {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptSegment = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    onTranscription(transcriptSegment);
                }
            }
        };

        recognitionRef.current.onerror = (event: any) => {
            setError(`Speech recognition error: ${event.error}`);
            setIsRecording(false);
        };

        recognitionRef.current.onend = () => {
            setIsRecording(false);
        };

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [onTranscription]);

    const startRecording = () => {
        if (!recognitionRef.current || isRecording || disabled) return;

        setError(null);
        setIsRecording(true);

        try {
            recognitionRef.current.start();
        } catch (err) {
            setError('Failed to start recording');
            setIsRecording(false);
        }
    };

    const stopRecording = () => {
        if (!recognitionRef.current || !isRecording) return;

        recognitionRef.current.stop();
    };

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    const handleClick = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    return (
        <div className={`inline-flex items-center justify-center cursor-pointer ${className}`} onClick={handleClick}>
            {isRecording ? (
                // Stop icon
                <svg
                    className="w-4 h-4 text-red-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 9v6m4-6v6"
                    />
                </svg>
            ) : (
                // Microphone icon
                <svg
                    className="w-4 h-4 text-gray-500 hover:text-gray-700"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                </svg>
            )}
        </div>
    );
};

export default VoiceToText;