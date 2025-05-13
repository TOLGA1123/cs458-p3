// route.ts
import { NextResponse } from "next/server"
import fs from "fs/promises"
import path from "path"

export async function POST(request: Request) {
  const dataDir  = path.join(process.cwd(), "data")
  const filePath = path.join(dataDir, "saved_surveys.json")

  // ensure data folder exists
  try { await fs.access(dataDir) }
  catch { await fs.mkdir(dataDir) }

  // read or initialize the file
  let all: any[] = []
  try {
    const raw = await fs.readFile(filePath, "utf-8")
    all = JSON.parse(raw)
  } catch (e: any) {
    if (e.code === "ENOENT") {
      await fs.writeFile(filePath, JSON.stringify(all, null, 2), "utf-8")
    } else {
      return NextResponse.json({ success: false, message: e.message }, { status: 500 })
    }
  }

  // append the new survey
  try {
    const body = await request.json()
    const id   = all.length
    all.push({ id, ...body })
    await fs.writeFile(filePath, JSON.stringify(all, null, 2), "utf-8")
    return NextResponse.json({ success: true, id })
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 })
  }
}
