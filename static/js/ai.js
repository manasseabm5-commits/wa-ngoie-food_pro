// Script client pour l'interface ABM AI
// - Envoie les messages au endpoint local /ai/message
// - Reçoit du texte brut (text/plain) et l'affiche dans la fenêtre de chat
// - Adapté pour fonctionner sans JSON, sans API externe

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const chat = document.getElementById('chat');
    const tplUser = document.getElementById('tpl-user').innerHTML;
    const tplAI = document.getElementById('tpl-ai').innerHTML;

    // Ajoute un message dans la fenêtre (texte déjà échappé/formaté)
    function appendMessage(htmlTemplate) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = htmlTemplate;
        chat.appendChild(wrapper);
        chat.scrollTop = chat.scrollHeight - chat.clientHeight + 50;
    }

    // Ajoute une bulle utilisateur
    function appendUser(text) {
        const safe = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
        appendMessage(tplUser.replace('{TEXT}', safe));
    }

    // Ajoute une bulle AI
    function appendAI(text) {
        const safe = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
        appendMessage(tplAI.replace('{TEXT}', safe));
    }

    // Affiche un indicateur de frappe simple
    function showTyping() {
        const id = 'typing-indicator';
        if (document.getElementById(id)) return;
        const el = document.createElement('div');
        el.id = id;
        el.className = 'd-flex mb-3';
        el.innerHTML = '<div class="me-auto text-start"><div class="bubble ai"> <span class="typing">...</span></div><small class="text-muted d-block mt-1">ABM AI</small></div>';
        chat.appendChild(el);
        chat.scrollTop = chat.scrollHeight;
    }

    function hideTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    // Envoie le message au serveur (text/plain attendu)
    async function sendMessage(text) {
        try {
            showTyping();
            const fd = new FormData();
            fd.append('message', text);
            const resp = await fetch('/ai/message', { method: 'POST', body: fd });
            const data = await resp.text();
            hideTyping();
            appendAI(data);
        } catch (err) {
            hideTyping();
            appendAI('Erreur : impossible de joindre l\'assistant local.');
            console.error(err);
        }
    }

    // Gestion du submit
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        appendUser(text);
        input.value = '';
        sendMessage(text);
    });

    // Initialisation : demande de salutation (message vide) pour récupérer la réponse par défaut adaptée au rôle
    (function initialGreeting() {
        showTyping();
        fetch('/ai/message', { method: 'POST', body: new FormData() })
            .then(r => r.text())
            .then(t => {
                hideTyping();
                appendAI(t);
            })
            .catch(err => {
                hideTyping();
                appendAI('Impossible d\'obtenir la salutation de l\'assistant.');
                console.error(err);
            });
    })();

});
