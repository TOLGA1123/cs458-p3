import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, PlusCircle } from "lucide-react"

export default function HomePage() {
  return (
    <div className="container mx-auto py-16 px-4 max-w-5xl">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Survey Creator</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Create custom surveys with multiple question types and conditional logic. Collect and analyze responses
          easily.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
        <div className="bg-slate-50 p-8 rounded-lg text-center flex flex-col items-center">
          <PlusCircle className="h-12 w-12 mb-4 text-primary" />
          <h2 className="text-2xl font-semibold mb-2">Create New Survey</h2>
          <p className="mb-6 text-muted-foreground">
            Design a custom survey with multiple question types, conditional logic, and more.
          </p>
          <Button asChild size="lg">
            <Link href="/create-survey">Create Survey</Link>
          </Button>
        </div>

        <div className="bg-slate-50 p-8 rounded-lg text-center flex flex-col items-center">
          <FileText className="h-12 w-12 mb-4 text-primary" />
          <h2 className="text-2xl font-semibold mb-2">View Saved Surveys</h2>
          <p className="mb-6 text-muted-foreground">
            Access your previously created surveys, edit them, or collect responses.
          </p>
          <Button asChild size="lg" variant="outline">
            <Link href="/saved-surveys">View Surveys</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
