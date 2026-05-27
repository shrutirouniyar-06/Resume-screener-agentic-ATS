import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
} from "recharts";
import VoiceRecorder from "../../components/interview/VoiceRecorder";
import "./InterviewPage.css";

export default function InterviewPage() {
  const { id } = useParams();

  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ratings, setRatings] = useState({});
  const [activeTab, setActiveTab] = useState("text");
  const [voiceInterviews, setVoiceInterviews] = useState({});

  useEffect(() => {
    load();
  }, [id]);

  async function load() {
    try {
      const r = await fetch(`http://localhost:5000/api/candidates/${id}`);

      const data = await r.json();

      setCandidate(data);

      // LOAD SAVED RATINGS

      const saved = {};

      Object.entries(data.interview_profile || {}).forEach(
        ([comp, questions]) => {
          Object.entries(questions).forEach(([qid, score]) => {
            saved[`${qid}-${comp}`] = score;
          });
        },
      );

      setRatings(saved);

      // LOAD VOICE INTERVIEWS

      try {
        const voiceRes = await fetch(
          `http://localhost:5000/api/candidates/${id}/voice-interviews`
        );
        if (voiceRes.ok) {
          const voiceData = await voiceRes.json();
          const voiceMap = {};
          voiceData.voice_interviews.forEach((vi) => {
            voiceMap[vi.question_id] = vi;
          });
          setVoiceInterviews(voiceMap);
        }
      } catch (e) {
        console.log("No voice interviews yet");
      }
    } finally {
      setLoading(false);
    }
  }

  // AGGREGATE

  const competencyScores = {};

  Object.entries(ratings).forEach(([key, value]) => {
    const comp = key.split("-").slice(1).join("-");

    if (!competencyScores[comp]) {
      competencyScores[comp] = [];
    }

    competencyScores[comp].push(value * 20);
  });

  const radarData = Object.entries(competencyScores).map(([k, vals]) => ({
    competency: k.replaceAll("_", " "),

    score: Math.round(vals.reduce((a, b) => a + b, 0) / vals.length),
  }));

  if (loading) {
    return <div className="center-fill">Loading interview...</div>;
  }

  if (!candidate) {
    return <div className="center-fill">Candidate not found</div>;
  }

  return (
    <div className="interview-page">
      <div className="interview-header">
        <div>
          <div className="interview-name">{candidate.name}</div>

          <div className="interview-role">{candidate.role_title}</div>
        </div>

        <div className="interview-score">
          Resume Score {candidate.score?.overall}
        </div>
      </div>

      <div className="interview-tabs">
        <button
          className={`tab-btn ${activeTab === "text" ? "active" : ""}`}
          onClick={() => setActiveTab("text")}
        >
          Interview
        </button>
        <button
          className={`tab-btn voice-tab ${activeTab === "voice" ? "active" : ""}`}
          onClick={() => setActiveTab("voice")}
        >
          <span className="voice-icon">🎤</span> Voice Interview
        </button>
      </div>

      <div className="interview-layout">
        {/* LEFT */}

        <div className="interview-main">
          {activeTab === "text" && candidate.interview_questions?.map((q, i) => (
            <div key={i} className="question-card">
              <div className="question-type">{q.type}</div>

              <div className="question-text">{q.question}</div>

              {q.follow_up && (
                <div className="question-followup">↳ {q.follow_up}</div>
              )}

              <div className="competency-row">
                {q.competencies?.map((c) => (
                  <span key={c} className="competency-chip">
                    {c.replaceAll("_", " ")}
                  </span>
                ))}
              </div>

              {/* RATINGS */}

              <div className="rating-block">
                {q.competencies?.map((comp) => (
                  <div key={comp} className="rating-row">
                    <div className="rating-label">
                      {comp.replaceAll("_", " ")}
                    </div>

                    <div className="stars">
                      {[1, 2, 3, 4, 5].map((star) => {
                        const value = ratings[`${i}-${comp}`] || 0;

                        return (
                          <span
                            key={star}
                            className={star <= value ? "star active" : "star"}
                            onClick={async () => {
                              setRatings((prev) => ({
                                ...prev,
                                [`${i}-${comp}`]: star,
                              }));

                              await fetch(
                                `http://localhost:5000/api/candidates/${id}/interview-rating`,
                                {
                                  method: "POST",
                                  headers: {
                                    "Content-Type": "application/json",
                                  },
                                  body: JSON.stringify({
                                    question_id: i,
                                    competency: comp,
                                    score: star,
                                  }),
                                },
                              );
                            }}
                          >
                            ★
                          </span>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {activeTab === "voice" && candidate.interview_questions?.map((q, i) => (
            <div key={i} className="question-card">
              <div className="question-type">{q.type}</div>

              <div className="question-text">{q.question}</div>

              {q.follow_up && (
                <div className="question-followup">↳ {q.follow_up}</div>
              )}

              <div className="competency-row">
                {q.competencies?.map((c) => (
                  <span key={c} className="competency-chip">
                    {c.replaceAll("_", " ")}
                  </span>
                ))}
              </div>

              {voiceInterviews[i] ? (
                <div className="voice-response-existing">
                  <div className="response-badge">✓ Recorded</div>
                  <div className="response-score">
                    Score: <strong>{voiceInterviews[i].communication_score}</strong>
                  </div>
                </div>
              ) : (
                <VoiceRecorder
                  questionIndex={i}
                  candidateId={id}
                  onComplete={() => load()}
                />
              )}
            </div>
          ))}
        </div>

        {/* RIGHT */}

        <div className="profile-panel">
          <div className="profile-title">Candidate Profile</div>

          <div className="profile-sub">Live interview competency map</div>

          <div className="radar-wrap">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid />

                  <PolarAngleAxis dataKey="competency" />

                  <Radar
                    dataKey="score"
                    stroke="#185FA5"
                    fill="#185FA5"
                    fillOpacity={0.45}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-radar">
                Rate questions to generate profile
              </div>
            )}
          </div>

          <div className="profile-breakdown">
            {radarData.map((r) => (
              <div key={r.competency} className="profile-row">
                <span>{r.competency}</span>

                <strong>{r.score}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
