import { useState, useEffect } from 'react'
import { useTheme } from '../../context/theme'

export default function ProgressBar({ value, color, height = 6, animated = true, bg }) {
    const { T } = useTheme()
    const c = color || T.up
    const [width, setWidth] = useState(0)
    useEffect(() => {
        const id = setTimeout(() => setWidth(value), animated ? 100 : 0)
        return () => clearTimeout(id)
    }, [animated, value])
    return (
        <div style={{ background: bg || T.border, borderRadius: 999, height, overflow: 'hidden' }}>
            <div style={{
                height: '100%', borderRadius: 999, background: c,
                width: `${width}%`,
                transition: animated ? 'width 0.7s cubic-bezier(0.4,0,0.2,1)' : 'none',
            }} />
        </div>
    )
}
