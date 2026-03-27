import { useState, useEffect } from 'react'

export function useNow() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60000)
    return () => clearInterval(id)
  }, [])
  const pad = n => String(n).padStart(2, '0')
  return `${now.getFullYear()}.${pad(now.getMonth()+1)}.${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
}