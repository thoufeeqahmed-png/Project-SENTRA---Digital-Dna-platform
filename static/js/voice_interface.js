/**
 * PROJECT DNA MATRIX - VOICE INTERFACE & AUDIO SYNTHESIS
 * Integrates Web Speech API (Speech Recognition & Speech Synthesis)
 * Features calm, intelligent audio personality and live wave visualizer.
 */

class VoiceInterface {
  constructor(options = {}) {
    this.onTranscript = options.onTranscript || (() => {});
    this.onStatusChange = options.onStatusChange || (() => {});
    this.isListening = false;
    this.voiceOutputEnabled = true;

    // Speech Recognition setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.onStatusChange({ isListening: true });
        this.startWaveAnimation();
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.onTranscript(transcript);
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        this.stopListening();
      };

      this.recognition.onend = () => {
        this.stopListening();
      };
    } else {
      console.warn('Web Speech API recognition is not supported in this browser.');
      this.recognition = null;
    }

    // Synthesis setup
    this.synth = window.speechSynthesis;
    this.preferredVoice = null;
    this.loadVoices();
    if (this.synth && this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = () => this.loadVoices();
    }

    // Canvas visualizer
    this.waveCanvas = options.waveCanvas || null;
    this.waveCtx = this.waveCanvas ? this.waveCanvas.getContext('2d') : null;
    this.waveAnimId = null;
    this.wavePhase = 0;
  }

  loadVoices() {
    if (!this.synth) return;
    const voices = this.synth.getVoices();
    // Seek a calm, natural English voice (Google US English, Samantha, Daniel, or Natural)
    this.preferredVoice = voices.find(v => 
      v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Daniel') || v.name.includes('Samantha'))
    ) || voices.find(v => v.lang.startsWith('en')) || voices[0];
  }

  toggleListening() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  startListening() {
    if (!this.recognition) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome, Edge, or Safari.');
      return;
    }
    try {
      this.recognition.start();
    } catch (e) {
      console.error('Recognition start error:', e);
    }
  }

  stopListening() {
    this.isListening = false;
    this.onStatusChange({ isListening: false });
    this.stopWaveAnimation();
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
  }

  speak(text) {
    if (!this.voiceOutputEnabled || !this.synth || !text) return;
    this.synth.cancel(); // Stop any pending speech

    // Clean text of markdown or special symbols for clean audio readout
    const cleanText = text
      .replace(/[*#`_~[\]()]/g, '')
      .replace(/https?:\/\/\S+/g, '')
      .replace(/\s+/g, ' ')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    if (this.preferredVoice) {
      utterance.voice = this.preferredVoice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 0.95; // Calm, intelligent slightly lower resonance

    utterance.onstart = () => {
      this.startWaveAnimation();
    };
    utterance.onend = () => {
      this.stopWaveAnimation();
    };
    utterance.onerror = () => {
      this.stopWaveAnimation();
    };

    this.synth.speak(utterance);
  }

  startWaveAnimation() {
    if (!this.waveCanvas || !this.waveCtx) return;
    if (this.waveAnimId) cancelAnimationFrame(this.waveAnimId);

    const render = () => {
      this.wavePhase += 0.1;
      const ctx = this.waveCtx;
      const w = this.waveCanvas.width;
      const h = this.waveCanvas.height;

      ctx.clearRect(0, 0, w, h);
      ctx.beginPath();
      ctx.strokeStyle = "#00f0ff";
      ctx.lineWidth = 2;

      for (let x = 0; x < w; x++) {
        const y = h / 2 + Math.sin(x * 0.08 + this.wavePhase) * (h * 0.35) * Math.sin(x / w * Math.PI);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      this.waveAnimId = requestAnimationFrame(render);
    };
    this.waveAnimId = requestAnimationFrame(render);
  }

  stopWaveAnimation() {
    if (this.waveAnimId) {
      cancelAnimationFrame(this.waveAnimId);
      this.waveAnimId = null;
    }
    if (this.waveCtx && this.waveCanvas) {
      this.waveCtx.clearRect(0, 0, this.waveCanvas.width, this.waveCanvas.height);
      // Draw quiet idle line
      this.waveCtx.beginPath();
      this.waveCtx.strokeStyle = "rgba(100, 116, 139, 0.4)";
      this.waveCtx.lineWidth = 1;
      this.waveCtx.moveTo(0, this.waveCanvas.height / 2);
      this.waveCtx.lineTo(this.waveCanvas.width, this.waveCanvas.height / 2);
      this.waveCtx.stroke();
    }
  }
}

window.VoiceInterface = VoiceInterface;
