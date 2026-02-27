import styled from 'styled-components'

const Panel = styled.div`
  position: absolute;
  right: 0;
  bottom: 64px;
  width: 200px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(25, 25, 25, 0.74);
  backdrop-filter: blur(10px);
  display: ${(p) => (p.$open ? 'flex' : 'none')};
  flex-direction: column;
  gap: 8px;
`

const Row = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
`

const ItemButton = styled.button`
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  text-align: left;
`

const Label = styled.div`
  color: rgba(255, 255, 255, 0.86);
  font-size: 12px;
`

const Range = styled.input`
  width: 120px;
`

export default function MenuPanel({
  open,
  onShowStatus,
  onReset,
  onQuit,
  speed,
  onSpeedChange,
}) {
  return (
    <Panel $open={open} data-interactive="menu">
      <ItemButton type="button" onClick={onShowStatus}>
        状态面板
      </ItemButton>
      <Row>
        <Label>速度</Label>
        <Range
          type="range"
          min={40}
          max={260}
          value={speed}
          onChange={(e) => onSpeedChange?.(Number(e.target.value))}
        />
      </Row>
      <ItemButton type="button" onClick={onReset}>
        重置位置
      </ItemButton>
      <ItemButton type="button" onClick={onQuit}>
        退出应用
      </ItemButton>
    </Panel>
  )
}
