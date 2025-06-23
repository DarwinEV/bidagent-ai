import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'

const BACKEND_API_URL = process.env.BACKEND_API_URL;

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { bidId } = body

    if (!bidId) {
      return NextResponse.json({ error: 'Missing bidId' }, { status: 400 })
    }

    const response = await fetch(`${BACKEND_API_URL}/api/run_analysis_agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bidId, userId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Analysis agent failed:", errorText);
      throw new Error(`Analysis agent failed with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in analysis route:', error)
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    return NextResponse.json({ error: 'Analysis failed', details: errorMessage }, { status: 500 })
  }
}
