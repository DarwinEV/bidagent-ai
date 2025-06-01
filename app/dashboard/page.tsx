
import { auth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'
import { DashboardContent } from '@/components/pages/DashboardContent'

export default function Dashboard() {
  const { userId } = auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return <DashboardContent />
}