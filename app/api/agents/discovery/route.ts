import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { db } from '@/lib/firebase'
import { collection, addDoc, query, where, orderBy, limit, getDocs } from 'firebase/firestore'

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { keywords, naicsCodes, geography, portals } = body

    // Simulate discovery process
    const mockDiscoveredBids = [
      {
        title: "HVAC Replacement for Building 42",
        agency: "State University of California",
        deadline: "2025-07-15",
        location: "Sacramento, CA",
        description: "Replace existing HVAC system with energy-efficient units...",
        portal: "SAM.gov",
        relevanceScore: 0.92,
        status: "new",
        userId,
        createdAt: new Date()
      },
      {
        title: "Plumbing Maintenance Services",
        agency: "City of San Francisco",
        deadline: "2025-06-30",
        location: "San Francisco, CA",
        description: "Annual plumbing maintenance for municipal buildings...",
        portal: "CA State Portal",
        relevanceScore: 0.87,
        status: "new",
        userId,
        createdAt: new Date()
      }
    ]

    // Store in Firestore
    const bidsCollection = collection(db, 'bids')
    const savedBids = []

    for (const bid of mockDiscoveredBids) {
      const docRef = await addDoc(bidsCollection, bid)
      savedBids.push({ id: docRef.id, ...bid })
    }

    // Log activity
    await addDoc(collection(db, 'activities'), {
      userId,
      type: 'discovery',
      message: `Found ${savedBids.length} new opportunities`,
      timestamp: new Date(),
      details: { keywords, naicsCodes, geography, portals }
    })

    return NextResponse.json({ 
      success: true, 
      bids: savedBids,
      message: `Discovery complete. Found ${savedBids.length} opportunities.`
    })
  } catch (error) {
    console.error('Discovery error:', error)
    return NextResponse.json({ error: 'Discovery failed' }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const bidsCollection = collection(db, 'bids')
    const q = query(
      bidsCollection,
      where('userId', '==', userId),
      orderBy('createdAt', 'desc'),
      limit(50)
    )
    
    const snapshot = await getDocs(q)
    const bids = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }))

    return NextResponse.json({ bids })
  } catch (error) {
    console.error('Get bids error:', error)
    return NextResponse.json({ error: 'Failed to fetch bids' }, { status: 500 })
  }
}
