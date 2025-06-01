
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { DashboardContent } from '@/components/pages/DashboardContent'

export default async function Dashboard() {
  return <DashboardContent />
}