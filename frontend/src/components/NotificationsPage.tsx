import { useState, useEffect } from "react";
import type { Notification } from "../types";
import { ApiError, listNotifications } from "../services/api";
import NotificationForm from "./NotificationForm";

interface Props {
  onLogout: () => void;
}

const NotificationPage = ({ onLogout }: Props) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // List comes newest first, so prepend
  const handleCreated = (created: Notification) => {
    setNotifications((prev) => [created, ...prev]);
    setShowForm(false);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await listNotifications();
        setNotifications(data);
      } catch (err) {
        // Expired token: storage is already cleared, sync App state too
        if (err instanceof ApiError && err.status === 401) {
          onLogout();
          return;
        }
        setError(err instanceof Error ? err.message : "Unexpected error");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [onLogout]);

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <h2>Notificaciones</h2>
        <div className="header-actions">
          {!showForm && (
            <button onClick={() => setShowForm(true)}>+ Crear notificación</button>
          )}
          <button className="secondary" onClick={onLogout}>
            Cerrar sesión
          </button>
        </div>
      </div>

      {showForm && (
        <NotificationForm
          onCreated={handleCreated}
          onCancel={() => setShowForm(false)}
          onUnauthorized={onLogout}
        />
      )}

      {loading && <p>Cargando...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && notifications.length === 0 && (
        <p className="empty">No hay notificaciones.</p>
      )}

      <ul className="notifications-list">
        {notifications.map((n) => (
          <li key={n.id} className="notification-item">
            <div className="notification-top">
              <strong>{n.title}</strong>
              <span className="badge">{n.channel}</span>
              <span className={`badge status-${n.status}`}>{n.status}</span>
            </div>
            <div>{n.content}</div>
            <div className="notification-meta">
              Para: {n.recipient} · {new Date(n.created_at).toLocaleString()}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NotificationPage;
