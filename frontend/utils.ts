export const getProgressPercentage = (status: any): number => {
  if (!status?.progress) return 0
  return Math.round((status.progress.completed / status.progress.total) * 100)
}

export const getStatusClass = (state: string): string => {
  const classes: Record<string, string> = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    STARTED: 'bg-blue-100 text-blue-800',
    PROGRESS: 'bg-blue-100 text-blue-800',
    SUCCESS: 'bg-green-100 text-green-800',
    FAILURE: 'bg-red-100 text-red-800'
  }
  return classes[state] || 'bg-gray-100 text-gray-800'
}

