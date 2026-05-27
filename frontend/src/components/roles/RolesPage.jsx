import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getRoles,
  createRole,
  deleteRole,
  autoGenerateRole,
} from "../../lib/api";
import { Badge, EmptyState, Spinner } from "../layout/UI";
import { Plus, Trash2, Settings, BriefcaseBusiness } from "lucide-react";
import "./RolesPage.css";

export default function RolesPage() {
  const navigate = useNavigate();
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    department: "",
    description: "",
  });
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [validationError, setValidationError] = useState("");

  const load = () =>
    getRoles().then((r) => {
      setRoles(r);
      setLoading(false);
    });
  useEffect(() => {
    load();
  }, []);

  const validateForm = () => {
    setValidationError("");

    if (!form.title.trim()) {
      setValidationError("Role title is required");
      return false;
    }

    if (form.title.trim().length < 3) {
      setValidationError("Role title must be at least 3 characters");
      return false;
    }

    if (form.title.trim().length > 100) {
      setValidationError("Role title must be 100 characters or less");
      return false;
    }

    if (form.department.trim().length > 50) {
      setValidationError("Department must be 50 characters or less");
      return false;
    }

    if (form.description.trim().length > 500) {
      setValidationError("Description must be 500 characters or less");
      return false;
    }

    return true;
  };

  const handleCreate = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setSaving(true);
    try {
      await createRole(form);
      setForm({ title: "", department: "", description: "" });
      setShowForm(false);
      load();
    } catch (err) {
      setValidationError(err.response?.data?.error || "Failed to create role");
    } finally {
      setSaving(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!form.title.trim()) {
      alert("Enter role title first");
      return;
    }

    try {
      setGenerating(true);

      // 1 Generate config
      const generated = await autoGenerateRole(form.title);

      // 2 Create role
      const role = await createRole({
        title: form.title,
        department: form.department,
        description: generated.description,
      });

      // 3 Save scoring config
      await fetch(`http://localhost:5000/api/roles/${role.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...role,
          description: generated.description,
          scoring_config: {
            ...role.scoring_config,
            skills: generated.skills,
            experience_band: generated.experience_band,
            threshold: generated.threshold,
          },
        }),
      });

      load();

      navigate(`/roles/${role.id}/scoring`);
    } catch (e) {
      alert("AI generation failed");
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this role?")) return;
    await deleteRole(id);
    load();
  };

  if (loading)
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "60vh",
        }}
      >
        <Spinner />
      </div>
    );

  return (
    <div className="page">
      <div className="topbar">
        <div className="page-title">Job roles</div>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          <Plus size={14} /> New role
        </button>
      </div>
      <div className="content">
        {showForm && (
          <div className="role-form-card">
            <div className="form-title">Create new role</div>
            {validationError && (
              <div className="form-error">
                <span>{validationError}</span>
              </div>
            )}
            <form onSubmit={handleCreate} className="role-form">
              <div className="form-row">
                <label>Role title</label>
                <input
                  required
                  placeholder="e.g. Senior ML Engineer"
                  value={form.title}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, title: e.target.value }))
                  }
                />
              </div>
              <div className="form-row">
                <label>Department</label>
                <input
                  placeholder="e.g. Engineering"
                  value={form.department}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, department: e.target.value }))
                  }
                />
              </div>
              <div className="form-row">
                <label>Description</label>
                <textarea
                  rows={3}
                  placeholder="Brief role description…"
                  value={form.description}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, description: e.target.value }))
                  }
                />
              </div>
              <div className="form-actions">
                <button
                  type="button"
                  className="btn"
                  disabled={generating}
                  onClick={handleAIGenerate}
                >
                  {generating ? "Generating…" : "AI Generate"}
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? "Creating…" : "Create role"}
                </button>

                <button
                  type="button"
                  className="btn"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {roles.length === 0 && !showForm ? (
          <EmptyState
            icon={<BriefcaseBusiness size={32} />}
            title="No roles yet"
            desc="Create a job role to start screening resumes"
            action={
              <button
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
              >
                <Plus size={14} /> Create role
              </button>
            }
          />
        ) : (
          <div className="roles-grid">
            {roles.map((r) => (
              <div key={r.id} className="role-card">
                <div className="role-card-header">
                  <div>
                    <div className="role-title">{r.title}</div>
                    <div className="role-dept">{r.department || "—"}</div>
                  </div>
                  <Badge
                    status={
                      r.scoring_config?.skills?.length > 0 ? "Active" : "Draft"
                    }
                  />
                </div>
                {r.description && (
                  <div className="role-desc">{r.description}</div>
                )}
                <div className="role-skills">
                  {(r.scoring_config?.skills || []).slice(0, 5).map((s) => (
                    <span key={s.name} className="skill-tag">
                      {s.name}
                    </span>
                  ))}
                  {(r.scoring_config?.skills || []).length > 5 && (
                    <span className="skill-tag">
                      +{r.scoring_config.skills.length - 5} more
                    </span>
                  )}
                  {(r.scoring_config?.skills || []).length === 0 && (
                    <span style={{ fontSize: 11, color: "#aaa" }}>
                      No skills configured yet
                    </span>
                  )}
                </div>
                <div className="role-meta">
                  <span>Threshold: {r.scoring_config?.threshold ?? 75}%</span>
                  <span>
                    Updated {new Date(r.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="role-actions">
                  <button
                    className="btn"
                    onClick={() => navigate(`/roles/${r.id}/scoring`)}
                  >
                    <Settings size={13} /> Configure scoring
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(r.id)}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
