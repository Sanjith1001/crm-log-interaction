import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type PageView = "login" | "log" | "history" | "hcp";

interface UiState {
  currentPage: PageView;
  activeMode: "form" | "chat";
}

const initialState: UiState = {
  currentPage: "log",
  activeMode: "chat",
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setCurrentPage: (state, action: PayloadAction<PageView>) => {
      state.currentPage = action.payload;
    },
    setActiveMode: (state, action: PayloadAction<"form" | "chat">) => {
      state.activeMode = action.payload;
    },
  },
});

export const { setCurrentPage, setActiveMode } = uiSlice.actions;
export default uiSlice.reducer;
