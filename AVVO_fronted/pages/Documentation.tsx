
import React, { useState, useMemo } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import { useApp } from '../contexts/AppContext';
import { LogEntry, Page } from '../types';
import { useAuth } from '../contexts/AuthContext';

interface TaskEntry {
    id: string;
    name: string;
    status: 'completed' | 'failed' | 'in_progress';
    timestamp: string;
    error?: string;
    retryable: boolean;
}

interface DocumentEntry {
    id: string;
    name: string;
    version: string;
    type: 'guide' | 'api' | 'tutorial' | 'reference';
    author: string;
    lastModified: string;
    size: string;
    downloadUrl: string;
}

interface VersionEntry {
    version: string;
    releaseDate: string;
    changes: string[];
    author: string;
}

interface DocumentationProps {
    setActivePage: (page: Page) => void;
}

const Documentation: React.FC<DocumentationProps> = ({ setActivePage }) => {
    const { user } = useAuth();
    const { logs, clearLogs } = useApp();
    const [filters, setFilters] = useState({ INFO: true, SUCCESS: true, ERROR: true });
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDocType, setSelectedDocType] = useState<string>('all');
    const [tasks, setTasks] = useState<TaskEntry[]>([
        {
            id: '1',
            name: 'Trend Discovery Agent',
            status: 'completed',
            timestamp: new Date().toLocaleTimeString(),
            retryable: false
        },
        {
            id: '2',
            name: 'Story Ideation Agent',
            status: 'completed',
            timestamp: new Date().toLocaleTimeString(),
            retryable: false
        },
        {
            id: '3',
            name: 'Video Generation Agent',
            status: 'failed',
            timestamp: new Date().toLocaleTimeString(),
            error: 'Video generation failed due to invalid script format',
            retryable: true
        }
    ]);

    const [documents, setDocuments] = useState<DocumentEntry[]>([
        {
            id: '1',
            name: 'API Reference Guide',
            version: '2.1.0',
            type: 'api',
            author: 'John Doe',
            lastModified: '2024-01-15',
            size: '2.4 MB',
            downloadUrl: '/docs/api-guide-v2.1.0.pdf'
        },
        {
            id: '2',
            name: 'User Manual',
            version: '1.5.2',
            type: 'guide',
            author: 'Jane Smith',
            lastModified: '2024-01-10',
            size: '5.1 MB',
            downloadUrl: '/docs/user-manual-v1.5.2.pdf'
        },
        {
            id: '3',
            name: 'Quick Start Tutorial',
            version: '1.0.0',
            type: 'tutorial',
            author: 'Mike Johnson',
            lastModified: '2024-01-08',
            size: '1.2 MB',
            downloadUrl: '/docs/quick-start-v1.0.0.pdf'
        }
    ]);

    const [versions, setVersions] = useState<VersionEntry[]>([
        {
            version: '2.1.0',
            releaseDate: '2024-01-15',
            author: 'John Doe',
            changes: [
                'Added new chat API endpoints',
                'Improved comment system performance',
                'Fixed documentation rendering issues',
                'Enhanced system logging capabilities'
            ]
        },
        {
            version: '2.0.0',
            releaseDate: '2023-12-20',
            author: 'Jane Smith',
            changes: [
                'Major UI redesign',
                'Added real-time collaboration features',
                'Implemented advanced search functionality',
                'Enhanced security measures'
            ]
        },
        {
            version: '1.9.0',
            releaseDate: '2023-11-15',
            author: 'Mike Johnson',
            changes: [
                'Added version control system',
                'Improved document management',
                'Enhanced export capabilities',
                'Bug fixes and performance improvements'
            ]
        }
    ]);

    const filteredDocuments = useMemo(() => {
        return documents.filter(doc => {
            const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                doc.author.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = selectedDocType === 'all' || doc.type === selectedDocType;
            return matchesSearch && matchesType;
        });
    }, [documents, searchTerm, selectedDocType]);

    const handleFilterChange = (level: keyof typeof filters) => {
        setFilters(prev => ({ ...prev, [level]: !prev[level] }));
    };

    const filteredLogs = useMemo(() => {
        return logs.filter(log => filters[log.level]);
    }, [logs, filters]);

    const retryTask = (taskId: string) => {
        setTasks(prev => prev.map(task =>
            task.id === taskId
                ? { ...task, status: 'in_progress' as const, error: undefined }
                : task
        ));
        // Here you would trigger the actual retry logic
        setTimeout(() => {
            setTasks(prev => prev.map(task =>
                task.id === taskId
                    ? { ...task, status: 'completed' as const }
                    : task
            ));
        }, 2000);
    };

    const exportLogs = () => {
        const logData = filteredLogs.map(log =>
            `[${log.timestamp}] ${log.level}: ${log.message}`
        ).join('\n');

        const blob = new Blob([logData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `system-logs-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const downloadDocument = (doc: DocumentEntry) => {
        // In a real implementation, this would trigger the actual download
        alert(`Downloading ${doc.name} v${doc.version}`);
    };

    const completedTasks = tasks.filter(task => task.status === 'completed');
    const failedTasks = tasks.filter(task => task.status === 'failed');
    
    const levelClasses = {
        INFO: 'text-cyan-500',
        SUCCESS: 'text-green-500',
        ERROR: 'text-red-500',
    };

    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Documentation & Versioning</h1>

            {/* Version Control Section */}
            <Card title="Version History" className="mb-8">
                <div className="space-y-6">
                    {versions.map((version, index) => (
                        <div key={version.version} className="border border-border rounded-lg p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-lg font-bold text-primary">Version {version.version}</h3>
                                    <p className="text-sm text-text-light">Released on {new Date(version.releaseDate).toLocaleDateString()} by {version.author}</p>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                    index === 0 ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                                }`}>
                                    {index === 0 ? 'Latest' : 'Previous'}
                                </span>
                            </div>
                            <div className="space-y-2">
                                <h4 className="font-medium text-sm">Changes:</h4>
                                <ul className="list-disc list-inside space-y-2">
                                    {version.changes.map((change, changeIndex) => (
                                        <li key={changeIndex} className="text-sm text-text-light leading-relaxed">{change}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            </Card>

            {/* Document Management Section */}
            <Card title="Document Library" className="mb-8">
                <div className="flex flex-col sm:flex-row gap-6 mb-8">
                    <div className="flex-1">
                        <label htmlFor="searchDocuments" className="sr-only">Search documents</label>
                        <input
                            type="text"
                            id="searchDocuments"
                            placeholder="Search documents..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full p-3 border border-border rounded-lg"
                        />
                    </div>
                    <div className="sm:w-48">
                        <label htmlFor="docTypeFilter" className="sr-only">Filter by document type</label>
                        <select
                            id="docTypeFilter"
                            value={selectedDocType}
                            onChange={(e) => setSelectedDocType(e.target.value)}
                            className="w-full p-3 border border-border rounded-lg"
                        >
                            <option value="all">All Types</option>
                            <option value="guide">Guides</option>
                            <option value="api">API Docs</option>
                            <option value="tutorial">Tutorials</option>
                            <option value="reference">References</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredDocuments.map(doc => (
                        <div key={doc.id} className="border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-3">
                                <h3 className="font-bold text-sm">{doc.name}</h3>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                    doc.type === 'api' ? 'bg-blue-100 text-blue-800' :
                                    doc.type === 'guide' ? 'bg-green-100 text-green-800' :
                                    doc.type === 'tutorial' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                }`}>
                                    {doc.type}
                                </span>
                            </div>
                            <div className="space-y-2 mb-4">
                                <p className="text-xs text-text-light leading-relaxed">Version {doc.version}</p>
                                <p className="text-xs text-text-light leading-relaxed">By {doc.author}</p>
                                <p className="text-xs text-text-light leading-relaxed">Modified: {new Date(doc.lastModified).toLocaleDateString()}</p>
                                <p className="text-xs text-text-light leading-relaxed">Size: {doc.size}</p>
                            </div>
                            <Button
                                size="sm"
                                variant="secondary"
                                onClick={() => downloadDocument(doc)}
                                className="w-full"
                            >
                                Download
                            </Button>
                        </div>
                    ))}
                </div>

                {filteredDocuments.length === 0 && (
                    <div className="text-center py-8 text-text-light">
                        No documents found matching your criteria.
                    </div>
                )}
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <Card title="Task Status Overview">
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <span className="text-green-600 font-semibold">✅ Completed Tasks</span>
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">{completedTasks.length}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-red-600 font-semibold">❌ Failed Tasks</span>
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">{failedTasks.length}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-blue-600 font-semibold">🔄 In Progress</span>
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">{tasks.filter(t => t.status === 'in_progress').length}</span>
                        </div>
                    </div>
                </Card>

                <Card title="Task Management">
                    <div className="space-y-4">
                        {tasks.map(task => (
                            <div key={task.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className={`font-medium ${
                                            task.status === 'completed' ? 'text-green-600' :
                                            task.status === 'failed' ? 'text-red-600' : 'text-blue-600'
                                        }`}>
                                            {task.status === 'completed' ? '✅' :
                                             task.status === 'failed' ? '❌' : '🔄'} {task.name}
                                        </span>
                                    </div>
                                    <div className="text-xs text-text-light mt-2 leading-relaxed">
                                        {task.timestamp}
                                        {task.error && (
                                            <div className="text-red-500 mt-2">
                                                Error: {task.error}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                {task.retryable && task.status === 'failed' && (
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => retryTask(task.id)}
                                    >
                                        Retry
                                    </Button>
                                )}
                            </div>
                        ))}
                    </div>
                </Card>
            </div>

            <Card title="System Activity Log">
                <div className="flex flex-wrap gap-6 items-center mb-6 pb-6 border-b border-border">
                    <div className="font-medium">Filter by:</div>
                    {Object.keys(filters).map(level => (
                        <label key={level} className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={filters[level as keyof typeof filters]}
                                onChange={() => handleFilterChange(level as keyof typeof filters)}
                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <span className={levelClasses[level as keyof typeof filters]}>{level}</span>
                        </label>
                    ))}
                    <Button variant="secondary" onClick={clearLogs} className="py-2 px-4 text-sm">
                        Clear Logs
                    </Button>
                    <Button variant="secondary" onClick={exportLogs} className="py-2 px-4 text-sm">
                        Export Logs
                    </Button>
                </div>
                <div className="log-feed bg-gray-800 p-6 rounded-lg font-mono text-sm text-gray-300 max-h-[65vh] overflow-y-auto">
                    {filteredLogs.map((log, index) => (
                        <div key={index} className="mb-3">
                             <span className="text-gray-500 mr-2">[{log.timestamp}]</span>
                             <span className={`${levelClasses[log.level]} font-bold mr-2`}>{log.level}</span>
                             <span className="leading-relaxed">{log.message}</span>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};

export default Documentation;
