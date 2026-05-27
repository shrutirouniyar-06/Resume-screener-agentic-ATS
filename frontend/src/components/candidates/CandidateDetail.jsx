import { ScoreRing, Badge } from '../layout/UI';
import './CandidateDetail.css';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function CandidateDetail({ candidate: c }) {
  const navigate = useNavigate();
  const [voiceProfile, setVoiceProfile] = useState(null);

  useEffect(() => {
    loadVoiceProfile();
  }, [c.id]);

  const loadVoiceProfile = async () => {
    try {
      const res = await fetch(
        `http://localhost:5000/api/candidates/${c.id}/voice-interviews`
      );
      if (res.ok) {
        const data = await res.json();
        setVoiceProfile(data.voice_profile);
      }
    } catch (e) {
      console.log("No voice profile yet");
    }
  };

  const score = c.score || {};
  const analysis = c.analysis || {};
  const questions = c.interview_questions || [];
  const rejection = c.rejection_feedback;

  return (
    <div className="detail-wrap">

      <div className="detail-header">
        <div>
          <div className="detail-name">{c.name}</div>
          <div className="detail-role">
            {c.role_title} · {analysis.years_experience ?? '?'} yrs exp
          </div>
        </div>

        <Badge status={c.status} />
      </div>

      <div className="detail-rings">
        <ScoreRing
          value={score.overall ?? 0}
          label="Overall"
          color="#185FA5"
        />

        <ScoreRing
          value={score.skills ?? 0}
          label="Skills"
          color="#1D9E75"
        />

        <ScoreRing
          value={score.experience ?? 0}
          label="Experience"
          color="#BA7517"
        />

        {voiceProfile && (
          <ScoreRing
            value={voiceProfile.communication_score ?? 0}
            label="Communication"
            color="#D97706"
          />
        )}
      </div>

      {analysis.skills_found?.length > 0 && (
        <div className="detail-section">
          <div className="detail-sec-title">
            Matched skills
          </div>

          <div className="skill-tags">
            {analysis.skills_found.map(s => (
              <span
                key={s}
                className="skill-tag"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {c.recruiter_summary && (
        <div className="detail-section">
          <div className="detail-sec-title">
            Recruiter summary
          </div>

          <div className="detail-summary">
            {c.recruiter_summary}
          </div>
        </div>
      )}

      {questions.length > 0 && (
        <div className="detail-section">

          <div className="detail-sec-title-row">
            <span className="detail-sec-title">
              Interview questions
            </span>

            <span className="detail-count">
              {questions.length} generated
            </span>
          </div>

          {questions.slice(0, 3).map((q, i) => (
            <div
              key={i}
              className="q-card"
            >
              <div className="q-type">
                {q.type} · {q.category}
              </div>

              <div className="q-text">
                {q.question}
              </div>

              {q.follow_up && (
                <div className="q-followup">
                  ↳ {q.follow_up}
                </div>
              )}
            </div>
          ))}

          {questions.length > 3 && (
            <div className="q-more">
              +{questions.length - 3} more questions
            </div>
          )}

          {/* NEW BUTTON */}

          <div style={{ marginTop: '12px' }}>
            <button
              className="btn btn-primary"
              onClick={() =>
                navigate(
                  `/candidates/${c.id}/interview`
                )
              }
            >
              Start Interview
            </button>
          </div>

        </div>
      )}

      {voiceProfile && (
        <div className="detail-section">
          <div className="detail-sec-title">
            Voice Interview Profile
          </div>

          <div className="voice-metrics">
            <div className="metric-item">
              <span className="metric-label">Clarity</span>
              <span className="metric-value">{voiceProfile.clarity}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Confidence</span>
              <span className="metric-value">{voiceProfile.confidence}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Relevance</span>
              <span className="metric-value">{voiceProfile.relevance}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Speaking Pace</span>
              <span className="metric-value">{voiceProfile.speaking_pace}</span>
            </div>
          </div>
        </div>
      )}

      {rejection && (
        <div className="detail-section">

          <div className="detail-sec-title">
            Feedback for candidate
            {!!c.malware_detected && (
              <span style={{ color:'#DC2626', marginLeft:'12px', fontSize:'12px', fontWeight:'600' }}>
                ⚠️ MALICIOUS ACTIVITY DETECTED
              </span>
            )}
          </div>

          {!!c.malware_detected && c.malware_feedback && (
            <div style={{
              backgroundColor:'#FEE2E2',
              border:'1px solid #FCA5A5',
              borderRadius:'6px',
              padding:'12px',
              marginBottom:'16px',
              color:'#DC2626',
              fontSize:'13px',
              lineHeight:'1.6'
            }}>
              <div style={{ fontWeight:'600', marginBottom:'8px' }}>
                🚨 {c.malware_feedback.what_is_this}
              </div>
              <div style={{ marginBottom:'8px' }}>
                <strong>Why this is dangerous:</strong>
                <ul style={{ marginTop:'4px', marginLeft:'16px', marginBottom:0 }}>
                  {c.malware_feedback.why_malicious?.map((reason, i) => (
                    <li key={i} style={{ marginBottom:'4px' }}>{reason}</li>
                  ))}
                </ul>
              </div>
              <div style={{ marginBottom:'8px' }}>
                <strong>Attack method:</strong> {c.malware_feedback.attack_method}
              </div>
              <div style={{ marginTop:'8px', padding:'8px', backgroundColor:'#FECACA', borderRadius:'4px', fontSize:'12px' }}>
                <strong>Security Impact:</strong> {c.malware_feedback.security_impact}
              </div>
            </div>
          )}

          <div className="rejection-reason">
            {rejection.reason}
          </div>

          {rejection.improvement_suggestions?.length > 0 && (
            <ul className="improvement-list">
              {rejection.improvement_suggestions.map(
                (s, i) => (
                  <li key={i}>
                    {s}
                  </li>
                )
              )}
            </ul>
          )}
        </div>
      )}

    </div>
  );
}