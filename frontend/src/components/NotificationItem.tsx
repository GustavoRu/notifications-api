import { memo, useState } from "react";
import type { Notification } from "../types";
import ConfirmModal from "./ConfirmModal";

interface Props {
  notification: Notification;
  onDelete: (id: number) => Promise<void>;
}

const NotificationItem = ({ notification, onDelete }: Props) => {
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const closeModal = () => {
    setConfirming(false);
    setError(null);
  };

  const handleConfirm = async () => {
    try {
      setDeleting(true);
      setError(null);
      // On success the parent removes this item, so no state to reset here
      await onDelete(notification.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
      setDeleting(false);
    }
  };

  return (
    <li className="notification-item">
      <div className="notification-top">
        <strong>{notification.title}</strong>
        <span className="badge">{notification.channel}</span>
        <span className={`badge status-${notification.status}`}>
          {notification.status}
        </span>
      </div>
      <div>{notification.content}</div>
      <div className="notification-bottom">
        <span className="notification-meta">
          Para: {notification.recipient} ·{" "}
          {new Date(notification.created_at).toLocaleString()}
        </span>
        <button className="danger small" onClick={() => setConfirming(true)}>
          Eliminar
        </button>
      </div>

      {confirming && (
        <ConfirmModal
          title="Eliminar notificación"
          message={`¿Seguro que querés eliminar "${notification.title}"?`}
          confirmLabel="Eliminar"
          loading={deleting}
          error={error}
          onConfirm={handleConfirm}
          onCancel={closeModal}
        />
      )}
    </li>
  );
};

export default memo(NotificationItem);
