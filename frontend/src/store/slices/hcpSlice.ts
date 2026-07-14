import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface HcpState {
  hcps: any[];
}

const initialState: HcpState = {
  hcps: [],
};

const hcpSlice = createSlice({
  name: "hcp",
  initialState,
  reducers: {
    setHcps: (state, action: PayloadAction<any[]>) => {
      state.hcps = action.payload;
    },
  },
});

export const { setHcps } = hcpSlice.actions;
export default hcpSlice.reducer;
