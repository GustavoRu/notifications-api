import { useCallback, useState } from "react";
import "./App.css";
import { clearToken, getToken } from "./services/api";
import LoginForm from "./components/LoginForm";
import NotificationPage from "./components/NotificationsPage";

function App() {
  const [token, setToken] = useState(getToken());

  // useCallback keeps these references stable across App renders:
  // NotificationsPage uses onLogout as a useEffect and useCallback dependency,
  // so a new function on every render would refetch the list and break memo.

  // login() in services already saved the token; just sync React state
  const handleLogin = useCallback(() => setToken(getToken()), []);

  const handleLogout = useCallback(() => {
    clearToken();
    setToken(null);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Notifications</h1>
      </header>

      <main className="app-main">
        {token ? (
          <NotificationPage onLogout={handleLogout} />
        ) : (
          <LoginForm onLogin={handleLogin} />
        )}
      </main>
    </div>
  );
}

export default App;
