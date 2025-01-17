class Logger {
    constructor(config) {
        this.parseUrl = config.parseUrl;
        this.csrfToken = config.csrfToken;
        this.typingTimer = null;
        this.doneTypingInterval = 300;
        
        this.initializeEventListeners();
        this.loadStoredText();
    }

    initializeEventListeners() {
        $('#inputArea').on('input', () => {
            clearTimeout(this.typingTimer);
            this.typingTimer = setTimeout(() => this.parseText(), this.doneTypingInterval);
            // Save text on every input
            this.saveCurrentText();
        });
    }

    saveCurrentText() {
        const currentText = $('#inputArea').val();
        const currentAdif = $('#adifOutput').text();
        sessionStorage.setItem('qsoInputText', currentText);
        sessionStorage.setItem('qsoAdifOutput', currentAdif);
    }

    loadStoredText() {
        const storedText = sessionStorage.getItem('qsoInputText');
        const storedAdif = sessionStorage.getItem('qsoAdifOutput');
        
        if (storedText) {
            $('#inputArea').val(storedText);
        }
        if (storedAdif) {
            $('#adifOutput').text(storedAdif);
        }
        
        // If we have text but no ADIF (e.g., after page refresh), parse it again
        if (storedText && !storedAdif) {
            this.parseText();
        }
    }

    parseText() {
        const text = $('#inputArea').val();
        if (text === '') {
            $('#adifOutput').text('');
            this.saveCurrentText();
            return;
        }
        
        $.ajax({
            url: this.parseUrl,
            type: 'POST',
            data: {
                'text': text,
                'csrfmiddlewaretoken': this.csrfToken
            },
            success: (response) => {
                if (response.adif) {
                    $('#adifOutput').text(response.adif);
                    this.saveCurrentText();
                } else if (response.error) {
                    console.error('Error:', response.error);
                }
            },
            error: (xhr, status, error) => {
                console.error('Error:', error);
                $('#adifOutput').text('Error parsing input');
            }
        });
    }
} 