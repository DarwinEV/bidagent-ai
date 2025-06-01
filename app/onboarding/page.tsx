
import { auth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'
import { OnboardingContent } from '@/components/pages/OnboardingContent'

export default function Onboarding() {
  const { userId } = auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return <OnboardingContent />
}