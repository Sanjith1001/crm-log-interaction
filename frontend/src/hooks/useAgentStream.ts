import { useDispatch, useSelector } from "react-redux";
  import { RootState } from "../store/store";
  import {
    addMessage,
    updateLastAgentMessage,
    setStreaming,
    setStatus,
    setPendingConfirmation,
    addToolCallToLastMessage,
    setToolCallsForLastMessage
  } from "../store/slices/chatSlice";

  export function useAgentStream() {
    const dispatch = useDispatch();
    const sessionId = useSelector((state: RootState) => state.chat.sessionId);
    const isStreaming = useSelector((state: RootState) => state.chat.isStreaming);
    const currentStatus = useSelector((state: RootState) => state.chat.currentStatus);

    const sendMessage = async (text: string, mode: "form" | "chat" = "chat") => {
      if (isStreaming) return;

      dispatch(addMessage({
        id: `msg-${Date.now()}-user`,
        sender: "user",
        text
      }));

      const agentMsgId = `msg-${Date.now()}-agent`;
      dispatch(addMessage({
        id: agentMsgId,
        sender: "agent",
        text: ""
      }));

      dispatch(setStreaming(true));
      dispatch(setStatus("Connecting..."));

      try {
        const response = await fetch("/api/agent/invoke", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            input_mode: mode,
            raw_input: text,
          }),
        });

        if (!response.body) throw new Error("No body in response");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let agentReplyText = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.substring(6));
                
                if (data.event === "status") {
                  dispatch(setStatus(data.text));
                } else if (data.event === "tool_start") {
                  dispatch(setStatus(`Calling tool: ${data.tool}...`));
                  dispatch(addToolCallToLastMessage({
                    tool: data.tool,
                    args: data.args
                  }));
                } else if (data.event === "tool_end") {
                  dispatch(setStatus(`Tool ${data.tool} finished.`));
                } else if (data.event === "token") {
                  agentReplyText += data.token;
                  dispatch(updateLastAgentMessage({ text: agentReplyText }));
                } else if (data.event === "final") {
                  dispatch(setStatus(""));
                  dispatch(setStreaming(false));
                  
                  if (data.tool_calls) {
                    dispatch(setToolCallsForLastMessage(data.tool_calls));
                  }
                  if (data.pending_confirmation) {
                    dispatch(setPendingConfirmation(data.pending_confirmation));
                  }
                }
              } catch (e) {
                console.error("SSE parse error:", e);
              }
            }
          }
        }
      } catch (err) {
        console.error("Streaming error:", err);
        dispatch(updateLastAgentMessage({ text: "Unable to reach the CRM agent. Check your connection." }));
        dispatch(setStreaming(false));
        dispatch(setStatus(""));
      }
    };

    return { sendMessage, isStreaming, currentStatus };
  }
