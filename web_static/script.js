// CortexCLI Web Interface JavaScript

class CortexCLI {
    constructor() {
        this.socket = null;
        this.currentModel = 'qwen2.5:72b';
        this.chatHistory = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.connectSocket();
    }

    setupEventListeners() {
        // Chat form
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        // Model selector
        const modelSelect = document.getElementById('model-select');
        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                this.currentModel = e.target.value;
                this.saveSettings();
            });
        }

        // Theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
            });
        }

        // Code execution
        const executeBtn = document.getElementById('execute-code');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => {
                this.executeCode();
            });
        }

        // File upload
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e);
            });
        }

        // Plugin management
        const pluginButtons = document.querySelectorAll('.plugin-toggle');
        pluginButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.togglePlugin(e.target.dataset.plugin);
            });
        });
    }

    connectSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.showNotification('Bağlandı', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.showNotification('Bağlantı kesildi', 'warning');
        });

        this.socket.on('new_message', (data) => {
            this.addMessage(data);
        });

        this.socket.on('error', (data) => {
            this.showNotification(data.message, 'error');
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage({
            user: message,
            assistant: '',
            timestamp: new Date().toISOString(),
            model: this.currentModel,
            type: 'user'
        });

        messageInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    model: this.currentModel
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage({
                    user: message,
                    assistant: data.response,
                    timestamp: data.timestamp,
                    model: this.currentModel,
                    type: 'assistant'
                });
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Mesaj gönderilemedi', 'error');
        }
    }

    addMessage(data) {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.type || 'assistant'}`;

        let content = '';
        if (data.user) {
            content += `<div class="message-user"><strong>Sen:</strong> ${this.escapeHtml(data.user)}</div>`;
        }
        if (data.assistant) {
            content += `<div class="message-assistant"><strong>AI:</strong> ${this.formatResponse(data.assistant)}</div>`;
        }
        if (data.model) {
            content += `<div class="message-model"><small>Model: ${data.model}</small></div>`;
        }

        messageDiv.innerHTML = content;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    formatResponse(response) {
        // Format code blocks
        response = response.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<div class="code-block"><pre><code class="language-${lang || 'text'}">${this.escapeHtml(code)}</code></pre></div>`;
        });

        // Format inline code
        response = response.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Format links
        response = response.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        return response;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async executeCode() {
        const codeEditor = document.getElementById('code-editor');
        const languageSelect = document.getElementById('language-select');
        const outputDiv = document.getElementById('code-output');

        if (!codeEditor || !languageSelect || !outputDiv) return;

        const code = codeEditor.value;
        const language = languageSelect.value;

        if (!code.trim()) {
            this.showNotification('Kod girin', 'warning');
            return;
        }

        outputDiv.innerHTML = '<div class="loading"></div> Çalıştırılıyor...';

        try {
            const response = await fetch('/api/code/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    language: language
                })
            });

            const data = await response.json();
            
            if (data.success) {
                outputDiv.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Başarılı!</strong> Çalışma süresi: ${data.execution_time}s
                    </div>
                    <div class="code-block">
                        <pre>${this.escapeHtml(data.output)}</pre>
                    </div>
                `;
            } else {
                outputDiv.innerHTML = `
                    <div class="alert alert-error">
                        <strong>Hata!</strong> ${this.escapeHtml(data.error)}
                    </div>
                `;
            }
        } catch (error) {
            outputDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Hata!</strong> Kod çalıştırılamadı
                </div>
            `;
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Dosya yüklendi: ${data.filename}`, 'success');
                this.loadFiles();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Dosya yüklenemedi', 'error');
        }
    }

    async loadFiles() {
        const filesContainer = document.getElementById('files-container');
        if (!filesContainer) return;

        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            
            if (data.success) {
                let html = '<div class="file-tree">';
                data.files.forEach(file => {
                    const icon = file.type === 'directory' ? '📁' : '📄';
                    html += `
                        <div class="file-item ${file.type}" onclick="cortexCLI.openFile('${file.name}')">
                            ${icon} ${file.name}
                        </div>
                    `;
                });
                html += '</div>';
                filesContainer.innerHTML = html;
            }
        } catch (error) {
            filesContainer.innerHTML = '<div class="alert alert-error">Dosyalar yüklenemedi</div>';
        }
    }

    async openFile(filename) {
        try {
            const response = await fetch('/api/file-preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filepath: filename
                })
            });

            const data = await response.json();
            
            if (data.success) {
                const previewDiv = document.getElementById('file-preview');
                if (previewDiv) {
                    previewDiv.innerHTML = `
                        <div class="code-block">
                            <pre>${this.escapeHtml(data.content)}</pre>
                        </div>
                    `;
                }
            }
        } catch (error) {
            this.showNotification('Dosya açılamadı', 'error');
        }
    }

    async togglePlugin(pluginName) {
        try {
            const response = await fetch('/api/plugins/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plugin: pluginName
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Plugin ${data.active ? 'etkinleştirildi' : 'devre dışı bırakıldı'}: ${pluginName}`, 'success');
                this.loadPlugins();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Plugin durumu değiştirilemedi', 'error');
        }
    }

    async loadPlugins() {
        const pluginsContainer = document.getElementById('plugins-container');
        if (!pluginsContainer) return;

        try {
            const response = await fetch('/api/plugins');
            const data = await response.json();
            
            if (data.success) {
                let html = '';
                data.plugins.forEach(plugin => {
                    html += `
                        <div class="plugin-card">
                            <div class="plugin-header">
                                <span class="plugin-status ${plugin.active ? 'active' : 'inactive'}"></span>
                                <strong>${plugin.name}</strong>
                                <button class="btn btn-secondary btn-sm plugin-toggle" data-plugin="${plugin.name}">
                                    ${plugin.active ? 'Devre Dışı' : 'Etkinleştir'}
                                </button>
                            </div>
                            <p>${plugin.description}</p>
                        </div>
                    `;
                });
                pluginsContainer.innerHTML = html;
                
                // Re-attach event listeners
                const pluginButtons = document.querySelectorAll('.plugin-toggle');
                pluginButtons.forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        this.togglePlugin(e.target.dataset.plugin);
                    });
                });
            }
        } catch (error) {
            pluginsContainer.innerHTML = '<div class="alert alert-error">Plugin\'ler yüklenemedi</div>';
        }
    }

    setTheme(themeId) {
        fetch('/api/themes/set', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                theme_id: themeId
            })
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Tema değiştirildi', 'success');
                this.loadThemeCSS();
            } else {
                this.showNotification(data.error, 'error');
            }
        });
    }

    loadThemeCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/api/themes/css?' + new Date().getTime();
        document.head.appendChild(link);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    saveSettings() {
        const settings = {
            model: this.currentModel,
            theme: document.getElementById('theme-select')?.value
        };
        localStorage.setItem('cortexcli-settings', JSON.stringify(settings));
    }

    loadSettings() {
        const settings = localStorage.getItem('cortexcli-settings');
        if (settings) {
            const data = JSON.parse(settings);
            this.currentModel = data.model || 'qwen2.5:72b';
            
            const modelSelect = document.getElementById('model-select');
            if (modelSelect) {
                modelSelect.value = this.currentModel;
            }
            
            const themeSelect = document.getElementById('theme-select');
            if (themeSelect && data.theme) {
                themeSelect.value = data.theme;
                this.setTheme(data.theme);
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cortexCLI = new CortexCLI();
});

// Export for global access
window.CortexCLI = CortexCLI; 