import { useEffect, useState } from 'react'
import styled from 'styled-components'
import { electronApi } from '../env'

const Backdrop = styled.div`
  position: fixed;
  inset: 0;
  display: ${(p) => (p.$open ? 'grid' : 'none')};
  place-items: center;
  background: rgba(0, 0, 0, 0.35);
  pointer-events: auto;
`

const Card = styled.div`
  width: 360px;
  max-width: calc(100vw - 32px);
  border-radius: 14px;
  background: rgba(25, 25, 25, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(12px);
  padding: 12px;
  color: rgba(255, 255, 255, 0.9);
`

const TitleRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
`

const Title = styled.div`
  font-size: 14px;
  font-weight: 600;
`

const Close = styled.button`
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.92);
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
`

const Pre = styled.pre`
  margin: 0;
  padding: 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  max-height: 260px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.4;
`

export default function StatusPanel({ open, onClose }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!open) return
    let mounted = true
    Promise.resolve(electronApi?.getStatus?.())
      .then((res) => {
        if (!mounted) return
        setData(res ?? { error: '未连接到 Electron 主进程' })
      })
      .catch((e) => {
        if (!mounted) return
        setData({ error: String(e?.message ?? e) })
      })
    return () => {
      mounted = false
    }
  }, [open])

  return (
    <Backdrop
      $open={open}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.()
      }}
    >
      <Card>
        <TitleRow>
          <Title>状态面板</Title>
          <Close type="button" onClick={onClose}>
            关闭
          </Close>
        </TitleRow>
        <Pre>{JSON.stringify(data ?? {}, null, 2)}</Pre>
      </Card>
    </Backdrop>
  )
}

