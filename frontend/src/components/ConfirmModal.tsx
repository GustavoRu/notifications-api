interface Props {
  title: string;
  message: string;
  confirmLabel?: string;
  loading?: boolean;
  error?: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmModal = ({
  title,
  message,
  confirmLabel = "Confirmar",
  loading = false,
  error,
  onConfirm,
  onCancel,
}: Props) => {
  return (
    <div className="modal-backdrop" onClick={onCancel}>
      {/* Stop clicks inside the card from closing the modal */}
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <h3>{title}</h3>
        <p>{message}</p>

        {error && <p className="error-message">{error}</p>}

        <div className="form-actions">
          <button className="secondary" onClick={onCancel} disabled={loading}>
            Cancelar
          </button>
          <button className="danger" onClick={onConfirm} disabled={loading}>
            {loading ? "Eliminando..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
