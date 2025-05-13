"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Eye, Edit, Trash2, FileText } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import Link from "next/link"

interface SavedSurvey {
  id: string
  title: string
  description: string
  questions: any[]
  createdAt: string
}

export default function SavedSurveysPage() {
  const [savedSurveys, setSavedSurveys] = useState<SavedSurvey[]>([])
  const router = useRouter()

  useEffect(() => {
    // Load saved surveys from localStorage
    const loadSavedSurveys = () => {
      const surveysJson = localStorage.getItem("savedSurveys")
      if (surveysJson) {
        try {
          const surveys = JSON.parse(surveysJson)
          setSavedSurveys(surveys)
        } catch (error) {
          console.error("Error parsing saved surveys:", error)
          setSavedSurveys([])
        }
      }
    }

    loadSavedSurveys()
  }, [])

  const deleteSurvey = (id: string) => {
    const updatedSurveys = savedSurveys.filter((survey) => survey.id !== id)
    setSavedSurveys(updatedSurveys)
    localStorage.setItem("savedSurveys", JSON.stringify(updatedSurveys))
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Saved Surveys</h1>
        <Button onClick={() => router.push("/create-survey")}>Create New Survey</Button>
      </div>

      {savedSurveys.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <div className="flex flex-col items-center gap-4">
              <FileText className="h-12 w-12 text-muted-foreground" />
              <h3 className="text-xl font-medium">No surveys found</h3>
              <p className="text-muted-foreground">
                You haven't created any surveys yet. Click the button above to create your first survey.
              </p>
              <Button onClick={() => router.push("/create-survey")} className="mt-2">
                Create New Survey
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {savedSurveys.map((survey) => (
            <Card key={survey.id} className="relative">
              <CardHeader>
                <CardTitle className="line-clamp-1">{survey.title}</CardTitle>
                <p className="text-sm text-muted-foreground">Created: {formatDate(survey.createdAt)}</p>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground line-clamp-2">{survey.description || "No description provided"}</p>
                <p className="text-sm mt-2">
                  {survey.questions.length} {survey.questions.length === 1 ? "question" : "questions"}
                </p>
              </CardContent>
              <Separator />
              <CardFooter className="flex justify-between pt-4">
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/survey/${survey.id}`}>
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Link>
                </Button>
                <Button variant="outline" size="sm" onClick={() => router.push(`/create-survey?edit=${survey.id}`)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" onClick={() => deleteSurvey(survey.id)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
