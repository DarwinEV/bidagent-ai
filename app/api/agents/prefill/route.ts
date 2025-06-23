import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { db } from '@/lib/firebase'
import { doc, updateDoc, addDoc, collection } from 'firebase/firestore'

const BACKEND_API_URL = process.env.BACKEND_API_URL

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { bidId, companyData } = body

    const response = await fetch(`${BACKEND_API_URL}/api/run_prefill_agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userId, bidId, companyData }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Prefill agent failed:', errorText)
      throw new Error(`Prefill agent failed with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in prefill route:', error)
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred'
    return NextResponse.json({ error: 'Prefill failed', details: errorMessage }, { status: 500 })
  }
}
