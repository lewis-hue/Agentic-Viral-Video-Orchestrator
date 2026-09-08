import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
    const { user } = useAuth();

    return (
        <>
            <div className="relative z-10">
                <div style={{
                    background: 'linear-gradient(135deg, #E8E8E8, #F8E8F0, #F0E8F0)',
                    padding: '20px',
                    borderRadius: '12px'
                }}>
                    <div className="mb-8 backdrop-blur-sm bg-white/80 p-6 rounded-lg">
                        <h1 className="text-4xl font-bold mb-4 font-poppins text-text">Welcome back, {user?.username}!</h1>
                        <p className="text-lg text-text-light mb-6 font-roboto text-text">
                            Your AI-powered viral content creation platform is ready. Explore the tools below to discover trends, ideate stories, generate videos, and more.
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
                <Card title="Trend Discovery">
                    <p className="text-text-light mb-4">
                        Scan social platforms like TikTok, YouTube, and Instagram to identify viral trends, sounds, and formats using AI.
                    </p>
                    <Link to="/trend-discovery">
                        <Button variant="primary">
                            Discover Trends
                        </Button>
                    </Link>
                </Card>

                <Card title="Story Ideation">
                    <p className="text-text-light mb-4">
                        Generate creative story ideas and scripts based on discovered trends and user inputs.
                    </p>
                    <Link to="/story-ideation">
                        <Button variant="primary">
                            Ideate Stories
                        </Button>
                    </Link>
                </Card>

                <Card title="Video Generation">
                    <p className="text-text-light mb-4">
                        Create dynamic videos with AI orchestration, including shots, effects, and voiceovers.
                    </p>
                    <Link to="/video-generation">
                        <Button variant="primary">
                            Generate Videos
                        </Button>
                    </Link>
                </Card>

                <Card title="Optimization Feedback">
                    <p className="text-text-light mb-4">
                        Get AI-driven feedback to optimize your content for better engagement and performance.
                    </p>
                    <Link to="/optimization-feedback">
                        <Button variant="primary">
                            Optimize Content
                        </Button>
                    </Link>
                </Card>

                <Card title="Publisher">
                    <p className="text-text-light mb-4">
                        Publish and schedule your content across multiple platforms with ease.
                    </p>
                    <Link to="/publisher">
                        <Button variant="primary">
                            Publish Now
                        </Button>
                    </Link>
                </Card>

                <Card title="Documentation">
                    <p className="text-text-light mb-4">
                        Access all system logs.
                    </p>
                    <Link to="/documentation">
                        <Button variant="primary">
                            View Docs
                        </Button>
                    </Link>
                </Card>

                <Card title="Comments">
                    <p className="text-text-light mb-4">
                        Manage and respond to comments and feedback from your team.
                    </p>
                    <Link to="/comments">
                        <Button variant="primary">
                            Manage Comments
                        </Button>
                    </Link>
                </Card>

                <Card title="Chat">
                    <p className="text-text-light mb-4">
                        Chat with members of your team.
                    </p>
                    <Link to="/chat">
                        <Button variant="primary">
                            Start Chat
                        </Button>
                    </Link>
                </Card>
            </div>
        </>
    );
};

export default Home;