'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LoginForm } from '../../components/loginform';

export default function LoginPage() {
  const [userInput, setUserInput] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('user_input', userInput);
      formData.append('password', password);

      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        body: formData,
        credentials: 'include', // send cookies/session if needed
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else {
        const data = await response.json();
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('An error occurred during login');
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = 'http://127.0.0.1:5000/google/login';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f4f7fc]">
      <LoginForm />
    </div>
  );
} 