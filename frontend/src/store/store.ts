import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import { agentApi } from "./api/agentApi";
import chatReducer from "./slices/chatSlice";
import hcpReducer from "./slices/hcpSlice";
import interactionsReducer from "./slices/interactionsSlice";
import uiReducer from "./slices/uiSlice";

export const store = configureStore({
  reducer: {
    [agentApi.reducerPath]: agentApi.reducer,
    chat: chatReducer,
    hcp: hcpReducer,
    interactions: interactionsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(agentApi.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
