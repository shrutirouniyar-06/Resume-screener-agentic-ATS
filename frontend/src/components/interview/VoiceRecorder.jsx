import { useState, useRef, useEffect } from "react";
import "./VoiceRecorder.css";

export default function VoiceRecorder({ questionIndex, candidateId, onComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [communicationScore, setCommunicationScore] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = async () => {
    try {
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert(
          "Your browser does not support audio recording. Please use Chrome, Firefox, or Edge."
        );
        return;
      }

      // Request microphone permission with proper constraints
      const constraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((track) => {
          track.stop();
        });
      };

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((t) => t + 1);
      }, 1000);
    } catch (error) {
      if (error.name === "NotAllowedError") {
        alert(
          "Microphone permission denied. Please check your browser settings and allow microphone access.\n\nSteps:\n1. Click the camera icon in the address bar\n2. Enable 'Microphone'\n3. Reload the page and try again"
        );
      } else if (error.name === "NotFoundError") {
        alert(
          "No microphone found. Please connect a microphone to your computer."
        );
      } else {
        alert("Recording error: " + error.message);
      }
      console.error("Recording error:", error);
    }
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.stop();
    clearInterval(timerRef.current);
    setIsRecording(false);

    // Process audio after recording stops
    setTimeout(async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      await processAudio(audioBlob);
    }, 500);
  };

  const processAudio = async (audioBlob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      // Use webm extension since modern browsers record in webm format
      const filename = `response.${audioBlob.type.split("/")[1] || "webm"}`;
      formData.append("audio", audioBlob, filename);
      formData.append("question_id", questionIndex);

      const response = await fetch(
        `http://localhost:5000/api/candidates/${candidateId}/voice-interview`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `Server error: ${response.status}`);
      }

      const data = await response.json();

      setTranscript(data.transcript);
      setCommunicationScore(data.communication_score);
      setMetrics(data.metrics);

      if (onComplete) {
        onComplete({
          transcript: data.transcript,
          score: data.communication_score,
          metrics: data.metrics,
        });
      }
    } catch (error) {
      alert("Failed to process audio: " + error.message);
      console.error(error);
      setIsRecording(false);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="voice-recorder">
      {/* Recording Controls */}
      <div className="recorder-controls">
        {!transcript ? (
          <>
            <button
              className={`record-btn ${isRecording ? "recording" : ""}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={loading}
            >
              {isRecording ? (
                <>
                  <span className="record-icon">⏹</span> Stop Recording
                </>
              ) : (
                <>
                  <span className="record-icon">🎤</span> Start Recording
                </>
              )}
            </button>

            {isRecording && (
              <div className="recording-time">
                <span className="pulse-dot"></span>
                {formatTime(recordingTime)}
              </div>
            )}

            {loading && <div className="loader">Processing audio...</div>}
          </>
        ) : (
          <div className="score-display">
            <div className="score-main">
              <div className="communication-badge">
                <div className="score-number">{communicationScore}</div>
                <div className="score-label">Communication</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Transcript Display */}
      {transcript && (
        <div className="transcript-section">
          <div className="section-title">Transcript</div>
          <div className="transcript-text">{transcript}</div>
        </div>
      )}

      {/* Metrics Display */}
      {metrics && (
        <div className="metrics-section">
          <div className="section-title">Communication Analysis</div>

          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-name">Clarity</div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{ width: `${metrics.clarity}%` }}
                ></div>
              </div>
              <div className="metric-value">{metrics.clarity}/100</div>
            </div>

            <div className="metric-card">
              <div className="metric-name">Confidence</div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{ width: `${metrics.confidence}%` }}
                ></div>
              </div>
              <div className="metric-value">{metrics.confidence}/100</div>
            </div>

            <div className="metric-card">
              <div className="metric-name">Relevance</div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{ width: `${metrics.relevance}%` }}
                ></div>
              </div>
              <div className="metric-value">{metrics.relevance}/100</div>
            </div>

            <div className="metric-card">
              <div className="metric-name">Speaking Pace</div>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{ width: `${metrics.speaking_pace}%` }}
                ></div>
              </div>
              <div className="metric-value">{metrics.speaking_pace}/100</div>
            </div>
          </div>

          {metrics.analysis && (
            <div className="analysis-note">{metrics.analysis}</div>
          )}
        </div>
      )}

      {/* Reset Button */}
      {transcript && (
        <button
          className="btn btn-secondary"
          onClick={() => {
            setTranscript("");
            setCommunicationScore(null);
            setMetrics(null);
            audioChunksRef.current = [];
          }}
        >
          Record Again
        </button>
      )}
    </div>
  );
}
