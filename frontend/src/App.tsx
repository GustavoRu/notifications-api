import { useState, useEffect } from "react";
import heroImg from "./assets/hero.png";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./App.css";
import { getToken } from "./services/api";
import LoginForm from "./components/LoginForm";
import NotificationPage from "./components/NotificationsPage";

function App() {
  const [count, setCount] = useState(0);
  const [token, setToken] = useState(getToken());

  useEffect(() => {
    console.log("token", token);
  }, []);

  return <>{token ? <NotificationPage /> : <LoginForm />}</>;
}

export default App;
