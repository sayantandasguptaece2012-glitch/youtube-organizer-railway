"""
Production-ready YouTube Organizer Web Application
"""

from flask import Flask, jsonify, request, render_template_string, redirect
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from youtube_auth import YouTubeManager
from playlist_categorizer import PlaylistCategorizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get directory where this script is running
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH', os.path.join(SCRIPT_DIR, 'credentials.json'))

# If credentials file doesn't exist but GOOGLE_CREDENTIALS env var is set, create it
if not os.path.exists(CREDENTIALS_PATH) and os.environ.get('GOOGLE_CREDENTIALS'):
    try:
        import json
        credentials_data = json.loads(os.environ['GOOGLE_CREDENTIALS'])
        with open(CREDENTIALS_PATH, 'w') as f:
            json.dump(credentials_data, f)
        logger.info("Created credentials.json from environment variable")
    except Exception as e:
        logger.error(f"Failed to create credentials.json from env var: {e}")

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Global instances
youtube_manager = None
categorizer = PlaylistCategorizer()

# Production HTML template (embedded for deployment)
PRODUCTION_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Playlist Organizer - Organize Your YouTube Content</title>
    <meta name="description" content="Organize your YouTube playlists with smart categorization. Automatically categorize playlists into Food, Career, Investment, and more.">
    <meta name="keywords" content="YouTube, playlists, organizer, categorization, management">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="YouTube Playlist Organizer">
    <meta property="og:description" content="Organize your YouTube playlists with smart categorization">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://picsum.photos/seed/youtube-organizer/1200/630.jpg">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com/3.3.0"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        .playlist-card { transition: all 0.3s ease; }
        .playlist-card:hover { transform: translateY(-4px); }
        .video-item { transition: background-color 0.2s ease; }
        .video-item:hover { background-color: rgba(59, 130, 246, 0.05); }
        .loading-spinner { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fab fa-youtube text-3xl"></i>
                    <div>
                        <h1 class="text-2xl font-bold">YouTube Playlist Organizer</h1>
                        <p class="text-sm opacity-90">Organize your playlists with smart categorization</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <button id="refreshBtn" class="bg-white text-red-600 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                        <i class="fas fa-sync-alt mr-2"></i>Refresh
                    </button>
                    <button id="shareBtn" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                        <i class="fas fa-share-alt mr-2"></i>Share
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Loading State -->
        <div id="loadingState" class="text-center py-12">
            <div class="loading-spinner mx-auto mb-4"></div>
            <p class="text-gray-600">Loading your YouTube playlists...</p>
        </div>

        <!-- Error State -->
        <div id="errorState" class="hidden bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
            <h3 class="text-lg font-semibold text-red-800 mb-2">Error Loading Playlists</h3>
            <p id="errorMessage" class="text-red-600"></p>
            <button id="retryBtn" class="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
                <i class="fas fa-redo mr-2"></i>Retry
            </button>
        </div>

        <!-- Channel Info -->
        <div id="channelInfo" class="hidden bg-white rounded-lg shadow-md p-6 mb-8">
            <div class="flex items-center space-x-4">
                <img id="channelThumbnail" src="" alt="Channel" class="w-16 h-16 rounded-full">
                <div>
                    <h2 id="channelTitle" class="text-xl font-bold text-gray-800"></h2>
                    <p id="channelStats" class="text-gray-600"></p>
                </div>
            </div>
        </div>

        <!-- Category Filter -->
        <div id="categoryFilter" class="hidden bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Filter by Category</h3>
            <div class="flex flex-wrap gap-2" id="categoryButtons">
                <button class="category-btn px-4 py-2 rounded-full bg-blue-500 text-white" data-category="all">
                    All Playlists
                </button>
            </div>
        </div>

        <!-- Stats Cards -->
        <div id="statsCards" class="hidden grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">User Playlists</p>
                        <p id="userPlaylistCount" class="text-2xl font-bold text-gray-800">0</p>
                    </div>
                    <i class="fas fa-list text-blue-500 text-2xl"></i>
                </div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Categories</p>
                        <p id="categoryCount" class="text-2xl font-bold text-gray-800">0</p>
                    </div>
                    <i class="fas fa-tags text-purple-500 text-2xl"></i>
                </div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Liked Videos</p>
                        <p id="likedVideosCount" class="text-2xl font-bold text-gray-800">0</p>
                    </div>
                    <i class="fas fa-heart text-red-500 text-2xl"></i>
                </div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Total Videos</p>
                        <p id="totalVideosCount" class="text-2xl font-bold text-gray-800">0</p>
                    </div>
                    <i class="fas fa-play-circle text-green-500 text-2xl"></i>
                </div>
            </div>
        </div>

        <!-- Playlists Container -->
        <div id="playlistsContainer" class="hidden">
            <section id="categorizedPlaylists" class="mb-12">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-folder mr-2 text-purple-500"></i>
                    Playlists by Category
                </h3>
                <div id="categoriesContainer" class="space-y-8">
                    <!-- Categories will be inserted here -->
                </div>
            </section>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="mb-4">YouTube Playlist Organizer - Organize your content smartly</p>
            <div class="flex justify-center space-x-6 text-sm">
                <a href="#" class="hover:text-red-400">Privacy</a>
                <a href="#" class="hover:text-red-400">Terms</a>
                <a href="#" class="hover:text-red-400">About</a>
                <a href="https://github.com" class="hover:text-red-400">GitHub</a>
            </div>
        </div>
    </footer>

    <script>
        class YouTubePlaylistWeb {
            constructor() {
                this.loading = false;
                this.playlists = [];
                this.categorySummary = {};
                this.currentFilter = 'all';
                this.editingPlaylist = null;
                this.init();
            }

            init() {
                this.setupEventListeners();
                this.loadPlaylists();
            }

            setupEventListeners() {
                // Add event listeners only if elements exist
                const refreshBtn = document.getElementById('refreshBtn');
                if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadPlaylists());
                
                const retryBtn = document.getElementById('retryBtn');
                if (retryBtn) retryBtn.addEventListener('click', () => this.loadPlaylists());
                
                const closeModal = document.getElementById('closeModal');
                if (closeModal) closeModal.addEventListener('click', () => this.closeModal());
                
                const closeCategoryModal = document.getElementById('closeCategoryModal');
                if (closeCategoryModal) closeCategoryModal.addEventListener('click', () => this.closeCategoryModal());
                
                const saveCategoryEdit = document.getElementById('saveCategoryEdit');
                if (saveCategoryEdit) saveCategoryEdit.addEventListener('click', () => this.saveCategoryEdit());
                
                // Close modal on background click
                const playlistModal = document.getElementById('playlistModal');
                if (playlistModal) {
                    playlistModal.addEventListener('click', (e) => {
                        if (e.target.id === 'playlistModal') {
                            this.closeModal();
                        }
                    });
                }
                
                const categoryEditModal = document.getElementById('categoryEditModal');
                if (categoryEditModal) {
                    categoryEditModal.addEventListener('click', (e) => {
                        if (e.target.id === 'categoryEditModal') {
                            this.closeCategoryModal();
                        }
                    });
                }
            }

            async loadPlaylists() {
                this.showLoading();
                try {
                    const response = await fetch('/api/playlists');
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    this.playlists = data;
                    this.categorySummary = data.category_summary || {};
                    this.renderPlaylists(data);
                } catch (error) {
                    console.error('Error loading playlists:', error);
                    this.showError('Failed to load playlists. Please make sure backend server is running.');
                }
            }

            showLoading() {
                document.getElementById('loadingState').classList.remove('hidden');
                document.getElementById('errorState').classList.add('hidden');
                document.getElementById('channelInfo').classList.add('hidden');
                document.getElementById('statsCards').classList.add('hidden');
                document.getElementById('playlistsContainer').classList.add('hidden');
            }

            showError(message) {
                document.getElementById('loadingState').classList.add('hidden');
                document.getElementById('errorState').classList.remove('hidden');
                document.getElementById('errorMessage').textContent = message;
            }

            renderPlaylists(data) {
                document.getElementById('loadingState').classList.add('hidden');
                document.getElementById('errorState').classList.add('hidden');
                
                // Render channel info
                if (data.channel) {
                    this.renderChannelInfo(data.channel);
                }
                
                // Render stats
                this.renderStats(data);
                
                // Render playlists
                this.renderUserPlaylists(data.user_playlists || []);
                this.renderSystemPlaylists(data.system_playlists || {});
                
                document.getElementById('channelInfo').classList.remove('hidden');
                document.getElementById('statsCards').classList.remove('hidden');
                document.getElementById('categoryFilter').classList.remove('hidden');
                document.getElementById('playlistsContainer').classList.remove('hidden');
            }

            renderChannelInfo(channel) {
                document.getElementById('channelTitle').textContent = channel.title;
                document.getElementById('channelStats').textContent = 
                    `${channel.subscriber_count} subscribers • ${channel.video_count} videos`;
                document.getElementById('channelThumbnail').src = channel.thumbnail_url;
            }

            renderStats(data) {
                const userCount = data.user_playlists ? data.user_playlists.length : 0;
                const categoryCount = Object.keys(this.categorySummary).filter(key => 
                    this.categorySummary[key].playlist_count > 0
                ).length;
                const likedCount = data.system_playlists && data.system_playlists.likes ? 
                    data.system_playlists.likes.video_count : 0;
                const totalVideos = data.user_playlists ? 
                    data.user_playlists.reduce((sum, p) => sum + p.video_count, 0) + likedCount : likedCount;

                document.getElementById('userPlaylistCount').textContent = userCount;
                document.getElementById('categoryCount').textContent = categoryCount;
                document.getElementById('likedVideosCount').textContent = likedCount;
                document.getElementById('totalVideosCount').textContent = totalVideos;
            }

            renderUserPlaylists(playlists) {
                this.renderCategorizedPlaylists();
                this.renderCategoryFilter();
            }

            renderCategorizedPlaylists() {
                const container = document.getElementById('categoriesContainer');
                container.innerHTML = '';

                const categories = Object.keys(this.categorySummary).filter(category => 
                    this.categorySummary[category].playlist_count > 0
                ).sort((a, b) => this.categorySummary[b].playlist_count - this.categorySummary[a].playlist_count);

                categories.forEach(category => {
                    const categoryData = this.categorySummary[category];
                    const categorySection = this.createCategorySection(category, categoryData);
                    container.appendChild(categorySection);
                });

                // Show uncategorized section if needed
                const uncategorized = this.playlists.user_playlists?.filter(p => p.category === 'Other') || [];
                if (uncategorized.length > 0) {
                    const uncategorizedSection = document.getElementById('uncategorizedPlaylists');
                    uncategorizedSection.classList.remove('hidden');
                    const uncategorizedContainer = document.getElementById('uncategorizedContainer');
                    uncategorizedContainer.innerHTML = '';
                    uncategorized.forEach(playlist => {
                        const card = this.createPlaylistCard(playlist, 'user');
                        uncategorizedContainer.appendChild(card);
                    });
                }
            }

            createCategorySection(categoryName, categoryData) {
                const section = document.createElement('div');
                section.className = 'bg-white rounded-lg shadow-md p-6';
                
                const categoryColors = {
                    'Food': 'bg-green-100 text-green-800 border-green-200',
                    'Career': 'bg-blue-100 text-blue-800 border-blue-200',
                    'Investment': 'bg-purple-100 text-purple-800 border-purple-200',
                    'Education': 'bg-indigo-100 text-indigo-800 border-indigo-200',
                    'Entertainment': 'bg-pink-100 text-pink-800 border-pink-200',
                    'Health & Fitness': 'bg-red-100 text-red-800 border-red-200',
                    'Technology': 'bg-gray-100 text-gray-800 border-gray-200',
                    'Travel': 'bg-yellow-100 text-yellow-800 border-yellow-200',
                    'Lifestyle': 'bg-orange-100 text-orange-800 border-orange-200',
                    'Other': 'bg-gray-100 text-gray-800 border-gray-200'
                };

                const colorClass = categoryColors[categoryName] || categoryColors['Other'];
                
                section.innerHTML = `
                    <div class="flex items-center justify-between mb-4">
                        <h4 class="text-lg font-semibold text-gray-800 flex items-center">
                            <span class="inline-block px-3 py-1 rounded-full text-sm font-medium mr-3 ${colorClass}">
                                ${categoryName}
                            </span>
                            <span class="text-gray-500 text-sm">${categoryData.playlist_count} playlists • ${categoryData.total_videos} videos</span>
                        </h4>
                        <button class="text-blue-500 hover:text-blue-700 text-sm toggle-category" data-category="${categoryName}">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 category-content" data-category="${categoryName}">
                        <!-- Playlist cards will be inserted here -->
                    </div>
                `;

                // Add playlist cards to this category
                const categoryContent = section.querySelector('.category-content');
                categoryData.playlists.forEach(playlist => {
                    const card = this.createPlaylistCard(playlist, 'user');
                    categoryContent.appendChild(card);
                });

                // Add toggle functionality
                const toggleBtn = section.querySelector('.toggle-category');
                toggleBtn.addEventListener('click', () => {
                    const content = section.querySelector('.category-content');
                    const icon = toggleBtn.querySelector('i');
                    
                    if (content.style.display === 'none') {
                        content.style.display = 'grid';
                        icon.className = 'fas fa-chevron-down';
                    } else {
                        content.style.display = 'none';
                        icon.className = 'fas fa-chevron-right';
                    }
                });

                return section;
            }

            renderCategoryFilter() {
                const container = document.getElementById('categoryButtons');
                container.innerHTML = '';

                // Add "All" button
                const allBtn = document.createElement('button');
                allBtn.className = 'category-btn px-4 py-2 rounded-full bg-blue-500 text-white';
                allBtn.textContent = 'All Playlists';
                allBtn.dataset.category = 'all';
                allBtn.addEventListener('click', () => this.filterByCategory('all'));
                container.appendChild(allBtn);

                // Add category buttons
                const categories = Object.keys(this.categorySummary).filter(category => 
                    this.categorySummary[category].playlist_count > 0
                );

                categories.forEach(category => {
                    const btn = document.createElement('button');
                    btn.className = 'category-btn px-4 py-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300';
                    btn.textContent = `${category} (${this.categorySummary[category].playlist_count})`;
                    btn.dataset.category = category;
                    btn.addEventListener('click', () => this.filterByCategory(category));
                    container.appendChild(btn);
                });
            }

            filterByCategory(category) {
                this.currentFilter = category;
                
                // Update button styles
                document.querySelectorAll('.category-btn').forEach(btn => {
                    if (btn.dataset.category === category) {
                        btn.className = 'category-btn px-4 py-2 rounded-full bg-blue-500 text-white';
                    } else {
                        btn.className = 'category-btn px-4 py-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300';
                    }
                });

                // Show/hide category sections
                document.querySelectorAll('.category-content').forEach(content => {
                    if (category === 'all' || content.dataset.category === category) {
                        content.parentElement.style.display = 'block';
                    } else {
                        content.parentElement.style.display = 'none';
                    }
                });

                // Handle uncategorized section
                const uncategorizedSection = document.getElementById('uncategorizedPlaylists');
                if (category === 'all' || category === 'Other') {
                    uncategorizedSection.style.display = 'block';
                } else {
                    uncategorizedSection.style.display = 'none';
                }
            }

            renderSystemPlaylists(systemPlaylists) {
                const container = document.getElementById('systemPlaylists');
                container.innerHTML = '';

                const systemPlaylistTypes = [
                    { key: 'likes', name: 'Liked Videos', icon: 'heart', color: 'red' },
                    { key: 'uploads', name: 'Your Uploads', icon: 'upload', color: 'green' }
                ];

                systemPlaylistTypes.forEach(type => {
                    if (systemPlaylists[type.key]) {
                        const playlist = {
                            ...systemPlaylists[type.key],
                            title: type.name,
                            type: type.key,
                            icon: type.icon,
                            color: type.color
                        };
                        const card = this.createPlaylistCard(playlist, 'system');
                        container.appendChild(card);
                    }
                });
            }

            createPlaylistCard(playlist, type) {
                const card = document.createElement('div');
                card.className = 'playlist-card bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg';
                
                const iconClass = playlist.icon || 'list';
                const colorClass = playlist.color || 'blue';
                
                card.innerHTML = `
                    <div class="relative">
                        <img src="${playlist.thumbnail_url || `https://picsum.photos/seed/${playlist.id}/400/200.jpg`}" 
                             alt="${playlist.title}" 
                             class="w-full h-48 object-cover">
                        <div class="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-sm">
                            <i class="fas fa-play mr-1"></i>${playlist.video_count || 0}
                        </div>
                        <div class="absolute top-2 left-2 bg-${colorClass}-500 text-white p-2 rounded-full">
                            <i class="fas fa-${iconClass}"></i>
                        </div>
                        ${playlist.category ? `
                        <div class="absolute bottom-2 left-2">
                            <span class="bg-green-500 text-white px-2 py-1 rounded text-xs font-medium">
                                ${playlist.category}
                            </span>
                        </div>
                        ` : ''}
                    </div>
                    <div class="p-4">
                        <h4 class="font-semibold text-gray-800 mb-2 truncate">${playlist.title}</h4>
                        <p class="text-gray-600 text-sm line-clamp-2">${playlist.description || 'No description available'}</p>
                        <div class="mt-3 flex items-center justify-between">
                            <span class="text-xs text-gray-500">
                                <i class="fas fa-calendar mr-1"></i>
                                ${new Date(playlist.published_at).toLocaleDateString()}
                            </span>
                            <div class="flex space-x-2">
                                <button class="text-blue-500 hover:text-blue-700 text-sm font-medium" onclick="event.stopPropagation(); window.app.showPlaylistVideos('${playlist.id}', '${type}')">
                                    View Videos <i class="fas fa-arrow-right ml-1"></i>
                                </button>
                                <button class="text-green-500 hover:text-green-700 text-sm font-medium" onclick="event.stopPropagation(); window.app.openCategoryEdit('${playlist.id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;

                card.addEventListener('click', () => this.showPlaylistVideos(playlist, type));
                return card;
            }

            async showPlaylistVideos(playlist, type) {
                const modal = document.getElementById('playlistModal');
                const modalTitle = document.getElementById('modalTitle');
                const modalVideos = document.getElementById('modalVideos');

                modalTitle.textContent = playlist.title;
                modalVideos.innerHTML = '<div class="text-center py-8"><div class="loading-spinner mx-auto mb-4"></div><p class="text-gray-600">Loading videos...</p></div>';
                modal.classList.remove('hidden');

                try {
                    const response = await fetch(`/api/playlist/${playlist.id}?type=${type}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const videos = await response.json();
                    this.renderVideos(videos);
                } catch (error) {
                    console.error('Error loading videos:', error);
                    modalVideos.innerHTML = '<p class="text-red-500 text-center">Failed to load videos</p>';
                }
            }

            renderVideos(videos) {
                const modalVideos = document.getElementById('modalVideos');
                
                if (videos.length === 0) {
                    modalVideos.innerHTML = '<p class="text-gray-500 text-center">No videos found in this playlist</p>';
                    return;
                }

                modalVideos.innerHTML = videos.map(video => `
                    <div class="video-item flex items-start space-x-3 p-3 rounded-lg cursor-pointer">
                        <img src="${video.thumbnail_url}" alt="${video.title}" class="w-24 h-16 object-cover rounded">
                        <div class="flex-1">
                            <h5 class="font-medium text-gray-800 line-clamp-2">${video.title}</h5>
                            <p class="text-sm text-gray-600 mt-1">
                                <i class="fas fa-calendar mr-1"></i>
                                ${new Date(video.published_at).toLocaleDateString()}
                            </p>
                        </div>
                        <a href="https://youtube.com/watch?v=${video.video_id}" 
                           target="_blank" 
                           class="text-red-500 hover:text-red-700">
                            <i class="fab fa-youtube text-xl"></i>
                        </a>
                    </div>
                `).join('');
            }

            closeModal() {
                document.getElementById('playlistModal').classList.add('hidden');
            }

            openCategoryEdit(playlistId) {
                const playlist = this.findPlaylistById(playlistId);
                if (!playlist) return;

                this.editingPlaylist = playlist;
                
                // Set modal content
                document.getElementById('editPlaylistTitle').textContent = playlist.title;
                document.getElementById('categorySelect').value = playlist.category || 'Other';
                
                // Update current category badge
                const currentBadge = document.getElementById('currentCategoryBadge');
                const confidence = document.getElementById('currentCategoryConfidence');
                
                if (playlist.category) {
                    currentBadge.textContent = playlist.category;
                    currentBadge.className = `inline-block px-3 py-1 rounded-full text-sm font-medium ${this.getCategoryColorClass(playlist.category)}`;
                    confidence.textContent = `(confidence: ${(playlist.category_confidence || 0).toFixed(2)})`;
                } else {
                    currentBadge.textContent = 'Not categorized';
                    currentBadge.className = 'inline-block px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800';
                    confidence.textContent = '';
                }
                
                // Show modal
                document.getElementById('categoryEditModal').classList.remove('hidden');
            }

            closeCategoryModal() {
                document.getElementById('categoryEditModal').classList.add('hidden');
                this.editingPlaylist = null;
            }

            async saveCategoryEdit() {
                if (!this.editingPlaylist) return;

                const newCategory = document.getElementById('categorySelect').value;
                
                try {
                    const response = await fetch(`/api/playlist/${this.editingPlaylist.id}/category`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            category: newCategory
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    // Update local data
                    this.editingPlaylist.category = newCategory;
                    this.editingPlaylist.category_confidence = 1.0; // Manual categorization has full confidence
                    
                    // Refresh display
                    this.loadPlaylists();
                    this.closeCategoryModal();
                    
                    // Show success message
                    this.showSuccessMessage('Category updated successfully!');
                    
                } catch (error) {
                    console.error('Error updating category:', error);
                    this.showError('Failed to update category');
                }
            }

            findPlaylistById(playlistId) {
                return this.playlists.user_playlists?.find(p => p.id === playlistId);
            }

            getCategoryColorClass(category) {
                const colors = {
                    'Food': 'bg-green-100 text-green-800',
                    'Career': 'bg-blue-100 text-blue-800',
                    'Investment': 'bg-purple-100 text-purple-800',
                    'Education': 'bg-indigo-100 text-indigo-800',
                    'Entertainment': 'bg-pink-100 text-pink-800',
                    'Health & Fitness': 'bg-red-100 text-red-800',
                    'Technology': 'bg-gray-100 text-gray-800',
                    'Travel': 'bg-yellow-100 text-yellow-800',
                    'Lifestyle': 'bg-orange-100 text-orange-800',
                    'Other': 'bg-gray-100 text-gray-800'
                };
                return colors[category] || colors['Other'];
            }

            showSuccessMessage(message) {
                // Create success notification
                const notification = document.createElement('div');
                notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
                notification.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-check-circle mr-2"></i>
                        ${message}
                    </div>
                `;
                
                document.body.appendChild(notification);
                
                // Remove after 3 seconds
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
        }

        // Initialize app
        document.addEventListener('DOMContentLoaded', () => {
            window.app = new YouTubePlaylistWeb();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve main HTML page or setup page."""
    # Check if credentials exist
    if not os.path.exists(CREDENTIALS_PATH):
        return render_template_string(open('static/setup.html').read())
    
    # Check if authenticated
    token_path = os.path.join(SCRIPT_DIR, 'token.pickle')
    if not os.path.exists(token_path):
        return render_template_string(open('static/auth.html').read())
    
    # For development, serve the full static HTML
    if app.config['DEBUG']:
        with open(os.path.join(SCRIPT_DIR, 'static', 'index.html'), 'r') as f:
            return f.read()
    
    return PRODUCTION_HTML

@app.route('/upload-credentials', methods=['POST'])
def upload_credentials():
    """Handle credentials file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename != 'credentials.json':
            return jsonify({'error': 'File must be named credentials.json'}), 400
        
        # Save file to absolute path
        file.save(CREDENTIALS_PATH)
        
        return jsonify({
            'success': True,
            'message': 'Credentials uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    """Get all playlists from the authenticated YouTube account."""
    global youtube_manager
    
    try:
        # Check if credentials exist
        if not os.path.exists(CREDENTIALS_PATH):
            return jsonify({'error': 'No credentials file found. Please upload credentials.json'}), 401
        
        # Check if authenticated
        token_path = os.path.join(SCRIPT_DIR, 'token.pickle')
        if not os.path.exists(token_path):
            return jsonify({'error': 'Not authenticated. Please authenticate via command line first.'}), 401
        
        # Try to get authenticated service
        try:
            # Direct approach without file_cache
            import pickle
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            
            # Build service directly
            from googleapiclient.discovery import build
            service = build('youtube', 'v3', credentials=creds)
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed. Please re-authenticate.'}), 401
        
        # Use the authenticated service directly instead of YouTubeManager
        # Get channel info
        channel_response = service.channels().list(
            part='snippet',
            mine=True
        ).execute()
        
        channel_info = None
        if channel_response.get('items'):
            channel = channel_response['items'][0]
            channel_info = {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'thumbnail_url': channel['snippet']['thumbnails'].get('high', {}).get('url', '')
            }
        
        # Get user playlists
        playlists_response = service.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        ).execute()
        
        user_playlists = []
        for playlist in playlists_response.get('items', []):
            playlist_data = {
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet'].get('description', ''),
                'published_at': playlist['snippet']['publishedAt'],
                'video_count': playlist['contentDetails']['itemCount'],
                'thumbnail_url': playlist['snippet']['thumbnails'].get('high', {}).get('url', '')
            }
            user_playlists.append(playlist_data)
        
        # Categorize user playlists
        categorized_user_playlists = categorizer.categorize_playlists(user_playlists)
        
        # Get category summary
        category_summary = categorizer.get_category_summary(user_playlists)
        
        # Get system playlists
        system_playlists = {}
        try:
            channel_response = service.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if channel_response.get('items'):
                related_playlists = channel_response['items'][0]['contentDetails']['relatedPlaylists']
                
                # Get likes playlist
                if related_playlists.get('likes'):
                    likes_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=related_playlists['likes']
                    ).execute()
                    
                    if likes_response.get('items'):
                        likes = likes_response['items'][0]
                        system_playlists['likes'] = {
                            'id': likes['id'],
                            'title': likes['snippet']['title'],
                            'description': likes['snippet'].get('description', ''),
                            'published_at': likes['snippet']['publishedAt'],
                            'video_count': likes['contentDetails']['itemCount'],
                            'thumbnail_url': likes['snippet']['thumbnails'].get('high', {}).get('url', '')
                        }
                        
        except Exception as e:
            logger.error(f"Error getting system playlists: {e}")
        
        logger.info(f"Returning playlists: {len(categorized_user_playlists)} user playlists, {len(system_playlists)} system playlists")
        return jsonify({
            'channel': channel_info,
            'user_playlists': categorized_user_playlists,
            'system_playlists': system_playlists,
            'category_summary': category_summary
        })
        
    except Exception as e:
        logger.error(f"Error in get_playlists: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<playlist_id>', methods=['GET'])
def get_playlist_videos(playlist_id):
    """Get videos from a specific playlist."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            return jsonify({'error': 'Not authenticated'}), 401
        
        playlist_type = request.args.get('type', 'user')
        max_results = int(request.args.get('max_results', 25))
        
        videos = youtube_manager.get_playlist_videos(playlist_id, max_results)
        
        return jsonify(videos)
        
    except Exception as e:
        logger.error(f"Error getting playlist videos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<playlist_id>/category', methods=['POST'])
def update_playlist_category(playlist_id):
    """Update the category of a playlist."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        new_category = data.get('category')
        
        if not new_category:
            return jsonify({'error': 'Category is required'}), 400
        
        from playlist_categorizer import PlaylistCategory
        
        try:
            category_enum = PlaylistCategory(new_category)
        except ValueError:
            return jsonify({'error': f'Invalid category: {new_category}'}), 400
        
        categorizer.add_custom_rule(
            keywords=[playlist_id],
            category=category_enum,
            weight=10
        )
        
        return jsonify({
            'success': True,
            'message': f'Playlist category updated to {new_category}',
            'playlist_id': playlist_id,
            'new_category': new_category
        })
        
    except Exception as e:
        logger.error(f"Error updating category: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth', methods=['GET'])
def start_auth():
    """Start YouTube authentication flow."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            youtube_manager = YouTubeManager()
        
        # Check if credentials exist
        if not os.path.exists(CREDENTIALS_PATH):
            return jsonify({'error': 'No credentials file found'}), 401
        
        # Get authorization URL
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/youtube'],
            redirect_uri=os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:8000/api/auth/callback')
        )
        
        # Generate auth URL for web-based flow
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return jsonify({
            'auth_url': auth_url,
            'message': 'Please visit this URL to authorize the application'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback."""
    global youtube_manager
    
    try:
        # Get authorization code from query parameters
        auth_code = request.args.get('code')
        if not auth_code:
            return jsonify({'error': 'No authorization code provided'}), 400
        
        # Exchange code for credentials
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/youtube'],
            redirect_uri=os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:8000/api/auth/callback')
        )
        
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save credentials
        import pickle
        with open(os.path.join(SCRIPT_DIR, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)
        
        # Build service
        service = build('youtube', 'v3', credentials=creds)
        
        # Update global manager if needed
        global youtube_manager
        if youtube_manager:
            youtube_manager.service = service
        
        # Redirect to main app
        return redirect('/')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    global youtube_manager
    
    # Check if credentials exist
    if not os.path.exists(CREDENTIALS_PATH):
        return jsonify({
            'status': 'healthy', 
            'authenticated': False,
            'error': 'No credentials file found',
            'timestamp': datetime.now().isoformat()
        })
    
    # Check if authenticated
    token_path = os.path.join(SCRIPT_DIR, 'token.pickle')
    if not os.path.exists(token_path):
        return jsonify({
            'status': 'healthy', 
            'authenticated': False,
            'error': 'No authentication token found',
            'timestamp': datetime.now().isoformat()
        })
    
    # Try to get authenticated service
    try:
        from web_auth import get_authenticated_service
        service = get_authenticated_service(CREDENTIALS_PATH, token_path)
        
        if service:
            return jsonify({
                'status': 'healthy', 
                'authenticated': True,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'healthy', 
                'authenticated': False,
                'error': 'Authentication expired',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'status': 'healthy', 
            'authenticated': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/info', methods=['GET'])
def app_info():
    """Application information."""
    return jsonify({
        'name': 'YouTube Playlist Organizer',
        'version': '1.0.0',
        'description': 'Organize your YouTube playlists with smart categorization',
        'features': [
            'Automatic playlist categorization',
            'Manual category editing',
            'Category filtering',
            'Video browsing',
            'Export functionality'
        ],
        'categories': [cat.value for cat in PlaylistCategory]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting YouTube Playlist Organizer on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
