"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("") // Clear any previous errors
    try {
      const formData = new FormData()
      formData.append('user_input', email)
      formData.append('password', password)

      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      let data
      try {
        data = await response.json()
      } catch (jsonErr) {
        console.error('Failed to parse JSON:', jsonErr)
        setError('Server returned an invalid response. Please try again.')
        return
      }

      console.log('Login response:', data)
      if (data.success) {
        window.location.href = data.redirect
      } else if (data.error) {
        setError(data.error)
      } else {
        setError('Login failed. Please try again.')
      }
    } catch (err) {
      console.error('Login error:', err)
      if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
        setError('Unable to connect to the server. Please check your internet connection.')
      } else {
        setError('An unexpected error occurred. Please try again.')
      }
    }
  }

  const handleGoogleLogin = () => {
    window.location.href = 'http://127.0.0.1:5000/google/login';
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Login</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user_input">Email / Phone Number</Label>
            <Input
              id="user_input"
              type="text"
              placeholder="Enter your email or phone number"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Button id="loginButton" type="submit" className="w-full">
            Login
          </Button>
          <Button id="googleLoginButton" variant="outline" type="button" className="w-full" onClick={handleGoogleLogin}>
            Google Login
          </Button>
          {error && (
            <p id="errorMessage" className="mt-4 text-center text-sm text-red-600">{error}</p>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
