import { useTheme } from '../../context/theme'
import Card from './Card'

export default function StateMessage({ children, tone = 'muted', gridColumn }) {
    const { T } = useTheme()
    const color = tone === 'error' ? T.down : T.muted
    const content = <p style={{ fontSize: 13, color }}>{children}</p>

    if (gridColumn) {
        return (
            <div style={{ gridColumn, textAlign: 'center', padding: 40, color, fontSize: 14 }}>
                {children}
            </div>
        )
    }

    return <Card>{content}</Card>
}
