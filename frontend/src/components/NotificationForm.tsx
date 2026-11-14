import { useState, type FormEvent } from "react";
import type { Notification, NotificationCreate } from "../types";
import { ApiError, createNotification } from "../services/api";

interface Props {
  onCreated: (notification: Notification) => void;
  onCancel: () => void;
  onUnauthorized: () => void;
}

const CHANNELS = [
  { value: "sms", label: "SMS", placeholder: "+5491112345678" },
  { value: "email", label: "Email", placeholder: "ejemplo@correo.com" },
  { value: "push", label: "Push", placeholder: "Token del dispositivo" },
];

const EMPTY_FORM: NotificationCreate = {
  title: "",
  content: "",
  channel: "sms",
  recipient: "",
};

const NotificationForm = ({ onCreated, onCancel, onUnauthorized }: Props) => {
  const [form, setForm] = useState<NotificationCreate>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const setField = (field: keyof NotificationCreate, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const data = {
      title: form.title.trim(),
      content: form.content.trim(),
      channel: form.channel,
      recipient: form.recipient.trim(),
    };
    if (!data.title || !data.content || !data.recipient) {
      setError("Completá todos los campos.");
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const created = await createNotification(data);
      onCreated(created);
      setForm(EMPTY_FORM);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        onUnauthorized();
        return;
      }
      // Channel rules (phone format, SMS length, etc.) are validated by the backend
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setSaving(false);
    }
  };

  const placeholder = CHANNELS.find((c) => c.value === form.channel)?.placeholder;

  return (
    <form onSubmit={handleSubmit} className="notification-form">
      <h3>Nueva notificación</h3>

      {error && <p className="error-message">{error}</p>}

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="channel">Canal</label>
          <select
            id="channel"
            value={form.channel}
            onChange={(e) => setField("channel", e.target.value)}
          >
            {CHANNELS.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group grow">
          <label htmlFor="recipient">Destinatario</label>
          <input
            id="recipient"
            value={form.recipient}
            onChange={(e) => setField("recipient", e.target.value)}
            placeholder={placeholder}
            maxLength={250}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="title">Título</label>
        <input
          id="title"
          value={form.title}
          onChange={(e) => setField("title", e.target.value)}
          maxLength={60}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="content">
          Contenido <span className="hint">{form.content.length}/250</span>
        </label>
        <textarea
          id="content"
          value={form.content}
          onChange={(e) => setField("content", e.target.value)}
          maxLength={250}
          rows={3}
          required
        />
      </div>

      <div className="form-actions">
        <button type="button" className="secondary" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" disabled={saving}>
          {saving ? "Creando..." : "Crear"}
        </button>
      </div>
    </form>
  );
};

export default NotificationForm;
