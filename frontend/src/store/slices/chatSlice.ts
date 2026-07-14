import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
  status?: string;
  toolCalls?: Array<{ tool: string; args: any; output?: any }>;
  pendingConfirmation?: any;
}

interface ChatState {
  messages: Message[];
  sessionId: string;
  isStreaming: boolean;
  currentStatus: string;
  pendingConfirmation: any | null;
}

const initialState: ChatState = {
  messages: [],
  sessionId: `session-${Math.random().toString(36).substring(2, 11)}`,
  isStreaming: false,
  currentStatus: "",
  pendingConfirmation: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    updateLastAgentMessage: (state, action: PayloadAction<{ text: string }>) => {
      const agentMessages = state.messages.filter((m) => m.sender === "agent");
      if (agentMessages.length > 0) {
        const last = agentMessages[agentMessages.length - 1];
        last.text = action.payload.text;
      }
    },
    setStreaming: (state, action: PayloadAction<boolean>) => {
      state.isStreaming = action.payload;
    },
    setStatus: (state, action: PayloadAction<string>) => {
      state.currentStatus = action.payload;
    },
    setPendingConfirmation: (state, action: PayloadAction<any | null>) => {
      state.pendingConfirmation = action.payload;
    },
    addToolCallToLastMessage: (state, action: PayloadAction<{ tool: string; args: any; output?: any }>) => {
      const agentMessages = state.messages.filter((m) => m.sender === "agent");
      if (agentMessages.length > 0) {
        const last = agentMessages[agentMessages.length - 1];
        if (!last.toolCalls) last.toolCalls = [];
        if (!last.toolCalls.some((t) => t.tool === action.payload.tool)) {
          last.toolCalls.push(action.payload);
        }
      }
    },
    setToolCallsForLastMessage: (state, action: PayloadAction<any[]>) => {
      const agentMessages = state.messages.filter((m) => m.sender === "agent");
      if (agentMessages.length > 0) {
        const last = agentMessages[agentMessages.length - 1];
        last.toolCalls = action.payload;
      }
    },
    clearChat: (state) => {
      state.messages = [];
      state.pendingConfirmation = null;
      state.currentStatus = "";
    },
  },
});

export const {
  addMessage,
  updateLastAgentMessage,
  setStreaming,
  setStatus,
  setPendingConfirmation,
  addToolCallToLastMessage,
  setToolCallsForLastMessage,
  clearChat,
} = chatSlice.actions;
export default chatSlice.reducer;
