"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Star, ArrowLeft } from "lucide-react"
import Link from "next/link"

interface Question {
  id: string
  type: "multiple-choice" | "rating" | "text" | "dropdown" | "checkbox"
  title: string
  required: boolean
  options?: string[]
  maxRating?: number
  placeholder?: string
  conditionalLogic: {
    enabled: boolean
    parentQuestionId: string | null
    parentAnswer: string | null
  }
}

interface Survey {
  id: string
  title: string
  description: string
  questions: Question[]
  createdAt: string
}

export default function SurveyPage() {
  const params = useParams()
  const router = useRouter()
  const [survey, setSurvey] = useState<Survey | null>(null)
  const [loading, setLoading] = useState(true)
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({})
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    // Load survey from localStorage
    const loadSurvey = () => {
      const surveysJson = localStorage.getItem("savedSurveys")
      if (surveysJson) {
        try {
          const surveys = JSON.parse(surveysJson)
          const foundSurvey = surveys.find((s: Survey) => s.id === params.id)
          if (foundSurvey) {
            setSurvey(foundSurvey)
          } else {
            setError("Survey not found")
          }
        } catch (error) {
          console.error("Error parsing saved surveys:", error)
          setError("Error loading survey")
        }
      } else {
        setError("No saved surveys found")
      }
      setLoading(false)
    }

    loadSurvey()
  }, [params.id])

  // Get visible questions based on conditional logic
  const getVisibleQuestions = () => {
    if (!survey) return []

    return survey.questions.filter((question) => {
      if (!question.conditionalLogic.enabled) {
        return true
      }

      return (
        question.conditionalLogic.parentQuestionId &&
        question.conditionalLogic.parentAnswer &&
        answers[question.conditionalLogic.parentQuestionId] === question.conditionalLogic.parentAnswer
      )
    })
  }

  const handleSubmit = () => {
    // Validate required questions
    const visibleQuestions = getVisibleQuestions()
    const unansweredRequired = visibleQuestions.filter(
      (q) =>
        q.required && (!answers[q.id] || (Array.isArray(answers[q.id]) && (answers[q.id] as string[]).length === 0)),
    )

    if (unansweredRequired.length > 0) {
      setError(`Please answer all required questions (${unansweredRequired.length} remaining)`)
      return
    }

    // Here you would typically send the answers to a server
    console.log("Survey responses:", {
      surveyId: survey?.id,
      answers,
    })

    setSubmitted(true)
    setError("")
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 max-w-3xl text-center">
        <p>Loading survey...</p>
      </div>
    )
  }

  if (error && !survey) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <div className="bg-red-50 p-4 rounded-lg mb-6">
          <p className="text-red-600">{error}</p>
        </div>
        <Button asChild>
          <Link href="/saved-surveys">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Saved Surveys
          </Link>
        </Button>
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Card className="text-center py-12">
          <CardContent>
            <div className="flex flex-col items-center gap-4">
              <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-medium">Thank you for your response!</h3>
              <p className="text-muted-foreground">Your answers have been submitted successfully.</p>
              <Button asChild className="mt-4">
                <Link href="/saved-surveys">Return to Surveys</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const visibleQuestions = getVisibleQuestions()

  return (
    <div className="container mx-auto py-8 max-w-3xl">
      <Button variant="outline" asChild className="mb-6">
        <Link href="/saved-surveys">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Surveys
        </Link>
      </Button>

      <div className="bg-slate-50 p-6 rounded-lg">
        <div className="bg-white p-6 rounded-lg shadow-sm mb-6 text-center">
          <h1 className="text-2xl font-bold">{survey?.title}</h1>
          {survey?.description && <p className="text-muted-foreground mt-2">{survey.description}</p>}
        </div>

        {error && (
          <div className="bg-red-50 p-4 rounded-lg mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {visibleQuestions.map((question, visibleIndex) => (
          <Card key={question.id} className="mb-6 shadow-md">
            <CardContent className="p-0">
              {/* Question header */}
              <div className="p-4">
                <h3 className="font-medium text-lg">
                  {visibleIndex + 1}. {question.title}
                  {question.required && <span className="text-destructive ml-1">*</span>}
                </h3>
              </div>

              <Separator />

              {/* Question content */}
              <div className={`p-4 ${question.type === "rating" ? "text-center" : ""}`}>
                {question.type === "multiple-choice" && (
                  <div className="space-y-4">
                    {question.options?.map((option, i) => (
                      <div key={i} className="flex items-center space-x-3">
                        <input
                          type="radio"
                          id={`question-${question.id}-option-${i}`}
                          name={`question-${question.id}`}
                          value={option}
                          checked={answers[question.id] === option}
                          onChange={() => {
                            setAnswers({
                              ...answers,
                              [question.id]: option,
                            })
                          }}
                          className="h-4 w-4"
                        />
                        <Label htmlFor={`question-${question.id}-option-${i}`}>{option}</Label>
                      </div>
                    ))}
                  </div>
                )}

                {question.type === "rating" && (
                  <div className="flex gap-4 justify-center">
                    {Array.from({ length: question.maxRating || 5 }, (_, i) => {
                      const rating = (i + 1).toString()
                      return (
                        <button
                          key={i}
                          className="flex flex-col items-center"
                          onClick={() => {
                            setAnswers({
                              ...answers,
                              [question.id]: rating,
                            })
                          }}
                        >
                          {answers[question.id] && Number(answers[question.id]) >= i + 1 ? (
                            <Star className="h-8 w-8 fill-yellow-400 text-yellow-400" />
                          ) : (
                            <Star className="h-8 w-8 text-gray-300" />
                          )}
                          <span className="text-xs mt-1">{i + 1}</span>
                        </button>
                      )
                    })}
                  </div>
                )}

                {question.type === "text" && (
                  <div>
                    <Textarea
                      placeholder={question.placeholder || "Enter your answer here..."}
                      value={(answers[question.id] as string) || ""}
                      onChange={(e) => {
                        setAnswers({
                          ...answers,
                          [question.id]: e.target.value,
                        })
                      }}
                    />
                  </div>
                )}

                {question.type === "dropdown" && (
                  <div>
                    <Select
                      value={(answers[question.id] as string) || ""}
                      onValueChange={(value) => {
                        setAnswers({
                          ...answers,
                          [question.id]: value,
                        })
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select an option" />
                      </SelectTrigger>
                      <SelectContent>
                        {question.options?.map((option, i) => (
                          <SelectItem key={i} value={option}>
                            {option}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {question.type === "checkbox" && (
                  <div className="space-y-4">
                    {question.options?.map((option, i) => {
                      const selectedOptions = (answers[question.id] as string[]) || []
                      const isChecked = selectedOptions.includes(option)

                      return (
                        <div key={i} className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            id={`question-${question.id}-option-${i}`}
                            checked={isChecked}
                            onChange={() => {
                              let newSelected
                              if (isChecked) {
                                newSelected = selectedOptions.filter((item) => item !== option)
                              } else {
                                newSelected = [...selectedOptions, option]
                              }
                              setAnswers({
                                ...answers,
                                [question.id]: newSelected,
                              })
                            }}
                            className="h-4 w-4"
                          />
                          <Label htmlFor={`question-${question.id}-option-${i}`}>{option}</Label>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        <div className="text-center mt-8">
          <Button size="lg" onClick={handleSubmit}>
            Submit Survey
          </Button>
        </div>
      </div>
    </div>
  )
}
