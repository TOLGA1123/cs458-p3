"use client"

import * as React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { format } from "date-fns"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const educationLevels = [
  { value: "high_school", label: "High School" },
  { value: "bachelors", label: "Bachelor's Degree" },
  { value: "masters", label: "Master's Degree" },
  { value: "phd", label: "PhD" },
  { value: "other", label: "Other" },
]

const aiModels = [
  { id: "chatgpt", label: "ChatGPT" },
  { id: "claude", label: "Claude" },
  { id: "bard", label: "Bard" },
  { id: "llama", label: "Llama" },
  { id: "gpt4", label: "GPT-4" },
]

const formSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  birthDate: z
    .date({
      required_error: "Birth date is required.",
    })
    .refine((date) => date <= new Date(), {
      message: "Birth date cannot be in the future.",
    }),
  educationLevel: z.string({
    required_error: "Please select an education level.",
  }),
  city: z.string().min(2, {
    message: "City must be at least 2 characters.",
  }),
  gender: z.enum(["male", "female", "other", "prefer_not_to_say"], {
    required_error: "Please select a gender.",
  }),
  models: z.array(z.string()).refine((value) => value.length > 0, {
    message: "You must select at least one AI model.",
  }),
  modelCons: z.record(z.string().optional()),
  useCase: z.string().min(10, {
    message: "Use case must be at least 10 characters.",
  }),
})

export default function AISurveyForm() {
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [flashMessage, setFlashMessage] = React.useState<{ message: string; type: "success" | "error" } | null>(null)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      city: "",
      educationLevel: "",
      gender: undefined,
      models: [],
      modelCons: {},
      useCase: "",
    },
  })

  const watchedModels = form.watch("models")

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true)
    console.log("Form submission started with values:", values)

    // Check for duplicate submission
    const newSubmission = JSON.stringify(values)
    const lastSubmission = localStorage.getItem("lastSurveySubmission")
    console.log("Checking for duplicate submission:", { newSubmission, lastSubmission })

    if (newSubmission === lastSubmission) {
      console.log("Duplicate submission detected")
      setFlashMessage({
        message: "You can only submit same form contents once.",
        type: "error",
      })
      setIsSubmitting(false)
      return
    }

    try {
      // Format the data to match backend expectations
      const formData = {
        name: values.name,
        birth_date: format(values.birthDate, "yyyy-MM-dd"),
        education_level: values.educationLevel,
        city: values.city,
        gender: values.gender,
        models: values.models,
        use_case: values.useCase,
        // Add cons for each selected model, only if they have a value
        ...Object.entries(values.modelCons).reduce((acc, [model, cons]) => {
          // Only add cons if they have a non-empty value
          if (cons && cons.trim() && cons.trim() !== "None") {
            return {
              ...acc,
              [`${model.toLowerCase()}_cons`]: cons.trim()
            }
          }
          return acc
        }, {})
      }
      console.log("Formatted data being sent to backend:", formData)

      const response = await fetch("http://127.0.0.1:5000/survey/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
        credentials: "include",
      })
      console.log("Backend response status:", response.status)

      const data = await response.json()
      console.log("Backend response data:", data)

      if (data.success) {
        console.log("Survey submission successful")
        // Store submission in localStorage to prevent duplicates
        localStorage.setItem("lastSurveySubmission", newSubmission)

        setFlashMessage({
          message: "Survey sent successfully!",
          type: "success",
        })
      } else {
        console.error("Backend returned error:", data.message)
        throw new Error(data.message || "Failed to send survey")
      }
    } catch (error) {
      console.error("Error during form submission:", error)
      setFlashMessage({
        message: error instanceof Error ? error.message : "An error occurred while submitting the form.",
        type: "error",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader className="pb-3">
        <CardTitle>AI Survey Form</CardTitle>
      </CardHeader>
      <CardContent>
        {flashMessage && (
          <Alert variant={flashMessage.type === "error" ? "destructive" : "default"} className="mb-4">
            <AlertDescription>{flashMessage.message}</AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input id="name" placeholder="Your name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="birthDate"
              render={({ field: { value, onChange, ...fieldProps } }) => (
                <FormItem>
                  <FormLabel>Birth Date</FormLabel>
                  <FormControl>
                    <Input
                      id="birth_date"
                      type="date"
                      placeholder="YYYY-MM-DD"
                      max={new Date().toISOString().split("T")[0]}
                      onChange={(e) => {
                        const date = e.target.value ? new Date(e.target.value) : undefined
                        onChange(date)
                      }}
                      value={value ? format(value, "yyyy-MM-dd") : ""}
                      {...fieldProps}
                    />
                  </FormControl>
                  <FormDescription>Enter your birth date in YYYY-MM-DD format</FormDescription>
                  <FormMessage id="birthdate_error" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="educationLevel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Education Level</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger id="education_level">
                        <SelectValue placeholder="Select education level" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {educationLevels.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="city"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>City</FormLabel>
                  <FormControl>
                    <Input id="city" placeholder="Your city" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="gender"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel>Gender</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="flex flex-col space-y-1"
                    >
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="male" />
                        </FormControl>
                        <FormLabel className="font-normal">Male</FormLabel>
                      </FormItem>
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="female" />
                        </FormControl>
                        <FormLabel className="font-normal">Female</FormLabel>
                      </FormItem>
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="other" />
                        </FormControl>
                        <FormLabel className="font-normal">Other</FormLabel>
                      </FormItem>
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="prefer_not_to_say" />
                        </FormControl>
                        <FormLabel className="font-normal">Prefer not to say</FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="models"
              render={() => (
                <FormItem>
                  <div className="mb-4">
                    <FormLabel className="text-base">Models Tried</FormLabel>
                    <FormDescription>Select the AI models you have tried.</FormDescription>
                  </div>
                  {aiModels.map((model) => (
                    <div key={model.id} className="mb-4 model-pair">
                      <FormField
                        control={form.control}
                        name="models"
                        render={({ field }) => {
                          return (
                            <FormItem key={model.id} className="flex flex-col space-y-2">
                              <div className="flex items-start space-x-3 space-y-0">
                                <FormControl>
                                  <Checkbox
                                    checked={field.value?.includes(model.id)}
                                    onCheckedChange={(checked) => {
                                      return checked
                                        ? field.onChange([...field.value, model.id])
                                        : field.onChange(field.value?.filter((value) => value !== model.id))
                                    }}
                                  />
                                </FormControl>
                                <FormLabel className="font-normal option">{model.label}</FormLabel>
                              </div>

                              {field.value?.includes(model.id) && (
                                <FormField
                                  control={form.control}
                                  name={`modelCons.${model.id}`}
                                  render={({ field: consField }) => (
                                    <FormItem>
                                      <FormControl>
                                        <Input className="cons-field" placeholder={`${model.label} Cons`} {...consField} />
                                      </FormControl>
                                    </FormItem>
                                  )}
                                />
                              )}
                            </FormItem>
                          )
                        }}
                      />
                    </div>
                  ))}
                  <FormMessage id="model_error" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="useCase"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Use Case</FormLabel>
                  <FormControl>
                    <Textarea id="use_case" placeholder="Describe your use case" className="resize-none" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button id="send-btn" type="submit" className="w-full" disabled={isSubmitting || !form.formState.isValid}>
              {isSubmitting ? "Sending..." : "Send"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
