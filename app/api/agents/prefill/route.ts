import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { db } from '@/lib/firebase'
import { doc, updateDoc, addDoc, collection } from 'firebase/firestore'

const PREFILL_AGENT_API_URL = "http://127.0.0.1:8000"

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { bidId, companyData } = body

    // Simulate pre-filling process
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Update bid status
    const bidRef = doc(db, 'bids', bidId)
    await updateDoc(bidRef, {
      status: 'pre-filled',
      preFilledAt: new Date(),
      preFilledData: companyData,
      preFilledPath: `/prefilled_bids/${userId}/${bidId}.pdf`
    })

    // Log activity
    await addDoc(collection(db, 'activities'), {
      userId,
      type: 'prefill',
      message: 'Forms pre-filled successfully',
      timestamp: new Date(),
      bidId
    })

    return NextResponse.json({ 
      success: true,
      message: 'Forms pre-filled successfully',
      preFilledPath: `/prefilled_bids/${userId}/${bidId}.pdf`
    })
  } catch (error) {
    console.error('Prefill error:', error)
    return NextResponse.json({ error: 'Pre-fill failed' }, { status: 500 })
  }
}
