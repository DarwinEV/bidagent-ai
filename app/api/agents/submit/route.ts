import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { db } from '@/lib/firebase'
import { doc, updateDoc, addDoc, collection } from 'firebase/firestore'

const SUBMIT_AGENT_API_URL = "http://127.0.0.1:8000"

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { bidId, submissionMethod, submissionEmail } = body

    // Simulate submission process
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Update bid status
    const bidRef = doc(db, 'bids', bidId)
    await updateDoc(bidRef, {
      status: 'submitted',
      submittedAt: new Date(),
      submissionMethod,
      submissionEmail
    })

    // Log activity
    await addDoc(collection(db, 'activities'), {
      userId,
      type: 'submission',
      message: `Bid submitted via ${submissionMethod}`,
      timestamp: new Date(),
      bidId
    })

    return NextResponse.json({ 
      success: true,
      message: `Bid submitted successfully via ${submissionMethod}`
    })
  } catch (error) {
    console.error('Submission error:', error)
    return NextResponse.json({ error: 'Submission failed' }, { status: 500 })
  }
}
