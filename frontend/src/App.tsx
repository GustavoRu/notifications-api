import { useState, useEffect } from "react";
import heroImg from "./assets/hero.png";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./App.css";
import { clearToken, getToken } from "./services/api";
import LoginForm from "./components/LoginForm";
import NotificationPage from "./components/NotificationsPage";

function App() {
  const [count, setCount] = useState(0);
  const [token, setToken] = useState(getToken());

  useEffect(() => {
    console.log("token", token);
  }, []);

  // login() in services already saved the token; just sync React state
  const handleLogin = () => setToken(getToken());

  const handleLogout = () => {
    clearToken();
    setToken(null);
  };

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
