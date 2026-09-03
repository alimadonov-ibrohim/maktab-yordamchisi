import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE ? `${API_BASE}/api` : '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
    }
    return Promise.reject(error);
  }
);

export function getTelegramInitData(): string {
  try {
    const tg = window.Telegram?.WebApp;
    if (tg?.initData) {
      return tg.initData;
    }
  } catch (e) {
    console.error('Telegram WebApp not available', e);
  }
  return '';
}

export async function authenticateWithTelegram() {
  const initData = getTelegramInitData();

  if (!initData) {
    throw new Error('Telegram WebApp initData not available');
  }

  const res = await api.post('/auth/telegram', { init_data: initData });
  return res.data;
}

export async function authenticateWithContact(phone: string, telegramId?: number) {
  const res = await api.post('/auth/contact', {
    phone,
    telegram_id: telegramId,
  });
  return res.data;
}
