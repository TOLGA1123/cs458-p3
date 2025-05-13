"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ClipboardList, FileText, PlusCircle, LogOut } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/logout', {
        method: 'GET',
        credentials: 'include',
      })
      if (response.ok) {
        router.push('/')
      }
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <main className="container mx-auto max-w-4xl">
        <div className="flex flex-col items-center space-y-8">
          {/* Card Reading Section */}
          <Card className="w-full shadow-lg">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl md:text-3xl font-bold">Welcome to SurveySide</CardTitle>
              <CardDescription className="text-lg">
                Your central place for creating and managing surveys
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <p className="text-center text-gray-600">
                Get started by creating a new survey or check your existing ones. Our survey tool helps you
                gather meaningful insights quickly.
              </p>
            </CardContent>
          </Card>

          {/* Buttons Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            <Button
              variant="default"
              size="lg"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700"
              asChild
            >
              <Link href="/ai-survey">
                <FileText className="h-6 w-6" />
                <span>AI Survey</span>
              </Link>
            </Button>

            <Button
              variant="default"
              size="lg"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700"
              asChild
            >
              <Link href="/saved-surveys">
                <ClipboardList className="h-6 w-6" />
                <span>Created Surveys</span>
              </Link>
            </Button>

            <Button
              variant="default"
              size="lg"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-green-600 hover:bg-green-700"
              asChild
            >
              <Link href="/create-survey">
                <PlusCircle className="h-6 w-6" />
                <span>Create A Survey</span>
              </Link>
            </Button>

            <Button
              variant="default"
              size="lg"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-red-600 hover:bg-red-700"
              onClick={handleLogout}
              id="logoutButton"
            >
              <LogOut className="h-6 w-6" />
              <span>Log Out</span>
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
