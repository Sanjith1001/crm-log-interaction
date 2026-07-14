import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const agentApi = createApi({
  reducerPath: "agentApi",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: ["Interactions", "Hcps"],
  endpoints: (builder) => ({
    getInteractions: builder.query<any[], { query?: string; hcpId?: string } | void>({
      query: (arg) => {
        const params = new URLSearchParams();
        if (arg) {
          if (arg.query) params.append("query", arg.query);
          if (arg.hcpId) params.append("hcp_id", arg.hcpId);
        }
        const qs = params.toString();
        return { url: qs ? `/interactions?${qs}` : "/interactions" };
      },
      providesTags: ["Interactions"],
    }),
    getInteractionById: builder.query<any, string>({
      query: (id) => `/interactions/${id}`,
    }),
    getHcps: builder.query<any[], string | void>({
      query: (search) => search ? `/hcp?query=${search}` : "/hcp",
      providesTags: ["Hcps"],
    }),
    getHcpById: builder.query<any, string>({
      query: (id) => `/hcp/${id}`,
      providesTags: (result, error, id) => [{ type: "Hcps", id }],
    }),
  }),
});

export const {
  useGetInteractionsQuery,
  useGetInteractionByIdQuery,
  useGetHcpsQuery,
  useGetHcpByIdQuery,
} = agentApi;
