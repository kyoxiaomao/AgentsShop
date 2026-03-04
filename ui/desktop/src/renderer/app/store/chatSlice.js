import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  agents: [],
  statusMap: {},
  messages: [],
  activeAgentId: null,
  sending: false,
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setAgents: (state, action) => {
      state.agents = action.payload
    },
    setStatusMap: (state, action) => {
      state.statusMap = action.payload
    },
    setMessages: (state, action) => {
      state.messages = action.payload
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    updateLastMessage: (state, action) => {
      const lastMessage = state.messages[state.messages.length - 1]
      if (lastMessage && lastMessage.id === action.payload.id) {
        Object.keys(action.payload).forEach((key) => {
          if (key === 'id') return
          if (action.payload[key] === undefined) return
          lastMessage[key] = action.payload[key]
        })
      }
    },
    setActiveAgent: (state, action) => {
      state.activeAgentId = action.payload
    },
    setSending: (state, action) => {
      state.sending = action.payload
    },
  },
})

export const {
  setAgents,
  setStatusMap,
  setMessages,
  addMessage,
  updateLastMessage,
  setActiveAgent,
  setSending,
} = chatSlice.actions

export default chatSlice.reducer
