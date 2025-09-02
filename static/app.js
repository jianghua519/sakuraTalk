class SakuraTalk {
    constructor() {
        this.chatHistory = document.getElementById('chatHistory');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.recordButton = document.getElementById('recordButton');
        this.recordStatus = document.getElementById('recordStatus');
        this.micIcon = document.getElementById('micIcon');
        this.recordingIndicator = document.getElementById('recordingIndicator');
        
        // 新增的元素
        this.aiTranslation = document.getElementById('aiTranslation');
        this.aiJapaneseText = document.getElementById('aiJapaneseText');
        this.aiHiragana = document.getElementById('aiHiragana');
        this.aiPronunciationScore = document.getElementById('aiPronunciationScore');
        this.userRecognizedText = document.getElementById('userRecognizedText');
        this.userPronunciationScore = document.getElementById('userPronunciationScore');
        this.nextSuggestion = document.getElementById('nextSuggestion');
        this.suggestionHiragana = document.getElementById('suggestionHiragana');
        this.suggestionTranslation = document.getElementById('suggestionTranslation');
        this.playUserVoice = document.getElementById('playUserVoice');
        this.playAiVoice = document.getElementById('playAiVoice');
        
        this.isRecording = false;
        this.currentScenario = 'greeting';
        this.audioElement = null; // 用于播放语音
        this.userAudioBlob = null; // 用户录音的音频数据
        
        // Web Speech API相关
        this.recognition = null;
        this.synth = window.speechSynthesis;
        
        this.initEventListeners();
        this.initSpeechRecognition();
    }
    
    initEventListeners() {
        // 发送消息事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // 录音事件 - 添加移动端触摸支持
        this.recordButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleRecording();
        });
        
        // 添加移动端触摸事件支持
        this.recordButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        
        this.recordButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        // 播放控制事件
        this.playUserVoice.addEventListener('click', () => this.playUserVoiceRecording());
        this.playAiVoice.addEventListener('click', () => this.playAiVoiceResponse());
        
        // 场景选择事件
        const scenarioButtons = document.querySelectorAll('.scenario-btn');
        scenarioButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.selectScenario(button.dataset.scenario);
            });
        });
    }
    
    // 初始化语音识别
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'ja-JP'; // 设置为日语识别
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            // 识别结果回调
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.userInput.value = transcript;
                this.recordStatus.textContent = '识别完成';
                this.userRecognizedText.textContent = transcript;
                this.stopRecording();
            };
            
            // 识别错误回调
            this.recognition.onerror = (event) => {
                console.error('语音识别错误:', event.error);
                this.recordStatus.textContent = '识别错误: ' + event.error;
                this.stopRecording();
            };
            
            // 识别结束回调
            this.recognition.onend = () => {
                this.stopRecording();
            };
        } else {
            console.warn('浏览器不支持Web Speech API');
        }
    }
    
    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        this.addMessageToHistory(message, 'user');
        this.userInput.value = '';
        
        // 显示AI正在输入
        const aiLoadingMessage = this.addMessageToHistory('AI正在思考中...', 'ai', true);
        
        // 发送请求到后端
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // 移除加载消息
            aiLoadingMessage.remove();
            
            // 显示AI回复
            const aiMessage = `
                <strong>AI助手:</strong>
                <p>${data.message}</p>
            `;
            this.addMessageToHistory(aiMessage, 'ai');
            
            // 更新详情面板
            this.updateDetailsPanel(data, message);
            
            // 请求语音合成
            this.synthesizeSpeech(data.message);
        })
        .catch(error => {
            console.error('Error:', error);
            aiLoadingMessage.remove();
            this.addMessageToHistory('抱歉，处理您的消息时出现错误。', 'ai');
        });
    }
    
    // 更新详情面板
    updateDetailsPanel(data, userMessage) {
        // 更新AI助手回复详情
        this.aiHiragana.textContent = data.hiragana || '暂无平假名';
        this.aiJapaneseText.textContent = data.message || '暂无内容';
        this.aiTranslation.textContent = data.translation || '暂无翻译';
        this.aiPronunciationScore.textContent = data.pronunciation_score || '-';
        
        // 更新用户发音详情
        this.userPronunciationScore.textContent = data.user_pronunciation_score || '-';
        
        // 更新下一句练习建议
        this.nextSuggestion.textContent = data.next_suggestion || 'お元気ですか？';
        this.suggestionHiragana.textContent = data.suggestion_hiragana || '暂无平假名';
        this.suggestionTranslation.textContent = data.suggestion_translation || '你好吗？';
        
        // 启用播放按钮
        this.playAiVoice.disabled = false;
        if (this.userAudioBlob) {
            this.playUserVoice.disabled = false;
        }
    }
    
    // 文本转语音功能
    synthesizeSpeech(text) {
        // 使用Web Speech API进行语音合成
        if (this.synth) {
            // 先停止当前正在播放的语音
            this.synth.cancel();
            
            // 创建语音对象
            const utterThis = new SpeechSynthesisUtterance(text);
            utterThis.lang = 'ja-JP'; // 设置为日语发音
            utterThis.rate = 0.8; // 语速稍慢，便于学习
            
            // 播放语音
            this.synth.speak(utterThis);
        } else {
            // 如果Web Speech API不可用，使用后端API
            fetch('/api/text_to_speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                if (data.audio_url) {
                    // 播放合成的语音
                    if (this.audioElement) {
                        this.audioElement.pause();
                    }
                    this.audioElement = new Audio(data.audio_url);
                    this.audioElement.play();
                }
            })
            .catch(error => {
                console.error('语音合成错误:', error);
            });
        }
    }
    
    // 播放用户语音录音
    playUserVoiceRecording() {
        if (this.userAudioBlob) {
            const audioUrl = URL.createObjectURL(this.userAudioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
        }
    }
    
    // 播放AI语音回复
    playAiVoiceResponse() {
        const aiMessage = this.chatHistory.querySelector('.ai-message:last-child p');
        if (aiMessage) {
            const text = aiMessage.textContent;
            this.synthesizeSpeech(text);
        }
    }
    
    toggleRecording() {
        if (!this.isRecording) {
            this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    
    startRecording() {
        this.isRecording = true;
        this.recordButton.classList.add('recording');
        this.recordingIndicator.classList.add('active');
        this.recordStatus.textContent = '录音中...点击停止';
        this.micIcon.textContent = '⏹';
        
        // 使用Web Speech API进行录音
        if (this.recognition) {
            this.recognition.start();
            console.log('开始录音...');
        } else {
            // 如果Web Speech API不可用，使用模拟方式
            console.log('开始录音(模拟)...');
            setTimeout(() => {
                this.recordStatus.textContent = '点击麦克风开始录音';
                // 模拟识别结果
                const recognizedText = 'こんにちは、元気ですか？';
                this.userInput.value = recognizedText;
                this.userRecognizedText.textContent = recognizedText;
                this.stopRecording();
            }, 1500);
        }
    }
    
    stopRecording() {
        this.isRecording = false;
        this.recordButton.classList.remove('recording');
        this.recordingIndicator.classList.remove('active');
        this.recordStatus.textContent = '点击麦克风开始录音';
        this.micIcon.textContent = '🎤';
        
        // 停止Web Speech API录音
        if (this.recognition) {
            this.recognition.stop();
        }
        
        console.log('停止录音...');
    }
    
    selectScenario(scenario) {
        this.currentScenario = scenario;
        
        // 更新UI
        document.querySelectorAll('.scenario-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-scenario="${scenario}"]`).classList.add('active');
        
        // 添加场景提示消息
        let scenarioMessage = '';
        switch(scenario) {
            case 'greeting':
                scenarioMessage = '场景已切换到"问候"。试着用日语打招呼吧！例: こんにちは、おはよう、こんばんは';
                break;
            case 'shopping':
                scenarioMessage = '场景已切换到"购物"。试着用日语询问价格或购买物品吧！例: これはいくらですか？';
                break;
            case 'restaurant':
                scenarioMessage = '场景已切换到"餐厅"。试着用日语点餐吧！例: お水をください。';
                break;
            case 'directions':
                scenarioMessage = '场景已切换到"问路"。试着用日语询问方向吧！例: 駅はどこですか？';
                break;
        }
        
        this.addMessageToHistory(scenarioMessage, 'ai');
    }
    
    addMessageToHistory(content, sender, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');
        
        if (isLoading) {
            messageDiv.innerHTML = `
                <strong>AI助手:</strong>
                <div class="loading"></div>
            `;
        } else {
            messageDiv.innerHTML = content;
        }
        
        this.chatHistory.appendChild(messageDiv);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        
        return messageDiv;
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new SakuraTalk();
});