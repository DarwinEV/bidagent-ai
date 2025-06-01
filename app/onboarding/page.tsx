
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { OnboardingContent } from '@/components/pages/OnboardingContent'

export default async function Onboarding() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return <OnboardingContent />
}