import React, { useState, forwardRef, useRef, useEffect } from "react";
import axios from "axios";

const clientCommands = {
  clear: (setHistory) => {
    setHistory("");
    return { message: "Terminal cleared.", level: "info", handled: true };
  },
  // Add more client-side commands here as needed
};

const textKeys = [
  "ArrowUp",
  "ArrowDown",
  "ArrowLeft",
  "ArrowRight",
  "Backspace",
  "Delete",
];

const Terminal = forwardRef(
  (
    {
      inputColor = "green",
      errorColor,
      backgroundColor = "black",
      style = {},
      msg = "",
    },
    ref
  ) => {
    const inputRef = useRef();
    const terminalRef = useRef();
    const keyHoldState = useRef({ ArrowUp: false, ArrowDown: false });
    const lastLineRef = useRef(null);

    const [autoScroll, setAutoScroll] = useState(true);
    const [loading, setLoading] = useState(false);

    const [currentPrompt, setCurrentPrompt] = useState("user@terminal:~$ ");
    const [command, setCommand] = useState("");
    const [history, setHistory] = useState(`${msg}\n${currentPrompt}`);
    const [commandHistoryIndex, setCommandHistoryIndex] = useState(-1); // -1 means not navigating
    const [commandHistory, setCommandHistory] = useState([]); // Store command history for navigation
    const [savedCommand, setSavedCommand] = useState(""); // Save current input when navigating

    const [caretPos, setCaretPos] = useState(0);
    const [cursorVisible, setCursorVisible] = useState(true);
    const [ignoreCursorInterval, setIgnoreCursorInterval] = useState(false);

    // --- Handle up/down arrow for command history navigation ---
    const handleHistoryNavigation = async (direction) => {
      let newIndex = commandHistoryIndex + direction;

      if (newIndex <= -1) {
        setCommandHistoryIndex(-1);
        setCommand(savedCommand);
        return;
      }

      setCommandHistoryIndex(newIndex);
      console.log("Navigating history:", commandHistoryIndex);

      // Fetch command history from client history
      if (newIndex < commandHistory.length) {
        setCommand(commandHistory[commandHistory.length - newIndex - 1]);
        return;
      }

      try {
        const res = await axios.get("http://127.0.0.1:8000/api/last-command", {
          params: { i: newIndex },
        });
        console.log("Command from history:", res.data.command);
        setCommand(res.data.command);
        setCommandHistoryIndex(res.data.i);
      } catch (error) {
        console.error("Error fetching command from history:", error);
      }
    };

    const handleInputKeyDown = (e) => {
      if (e.repeat) {
        // Key is being held down (auto-repeat)
        if (e.key === "ArrowUp" || e.key === "ArrowDown") {
          keyHoldState.current[e.key] = true;
        }
      }
      if (e.key === "ArrowUp" && !keyHoldState.current.ArrowUp) {
        e.preventDefault();
        handleHistoryNavigation(1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
      } else if (e.key === "ArrowDown" && !keyHoldState.current.ArrowDown) {
        e.preventDefault();
        handleHistoryNavigation(-1);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setCommandHistoryIndex(-1);
        setCommand(savedCommand);
      } else if (e.key === "Enter") {
        e.preventDefault();
        handleSubmit(e);
      } else if (e.key === "Escape") {
        e.preventDefault();
        setCommandHistoryIndex(-1); // Reset history navigation index
        setCommand(""); // Clear input on Escape
      }
    };

    // Interval to toggle cursor visibility
    useEffect(() => {
      const interval = setInterval(() => {
        if (!ignoreCursorInterval) {
          setCursorVisible((v) => !v);
        }
        setIgnoreCursorInterval(false);
      }, 530);
      return () => clearInterval(interval);
    }, [ignoreCursorInterval, cursorVisible]);

    // Listeners
    useEffect(() => {
      const handleKeyUp = (e) => {
        if (e.key === "ArrowUp" || e.key === "ArrowDown") {
          keyHoldState.current[e.key] = false;
        }
      };
      window.addEventListener("keyup", handleKeyUp);

      const handleKeyDown = (e) => {
        // Exclude ctrl and other hotkeys (e.g., Ctrl, Alt, Meta, Shift)
        if (e.ctrlKey || e.altKey || e.metaKey || e.commandKey) {
          console.log("Hotkey pressed:", e.key);
          // unfocus input
          if (!textKeys.includes(e.key) && inputRef.current) {
            inputRef.current.blur();
            return;
          } else if (textKeys.includes(e.key) && inputRef.current) {
            inputRef.current.focus();
          } else {
            return;
          }
        }

        setCursorVisible(true);
        if (inputRef.current) {
          inputRef.current.focus();
        }
        if (e.key === "ArrowUp" || e.key === "ArrowDown") {
          e.preventDefault(); // Prevent default scrolling behavior
        }
      };
      window.addEventListener("keydown", handleKeyDown);

      const handleScroll = () => {
        if (!terminalRef.current) return;
        const { scrollTop, scrollHeight, clientHeight } = terminalRef.current;
        // If user is at the bottom (within 5px), enable autoscroll
        if (scrollHeight - scrollTop - clientHeight < 5) {
          setAutoScroll(true);
        } else {
          setAutoScroll(false);
        }
      };
      const node = terminalRef.current;
      if (node) {
        node.addEventListener("scroll", handleScroll);
      }

      return () => {
        window.removeEventListener("keyup", handleKeyUp);
        window.removeEventListener("keydown", handleKeyDown);
        if (node) {
          node.removeEventListener("scroll", handleScroll);
        }
      };
    }, []);

    // Auto-scroll to bottom when history changes, if enabled
    useEffect(() => {
      if (autoScroll && terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    }, [history, autoScroll]);

    // Scroll to bottom when command changes
    useEffect(() => {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      if (commandHistoryIndex === -1) {
        setSavedCommand(command);
      }
    }, [command, commandHistoryIndex]);

    const handleInput = (e) => {
      setCommand(e.target.value);
      setCaretPos(e.target.selectionStart);
    };

    const handleInputSelect = (e) => {
      setCaretPos(e.target.selectionStart);
    };

    // Ensure caretPos is always valid
    useEffect(() => {
      if (caretPos > command.length) setCaretPos(command.length);
    }, [command, caretPos]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setCommand("");
      setSavedCommand("");
      setCommandHistoryIndex(-1); // Reset history navigation index
      let cmd = command.trim();
      setHistory((prev) => prev + cmd + "\n");

      if (loading) return;

      if (cmd.length !== 0) {
        setCommandHistory((prev) => [...prev, cmd]);
      }

      setCursorVisible(false);
      setLoading(true);

      // Check if the command should be handled on the client
      let result = {};
      if (clientCommands[cmd]) {
        if (cmd === "clear") {
          result = clientCommands[cmd](setHistory);
        }
      } else {
        result = {
          message: `Command not recognized: ${cmd}`,
          level: "error",
          handled: false,
        };
      }
      let res;
      // Get the current prompt
      try {
        res = await axios.get("http://127.0.0.1:8000/api/current-prompt");
        console.log("Current prompt from server:", res.data.prompt);
        if (res.data.prompt) {
          setCurrentPrompt(res.data.prompt);
        }
      } catch (error) {
        console.error("Error fetching current prompt:", error);
        setCurrentPrompt("user@terminal:~$ ");
      }

      // If not handled by client, send to server
      try {
        res = await axios.post("http://127.0.0.1:8000/api/terminal/", {
          command: cmd.trim(),
          handled: result.handled || false,
        });
        console.log("Response from server:", res.data);
        setHistory((prev) => prev + res.data.message);
      } catch (error) {
        setHistory((prev) => prev + error.message + "\n" + currentPrompt);
      }
      setLoading(false);
    };

    return (
      <div
        className="terminal"
        ref={terminalRef}
        style={{
          backgroundColor,
          color: inputColor,
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "scroll",
          ...style,
        }}
      >
        {history.split("\n").map((line, index, arr) => {
          let s = (
            <span
              style={{
                color: inputColor,
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
                display: "inline-block",
                width: "fit-content",
                maxWidth: "100%",
                cursor: "default",
              }}
            >
              {line}
            </span>
          );

          if (index === arr.length - 1) {
            lastLineRef.current = s;
            return (
              <span
                key={index}
                style={{
                  backgroundColor: backgroundColor,
                  color: inputColor,
                  border: "none",
                  outline: "none",
                  padding: "0px",
                  margin: "0px",
                  fontSize: "inherit",
                  fontFamily: "inherit",
                  lineHeight: "18.5px",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-all",
                  resize: "none",
                  cursor: "default",
                  zIndex: 2,
                }}
                tabIndex={0}
              >
                {s}
                {
                  // Render command with cursor at caretPos
                  (() => {
                    const before = command.slice(0, caretPos);
                    const after = command.slice(caretPos);
                    return (
                      <>
                        <span>{before}</span>
                        <span
                          style={{
                            display: "inline-block",
                            backgroundColor: cursorVisible
                              ? inputColor
                              : backgroundColor,
                            color: cursorVisible ? backgroundColor : inputColor,
                          }}
                        >
                          {after.length > 0 ? after[0] : "\u00A0"}
                        </span>
                        <span>{after.slice(1)}</span>
                        {command.length === 0 && (
                          <span style={{ opacity: 0.5 }}>&nbsp;</span>
                        )}
                      </>
                    );
                  })()
                }
              </span>
            );
          } else {
            return (
              <div key={index} style={{}}>
                {s}
              </div>
            );
          }
        })}
        <form
          onSubmit={handleSubmit}
          style={{
            position: "absolute",
            opacity: 0,
            pointerEvents: "none",
            height: 0,
            width: 0,
            top: 0,
            left: 0,
          }}
        >
          {/* Hidden input for actual input */}
          <input
            ref={inputRef}
            value={command}
            onChange={handleInput}
            onSelect={handleInputSelect}
            autoFocus
            autoComplete="off"
            style={{
              position: "absolute",
              opacity: 0,
              pointerEvents: "none",
              height: 0,
              width: 0,
              top: 0,
              left: 0,
            }}
            onKeyDown={handleInputKeyDown}
            tabIndex={-1}
          />
        </form>
      </div>
    );
  }
);

export default Terminal;
