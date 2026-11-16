import { useState, useEffect, useCallback, useMemo } from "react";
import type { Notification } from "../types";
import {
  ApiError,
  deleteNotification,
  listNotifications,
} from "../services/api";
import NotificationForm from "./NotificationForm";
import NotificationItem from "./NotificationItem";
import { useDebounce } from "../hooks/useDebounce";

interface Props {
  onLogout: () => void;
}

const NotificationPage = ({ onLogout }: Props) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [statusFilter, setStatusFilter] = useState<
    "all" | Notification["status"]
  >("all");
  const [searchInput, setSearchInput] = useState("");

  // Filter only after typing pauses, and ignore terms shorter than 2 chars.
  // `search` is derived (not state): it's recomputed from searchInput each render.
  const debouncedSearch = useDebounce(searchInput.trim(), 300);
  const search = debouncedSearch.length >= 2 ? debouncedSearch : "";

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

  // useMemo caches a computed value; it reruns only when a dependency changes.
  // Deps must be exactly the data the calculation reads.
  const filtered = useMemo(() => {
    return notifications.filter((noti) => {
      const textMatch =
        noti.title.toLowerCase().includes(search.toLowerCase()) ||
        noti.recipient.toLowerCase().includes(search.toLowerCase());

      const statusMatch =
        statusFilter === "all" || noti.status === statusFilter;

      return textMatch && statusMatch;
    });
  }, [notifications, search, statusFilter]);

  // Separate useMemo: reads only notifications, so searching or filtering doesn't recount
  const counts = useMemo(() => {
    return notifications.reduce(
      (acc, noti) => {
        acc.total += 1;

        if (noti.status === "pending") acc.pending += 1;
        if (noti.status === "sent") acc.sent += 1;
        if (noti.status === "failed") acc.failed += 1;

        return acc;
      },
      { total: 0, pending: 0, sent: 0, failed: 0 }, // Valor inicial del acumulador
    );
  }, [notifications]);

  // useCallback caches the function itself (not a result), so memo(NotificationItem)
  // receives the same reference on every render and can skip re-rendering
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

      <div className="filters">
        <input
          type="search"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Buscar por título o destinatario (mín. 2 letras)"
        />
        <select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value as typeof statusFilter)
          }
        >
          <option value="all">Todos ({counts.total})</option>
          <option value="pending">Pending ({counts.pending})</option>
          <option value="sent">Sent ({counts.sent})</option>
          <option value="failed">Failed ({counts.failed})</option>
        </select>
      </div>

      {loading && <p>Cargando...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && notifications.length === 0 && (
        <p className="empty">No hay notificaciones.</p>
      )}

      {notifications.length > 0 && filtered.length === 0 && (
        <p className="empty">Ninguna notificación coincide con el filtro.</p>
      )}

      <ul className="notifications-list">
        {filtered.map((n) => (
          // Pass handleDelete as is: an inline arrow would be a new function each render and break memo
          <NotificationItem
            key={n.id}
            notification={n}
            onDelete={handleDelete}
          />
        ))}
      </ul>
    </div>
  );
};

export default NotificationPage;
