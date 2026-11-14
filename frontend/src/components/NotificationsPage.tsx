import { useState, useEffect, useCallback } from "react";
import type { Notification } from "../types";
import { ApiError, deleteNotification, listNotifications } from "../services/api";
import NotificationForm from "./NotificationForm";
import NotificationItem from "./NotificationItem";

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

  // Stable reference so memo(NotificationItem) can skip re-renders
  const handleDelete = useCallback(
    async (id: number) => {
      try {
        await deleteNotification(id);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          onLogout();
          return;
        }
        throw err; // the item shows it inside the modal
      }
      setNotifications((prevNotifications) =>
        prevNotifications.filter((notification) => notification.id !== id),
      );
    },
    [onLogout],
  );

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <h2>Notificaciones</h2>
        <div className="header-actions">
          {!showForm && (
            <button onClick={() => setShowForm(true)}>
              + Crear notificación
            </button>
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
          <NotificationItem key={n.id} notification={n} onDelete={handleDelete} />
        ))}
      </ul>
    </div>
  );
};

export default NotificationPage;
