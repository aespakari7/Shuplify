// Shared chat logic for AI_email and AI_ES templates
(function(){
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function escapeAndFormat(text){
        const el = document.createElement('div');
        el.textContent = text;
        return el.innerHTML.replace(/\n/g,'<br>');
    }

    function appendMessage(chatWindow, type, text, name){
        const wrapper = document.createElement('div');
        wrapper.className = 'message ' + (type === 'user' ? 'user' : 'bot');

        if(type === 'bot'){
            const avatar = document.createElement('div');
            avatar.className = 'avatar bot';
            avatar.textContent = (name && name[0]) || 'G';
            const inner = document.createElement('div');
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = escapeAndFormat(text);
            const meta = document.createElement('div');
            meta.className = 'meta';
            meta.textContent = name || 'Gemini';
            inner.appendChild(bubble);
            inner.appendChild(meta);
            wrapper.appendChild(avatar);
            wrapper.appendChild(inner);
        } else {
            const inner = document.createElement('div');
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = text;
            const meta = document.createElement('div');
            meta.className = 'meta';
            meta.textContent = 'あなた';
            inner.appendChild(bubble);
            inner.appendChild(meta);
            wrapper.appendChild(inner);
        }

        chatWindow.appendChild(wrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function setupChat(options){
        // options: {chatWindowId, inputId, buttonId, endpoint, botName}
        const chatWindow = document.getElementById(options.chatWindowId);
        const userInput = document.getElementById(options.inputId);
        const sendButton = document.getElementById(options.buttonId);
        const endpoint = options.endpoint;
        const botName = options.botName || 'Gemini';

        if(!chatWindow || !userInput || !sendButton) return;

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e){ if(e.key === 'Enter') sendMessage(); });

        function sendMessage(){
            const message = userInput.value.trim();
            if(!message) return;
            appendMessage(chatWindow, 'user', message);
            userInput.value = '';

            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({ message: message })
            })
            .then(resp => resp.json())
            .then(data => {
                if(data.response){
                    appendMessage(chatWindow, 'bot', data.response, botName);
                } else {
                    appendMessage(chatWindow, 'bot', 'エラー: AIからの応答がありませんでした。', 'System');
                }
            })
            .catch(err => {
                console.error('通信エラー:', err);
                appendMessage(chatWindow, 'bot', 'エラーが発生しました: ' + (err.message || '接続に失敗しました'), 'System');
            });
        }
    }

    window.AIChat = { setupChat };
})();
