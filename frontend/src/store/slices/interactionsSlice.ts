import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface InteractionsState {
  interactions: any[];
}

const initialState: InteractionsState = {
  interactions: [],
};

const interactionsSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {
    setInteractions: (state, action: PayloadAction<any[]>) => {
      state.interactions = action.payload;
    },
    addInteraction: (state, action: PayloadAction<any>) => {
      if (!state.interactions.some((item) => item.id === action.payload.id)) {
        state.interactions.unshift(action.payload);
      }
    },
    updateInteractionInList: (state, action: PayloadAction<any>) => {
      const index = state.interactions.findIndex((item) => item.id === action.payload.id);
      if (index !== -1) {
        state.interactions[index] = action.payload;
      }
    },
  },
});

export const { setInteractions, addInteraction, updateInteractionInList } = interactionsSlice.actions;
export default interactionsSlice.reducer;
