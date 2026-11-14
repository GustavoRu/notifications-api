export interface Notification {
  id: number;
  title: string;
  content: string;
  channel: string;
  recipient: string;
  status: "pending" | "sent" | "failed";
  created_at: string;
}

export interface NotificationCreate {
  title: string;
  content: string;
  channel: string;
  recipient: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}