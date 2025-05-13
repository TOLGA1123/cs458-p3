"use client"

import { useState, useEffect } from "react"
import { PlusCircle, Trash2, ChevronDown, ChevronUp, Save, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { useRouter, useSearchParams } from "next/navigation"

// Question type definitions
type QuestionType = "multiple-choice" | "rating" | "text" | "dropdown" | "checkbox"

interface BaseQuestion {
  id: string
  type: QuestionType
  title: string
  required: boolean
  conditionalLogic: {
    enabled: boolean
    parentQuestionId: string | null
    parentAnswer: string | null
  }
}

interface MultipleChoiceQuestion extends BaseQuestion {
  type: "multiple-choice"
  options: string[]
}

interface RatingQuestion extends BaseQuestion {
  type: "rating"
  maxRating: number
}

interface TextQuestion extends BaseQuestion {
  type: "text"
  placeholder: string
}

interface DropdownQuestion extends BaseQuestion {
  type: "dropdown"
  options: string[]
}

interface CheckboxQuestion extends BaseQuestion {
  type: "checkbox"
  options: string[]
}

type Question = MultipleChoiceQuestion | RatingQuestion | TextQuestion | DropdownQuestion | CheckboxQuestion

export default function CreateSurveyPage() {
  const [surveyTitle, setSurveyTitle] = useState("Untitled Survey")
  const [surveyDescription, setSurveyDescription] = useState("")
  const [questions, setQuestions] = useState<Question[]>([])
  const [activeTab, setActiveTab] = useState("edit")
  const [previewAnswers, setPreviewAnswers] = useState<Record<string, string | string[]>>({})

  const router = useRouter()
  const searchParams = useSearchParams()
  const editParam = searchParams.get("edit")
  const [editingSurveyId, setEditingSurveyId] = useState<string | null>(null)

  useEffect(() => {
    // Check if we're editing an existing survey
    if (editParam) {
      setEditingSurveyId(editParam)

      // Load the survey data from localStorage
      const surveysJson = localStorage.getItem("savedSurveys")
      if (surveysJson) {
        try {
          const surveys = JSON.parse(surveysJson)
          const surveyToEdit = surveys.find((s: any) => s.id === editParam)

          if (surveyToEdit) {
            setSurveyTitle(surveyToEdit.title)
            setSurveyDescription(surveyToEdit.description || "")
            setQuestions(surveyToEdit.questions)
          }
        } catch (error) {
          console.error("Error loading survey to edit:", error)
        }
      }
    }
  }, [editParam])

  // Generate a unique ID for questions
  const generateId = () => `question_${Date.now()}_${Math.floor(Math.random() * 1000)}`

  // Add a new question
  const addQuestion = (type: QuestionType) => {
    const baseQuestion: BaseQuestion = {
      id: generateId(),
      type,
      title: "New Question",
      required: false,
      conditionalLogic: {
        enabled: false,
        parentQuestionId: null,
        parentAnswer: null,
      },
    }

    let newQuestion: Question

    switch (type) {
      case "multiple-choice":
        newQuestion = {
          ...baseQuestion,
          type: "multiple-choice",
          options: ["Option 1", "Option 2", "Option 3"],
        }
        break
      case "rating":
        newQuestion = {
          ...baseQuestion,
          type: "rating",
          maxRating: 5,
        }
        break
      case "text":
        newQuestion = {
          ...baseQuestion,
          type: "text",
          placeholder: "Enter your answer here...",
        }
        break
      case "dropdown":
        newQuestion = {
          ...baseQuestion,
          type: "dropdown",
          options: ["Option 1", "Option 2", "Option 3"],
        }
        break
      case "checkbox":
        newQuestion = {
          ...baseQuestion,
          type: "checkbox",
          options: ["Option 1", "Option 2", "Option 3"],
        }
        break
      default:
        return
    }

    setQuestions([...questions, newQuestion])
  }

  // Remove a question
  const removeQuestion = (id: string) => {
    setQuestions(questions.filter((q) => q.id !== id))

    // Also update any conditional logic that depends on this question
    setQuestions((prevQuestions) =>
      prevQuestions.map((q) => {
        if (q.conditionalLogic.parentQuestionId === id) {
          return {
            ...q,
            conditionalLogic: {
              enabled: false,
              parentQuestionId: null,
              parentAnswer: null,
            },
          }
        }
        return q
      }),
    )
  }

  // Update question title
  const updateQuestionTitle = (id: string, title: string) => {
    setQuestions(questions.map((q) => (q.id === id ? { ...q, title } : q)))
  }

  // Toggle question required status
  const toggleRequired = (id: string) => {
    setQuestions(questions.map((q) => (q.id === id ? { ...q, required: !q.required } : q)))
  }

  // Update options for multiple choice, dropdown, or checkbox questions
  const updateOptions = (id: string, options: string[]) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id && (q.type === "multiple-choice" || q.type === "dropdown" || q.type === "checkbox")) {
          return { ...q, options }
        }
        return q
      }),
    )
  }

  // Add option to a question
  const addOption = (id: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id && (q.type === "multiple-choice" || q.type === "dropdown" || q.type === "checkbox")) {
          return { ...q, options: [...q.options, `Option ${q.options.length + 1}`] }
        }
        return q
      }),
    )
  }

  // Remove option from a question
  const removeOption = (questionId: string, optionIndex: number) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === questionId && (q.type === "multiple-choice" || q.type === "dropdown" || q.type === "checkbox")) {
          return {
            ...q,
            options: q.options.filter((_, index) => index !== optionIndex),
          }
        }
        return q
      }),
    )
  }

  // Update option text
  const updateOptionText = (questionId: string, optionIndex: number, text: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === questionId && (q.type === "multiple-choice" || q.type === "dropdown" || q.type === "checkbox")) {
          const newOptions = [...q.options]
          newOptions[optionIndex] = text
          return { ...q, options: newOptions }
        }
        return q
      }),
    )
  }

  // Update max rating for rating questions
  const updateMaxRating = (id: string, maxRating: number) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id && q.type === "rating") {
          return { ...q, maxRating }
        }
        return q
      }),
    )
  }

  // Update placeholder for text questions
  const updatePlaceholder = (id: string, placeholder: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id && q.type === "text") {
          return { ...q, placeholder }
        }
        return q
      }),
    )
  }

  // Toggle conditional logic
  const toggleConditionalLogic = (id: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id) {
          return {
            ...q,
            conditionalLogic: {
              ...q.conditionalLogic,
              enabled: !q.conditionalLogic.enabled,
            },
          }
        }
        return q
      }),
    )
  }

  // Update conditional logic parent question
  const updateConditionalLogicParent = (id: string, parentQuestionId: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id) {
          return {
            ...q,
            conditionalLogic: {
              ...q.conditionalLogic,
              parentQuestionId,
              parentAnswer: null, // Reset answer when parent changes
            },
          }
        }
        return q
      }),
    )
  }

  // Update conditional logic parent answer
  const updateConditionalLogicAnswer = (id: string, parentAnswer: string) => {
    setQuestions(
      questions.map((q) => {
        if (q.id === id) {
          return {
            ...q,
            conditionalLogic: {
              ...q.conditionalLogic,
              parentAnswer,
            },
          }
        }
        return q
      }),
    )
  }

  // Move question up
  const moveQuestionUp = (index: number) => {
    if (index === 0) return
    const newQuestions = [...questions]
    const temp = newQuestions[index]
    newQuestions[index] = newQuestions[index - 1]
    newQuestions[index - 1] = temp
    setQuestions(newQuestions)
  }

  // Move question down
  const moveQuestionDown = (index: number) => {
    if (index === questions.length - 1) return
    const newQuestions = [...questions]
    const temp = newQuestions[index]
    newQuestions[index] = newQuestions[index + 1]
    newQuestions[index + 1] = temp
    setQuestions(newQuestions)
  }

  // Get available parent questions for conditional logic
  // (only questions that appear before the current question)
  const getAvailableParentQuestions = (currentQuestionId: string) => {
    const currentIndex = questions.findIndex((q) => q.id === currentQuestionId)
    return questions.filter(
      (q, index) =>
        index < currentIndex &&
        (q.type === "multiple-choice" || q.type === "dropdown" || q.type === "checkbox" || q.type === "rating"),
    )
  }

  // Get possible answers for a parent question
  const getPossibleAnswers = (parentQuestionId: string | null) => {
    if (!parentQuestionId) return []

    const parentQuestion = questions.find((q) => q.id === parentQuestionId)
    if (!parentQuestion) return []

    switch (parentQuestion.type) {
      case "multiple-choice":
      case "dropdown":
      case "checkbox":
        return parentQuestion.options
      case "rating":
        return Array.from({ length: parentQuestion.maxRating }, (_, i) => (i + 1).toString())
      default:
        return []
    }
  }

  const saveSurvey = () => {
    const survey = {
      id: editingSurveyId || generateId(),
      title: surveyTitle,
      description: surveyDescription,
      questions,
      createdAt: new Date().toISOString(),
    }

    // Get existing surveys from localStorage
    const existingSurveysJson = localStorage.getItem("savedSurveys")
    let existingSurveys = []

    if (existingSurveysJson) {
      try {
        existingSurveys = JSON.parse(existingSurveysJson)
      } catch (error) {
        console.error("Error parsing saved surveys:", error)
      }
    }

    // If editing, update the existing survey
    if (editingSurveyId) {
      existingSurveys = existingSurveys.map((s: any) => (s.id === editingSurveyId ? survey : s))
    } else {
      // Otherwise add the new survey
      existingSurveys.push(survey)
    }

    // Save back to localStorage
    localStorage.setItem("savedSurveys", JSON.stringify(existingSurveys))

    console.log("Survey saved:", survey)
    alert("Survey saved successfully!")

    // Navigate to the saved surveys page
    router.push("/saved-surveys")
  }

  const handleTabChange = (value: string) => {
    if (value === "preview") {
      // Reset preview answers when entering preview mode
      setPreviewAnswers({})
    }
    setActiveTab(value)
  }

  // Get visible questions based on conditional logic
  const getVisibleQuestions = () => {
    return questions.filter((question) => {
      if (!question.conditionalLogic.enabled) {
        return true
      }

      return (
        question.conditionalLogic.parentQuestionId &&
        question.conditionalLogic.parentAnswer &&
        previewAnswers[question.conditionalLogic.parentQuestionId] === question.conditionalLogic.parentAnswer
      )
    })
  }

  return (
    <div className="container mx-auto py-8 max-w-3xl">
      <h1 className="text-3xl font-bold mb-6">{editingSurveyId ? "Edit Survey" : "Create New Survey"}</h1>

      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="edit">Edit Survey</TabsTrigger>
          <TabsTrigger value="preview">Preview Survey</TabsTrigger>
        </TabsList>

        <TabsContent value="edit" className="space-y-6">
          {/* Survey Details */}
          <Card>
            <CardHeader>
              <CardTitle>Survey Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="survey-title">Survey Title</Label>
                <Input
                  id="survey-title"
                  value={surveyTitle}
                  onChange={(e) => setSurveyTitle(e.target.value)}
                  placeholder="Enter survey title"
                />
              </div>
              <div>
                <Label htmlFor="survey-description">Description (Optional)</Label>
                <Textarea
                  id="survey-description"
                  value={surveyDescription}
                  onChange={(e) => setSurveyDescription(e.target.value)}
                  placeholder="Enter survey description"
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Question List */}
          <div className="space-y-4">
            {questions.map((question, index) => (
              <Card key={question.id} className="relative">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="bg-muted text-muted-foreground w-8 h-8 rounded-full flex items-center justify-center">
                        {index + 1}
                      </div>
                      <Select
                        value={question.type}
                        onValueChange={(value: QuestionType) => {
                          // This is a simplified approach - in a real app, you'd need to handle conversion between question types
                          const newQuestion = {
                            ...question,
                            type: value as QuestionType,
                          } as Question

                          // Add default properties based on the new type
                          if (value === "multiple-choice" || value === "dropdown" || value === "checkbox") {
                            ;(newQuestion as any).options = ["Option 1", "Option 2", "Option 3"]
                          } else if (value === "rating") {
                            ;(newQuestion as any).maxRating = 5
                          } else if (value === "text") {
                            ;(newQuestion as any).placeholder = "Enter your answer here..."
                          }

                          setQuestions(questions.map((q) => (q.id === question.id ? newQuestion : q)))
                        }}
                      >
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="Question Type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="multiple-choice">Multiple Choice</SelectItem>
                          <SelectItem value="rating">Rating Scale</SelectItem>
                          <SelectItem value="text">Text Field</SelectItem>
                          <SelectItem value="dropdown">Dropdown</SelectItem>
                          <SelectItem value="checkbox">Checkbox</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" onClick={() => moveQuestionUp(index)} disabled={index === 0}>
                        <ChevronUp className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => moveQuestionDown(index)}
                        disabled={index === questions.length - 1}
                      >
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => removeQuestion(question.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor={`question-${question.id}-title`}>Question Text</Label>
                    <Input
                      id={`question-${question.id}-title`}
                      value={question.title}
                      onChange={(e) => updateQuestionTitle(question.id, e.target.value)}
                      placeholder="Enter question text"
                    />
                  </div>

                  {/* Question type specific settings */}
                  {question.type === "multiple-choice" && (
                    <div className="space-y-2">
                      <Label>Options</Label>
                      {question.options.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center gap-2">
                          <Input
                            value={option}
                            onChange={(e) => updateOptionText(question.id, optionIndex, e.target.value)}
                            placeholder={`Option ${optionIndex + 1}`}
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeOption(question.id, optionIndex)}
                            disabled={question.options.length <= 1}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      <Button variant="outline" size="sm" onClick={() => addOption(question.id)} className="mt-2">
                        <PlusCircle className="h-4 w-4 mr-2" />
                        Add Option
                      </Button>
                    </div>
                  )}

                  {question.type === "rating" && (
                    <div>
                      <Label htmlFor={`question-${question.id}-max-rating`}>Max Rating</Label>
                      <Select
                        value={question.maxRating.toString()}
                        onValueChange={(value) => updateMaxRating(question.id, Number.parseInt(value))}
                      >
                        <SelectTrigger id={`question-${question.id}-max-rating`}>
                          <SelectValue placeholder="Select max rating" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="3">3 Stars</SelectItem>
                          <SelectItem value="5">5 Stars</SelectItem>
                          <SelectItem value="10">10 Points</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {question.type === "text" && (
                    <div>
                      <Label htmlFor={`question-${question.id}-placeholder`}>Placeholder Text</Label>
                      <Input
                        id={`question-${question.id}-placeholder`}
                        value={question.placeholder}
                        onChange={(e) => updatePlaceholder(question.id, e.target.value)}
                        placeholder="Enter placeholder text"
                      />
                    </div>
                  )}

                  {question.type === "dropdown" && (
                    <div className="space-y-2">
                      <Label>Options</Label>
                      {question.options.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center gap-2">
                          <Input
                            value={option}
                            onChange={(e) => updateOptionText(question.id, optionIndex, e.target.value)}
                            placeholder={`Option ${optionIndex + 1}`}
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeOption(question.id, optionIndex)}
                            disabled={question.options.length <= 1}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      <Button variant="outline" size="sm" onClick={() => addOption(question.id)} className="mt-2">
                        <PlusCircle className="h-4 w-4 mr-2" />
                        Add Option
                      </Button>
                    </div>
                  )}

                  {question.type === "checkbox" && (
                    <div className="space-y-2">
                      <Label>Options</Label>
                      {question.options.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center gap-2">
                          <Input
                            value={option}
                            onChange={(e) => updateOptionText(question.id, optionIndex, e.target.value)}
                            placeholder={`Option ${optionIndex + 1}`}
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeOption(question.id, optionIndex)}
                            disabled={question.options.length <= 1}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      <Button variant="outline" size="sm" onClick={() => addOption(question.id)} className="mt-2">
                        <PlusCircle className="h-4 w-4 mr-2" />
                        Add Option
                      </Button>
                    </div>
                  )}

                  {/* Conditional Logic */}
                  <div className="border-t pt-4 mt-4">
                    <div className="flex items-center justify-between mb-4">
                      <Label htmlFor={`question-${question.id}-conditional`} className="font-medium">
                        Conditional Logic
                      </Label>
                      <Switch
                        id={`question-${question.id}-conditional`}
                        checked={question.conditionalLogic.enabled}
                        onCheckedChange={() => toggleConditionalLogic(question.id)}
                        disabled={index === 0} // First question can't have conditional logic
                      />
                    </div>

                    {question.conditionalLogic.enabled && (
                      <div className="space-y-4 pl-4 border-l-2 border-muted">
                        <p className="text-sm text-muted-foreground">Show this question only when:</p>

                        <div>
                          <Label htmlFor={`question-${question.id}-parent`}>Previous Question</Label>
                          <Select
                            value={question.conditionalLogic.parentQuestionId || ""}
                            onValueChange={(value) => updateConditionalLogicParent(question.id, value)}
                          >
                            <SelectTrigger id={`question-${question.id}-parent`}>
                              <SelectValue placeholder="Select a question" />
                            </SelectTrigger>
                            <SelectContent>
                              {getAvailableParentQuestions(question.id).map((q) => (
                                <SelectItem key={q.id} value={q.id}>
                                  {q.title}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        {question.conditionalLogic.parentQuestionId && (
                          <div>
                            <Label htmlFor={`question-${question.id}-answer`}>Answer is</Label>
                            <Select
                              value={question.conditionalLogic.parentAnswer || ""}
                              onValueChange={(value) => updateConditionalLogicAnswer(question.id, value)}
                            >
                              <SelectTrigger id={`question-${question.id}-answer`}>
                                <SelectValue placeholder="Select an answer" />
                              </SelectTrigger>
                              <SelectContent>
                                {getPossibleAnswers(question.conditionalLogic.parentQuestionId).map((answer) => (
                                  <SelectItem key={answer} value={answer}>
                                    {answer}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Required toggle */}
                  <div className="flex items-center space-x-2">
                    <Switch
                      id={`question-${question.id}-required`}
                      checked={question.required}
                      onCheckedChange={() => toggleRequired(question.id)}
                    />
                    <Label htmlFor={`question-${question.id}-required`}>
                      Required question
                      <span className="text-xs text-muted-foreground ml-2">
                        (Must be answered to submit the survey)
                      </span>
                    </Label>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Question Button */}
          <div className="flex flex-row flex-wrap gap-2 justify-center">
            <Button onClick={() => addQuestion("multiple-choice")} id="add-multiple-choice" >
              <PlusCircle className="h-4 w-4 mr-2" />
              Multiple Choice
            </Button>
            <Button onClick={() => addQuestion("rating")}  id="add-rating">
              <PlusCircle className="h-4 w-4 mr-2" />
              Rating Scale
            </Button>
            <Button onClick={() => addQuestion("text")}  id="add-text" >
              <PlusCircle className="h-4 w-4 mr-2" />
              Text Field
            </Button>
            <Button onClick={() => addQuestion("dropdown")} id="add-dropdown" >
              <PlusCircle className="h-4 w-4 mr-2" />
              Dropdown
            </Button>
            <Button onClick={() => addQuestion("checkbox")} id="add-checkbox" >
              <PlusCircle className="h-4 w-4 mr-2" />
              Checkbox
            </Button>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={saveSurvey} size="lg" className="gap-2" id="save-button">
              <Save className="h-4 w-4" />
              Save Survey
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="preview" className="space-y-6">
          <div className="bg-slate-50 p-6 rounded-lg">
            <div className="bg-white p-6 rounded-lg shadow-sm mb-6 text-center">
              <h1 className="text-2xl font-bold">{surveyTitle}</h1>
              {surveyDescription && <p className="text-muted-foreground mt-2">{surveyDescription}</p>}
            </div>

            {questions.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>No questions added yet. Switch to Edit mode to add questions.</p>
              </div>
            ) : (
              (() => {
                // Get visible questions based on conditional logic
                const visibleQuestions = getVisibleQuestions()

                return visibleQuestions.map((question, visibleIndex) => {
                  return (
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
                              {question.options.map((option, i) => (
                                <div key={i} className="flex items-center space-x-3">
                                  <input
                                    type="radio"
                                    id={`preview-${question.id}-option-${i}`}
                                    name={`preview-${question.id}`}
                                    value={option}
                                    checked={previewAnswers[question.id] === option}
                                    onChange={() => {
                                      setPreviewAnswers({
                                        ...previewAnswers,
                                        [question.id]: option,
                                      })
                                    }}
                                    className="h-4 w-4"
                                  />
                                  <Label htmlFor={`preview-${question.id}-option-${i}`}>{option}</Label>
                                </div>
                              ))}
                            </div>
                          )}

                          {question.type === "rating" && (
                            <div className="flex gap-4 justify-center">
                              {Array.from({ length: question.maxRating }, (_, i) => {
                                const rating = (i + 1).toString()
                                return (
                                  <button
                                    key={i}
                                    className="flex flex-col items-center"
                                    onClick={() => {
                                      setPreviewAnswers({
                                        ...previewAnswers,
                                        [question.id]: rating,
                                      })
                                    }}
                                  >
                                    {previewAnswers[question.id] && Number(previewAnswers[question.id]) >= i + 1 ? (
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
                                placeholder={question.placeholder}
                                value={(previewAnswers[question.id] as string) || ""}
                                onChange={(e) => {
                                  setPreviewAnswers({
                                    ...previewAnswers,
                                    [question.id]: e.target.value,
                                  })
                                }}
                              />
                            </div>
                          )}

                          {question.type === "dropdown" && (
                            <div>
                              <Select
                                value={(previewAnswers[question.id] as string) || ""}
                                onValueChange={(value) => {
                                  setPreviewAnswers({
                                    ...previewAnswers,
                                    [question.id]: value,
                                  })
                                }}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select an option" />
                                </SelectTrigger>
                                <SelectContent>
                                  {question.options.map((option, i) => (
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
                              {question.options.map((option, i) => {
                                const selectedOptions = (previewAnswers[question.id] as string[]) || []
                                const isChecked = selectedOptions.includes(option)

                                return (
                                  <div key={i} className="flex items-center space-x-3">
                                    <input
                                      type="checkbox"
                                      id={`preview-${question.id}-option-${i}`}
                                      checked={isChecked}
                                      onChange={() => {
                                        let newSelected
                                        if (isChecked) {
                                          newSelected = selectedOptions.filter((item) => item !== option)
                                        } else {
                                          newSelected = [...selectedOptions, option]
                                        }
                                        setPreviewAnswers({
                                          ...previewAnswers,
                                          [question.id]: newSelected,
                                        })
                                      }}
                                      className="h-4 w-4"
                                    />
                                    <Label htmlFor={`preview-${question.id}-option-${i}`}>{option}</Label>
                                  </div>
                                )
                              })}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })
              })()
            )}

            <div className="text-center mt-8">
              <Button size="lg">Submit Survey</Button>
            </div>
          </div>

          <div className="flex justify-center mt-6">
            <Button variant="outline" onClick={() => setActiveTab("edit")} className="mr-4">
              Back to Editor
            </Button>
            <Button onClick={saveSurvey} className="gap-2">
              <Save className="h-4 w-4" />
              Save Survey
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
