import React from "react";
import { default_context } from "./TerminalContext";
import thymeClient from "../client/thymeClient";
import words_context from "../words/wordsTerm";

class Terminal extends React.Component {
  textKeys = [
    "ArrowUp",
    "ArrowDown",
    "ArrowLeft",
    "ArrowRight",
    "Backspace",
    "Delete",
  ];

  constructor(props) {
    super(props);
    this.inputRef = React.createRef();
    this.terminalRef = React.createRef();
    this.keyHoldState = { ArrowUp: false, ArrowDown: false };
    this.state = {
      autoScroll: true,
      command: "",
      history: `${props.msg || ""}\n${default_context.prompt}`,
      commandHistoryIndex: -1,
      commandHistory: [],
      savedCommand: "",
      caretPos: 0,
      waiting: false,
    };
    this.terminalContext = [default_context];

    default_context.createRelation(
      this,
      words_context,
      "words",
      "Start the words terminal.",
      "Words terminal started."
    );
  }

  setWaiting(waiting) {
    this.setState({ waiting });
  }

  isWaiting() {
    return this.state.waiting;
  }

  out(data) {
    if (this.terminalRef.current) {
      this.setState((prev) => ({
        history: prev.history + data,
      }));
    }
  }

  br() {
    this.out("\n");
  }

  setHistory(history) {
    this.setState({ history });
  }

  getHistory() {
    return this.state.history;
  }

  clearHistory() {
    this.setState({ history: "" });
  }

  clearInput(postfixHistory="") {
    let cmd = this.state.command.trim();
    this.setState((prev) => ({
      command: "",
      savedCommand: "",
      commandHistoryIndex: -1,
      history: prev.history + cmd + postfixHistory + "\n",
      commandHistory:
        cmd.length !== 0 ? [...prev.commandHistory, cmd] : prev.commandHistory,
    }));
    return cmd;
  }

  async waitForInput(prompt = null) {
    if (prompt) {
      this.out(prompt);
    }
    return new Promise((resolve) => {
      const handleKeyDown = (e) => {
        if (e.key === "Enter" && this.state.command.trim() !== "") {
          e.preventDefault();
          window.removeEventListener("keydown", handleKeyDown);
          resolve();
        }
      };
      window.addEventListener("keydown", handleKeyDown);
    });
  }

  pushContext(context) {
    this.terminalContext.push(context);
    console.log(`Context pushed: ${context.prompt}\n`);
  }

  popContext() {
    if (this.terminalContext.length === 1) {
      this.out("No context to pop.\n");
      return;
    }
    const context = this.terminalContext.pop();
    this.out(`Context popped: ${context}\n`);
  }

  currentContext() {
    if (this.terminalContext.length === 0) {
      return null;
    }
    return this.terminalContext[this.terminalContext.length - 1];
  }

  componentDidMount() {
    window.addEventListener("keydown", this.handleKeyDown);

    if (this.terminalRef.current) {
      this.terminalRef.current.addEventListener("scroll", this.handleScroll);
    }

    thymeClient
      .get("/status/")
      .then((response) => {
        if (response.status !== 200) {
          console.error("Server is not responding correctly:", response.data);
        } else {
          console.log("Server is up and running.");
        }
      })
      .catch((error) => {
        console.error("Error checking server status:", error);
      });

    console.log("Command history: " + String(this.state.commandHistory));
  }

  componentWillUnmount() {
    window.removeEventListener("keydown", this.handleKeyDown);
    if (this.terminalRef.current) {
      this.terminalRef.current.removeEventListener("scroll", this.handleScroll);
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (
      this.state.autoScroll &&
      this.terminalRef.current &&
      prevState.history !== this.state.history
    ) {
      this.terminalRef.current.scrollTop =
        this.terminalRef.current.scrollHeight;
    }
    if (prevState.command !== this.state.command) {
      this.terminalRef.current.scrollTop =
        this.terminalRef.current.scrollHeight;
    }
    if (this.state.caretPos > this.state.command.length) {
      this.setState({ caretPos: this.state.command.length });
    }
  }

  submitCommand = async (e) => {
    e.preventDefault();
    let cmd = this.clearInput()

    thymeClient
      .post("/command-history/", { command: cmd })
      .then((response) => {})
      .catch((error) => {});

    await this.currentContext().handleCommand(this, cmd);
    this.out(this.currentContext().prompt);
  };

  navigateHistory = async (direction) => {
    let newIndex = this.state.commandHistoryIndex + direction;
    if (newIndex <= -1) {
      this.setState({
        commandHistoryIndex: -1,
        command: this.state.savedCommand,
      });
      return;
    }

    this.setState({ commandHistoryIndex: newIndex });
    if (newIndex < this.state.commandHistory.length) {
      this.setState({
        command:
          this.state.commandHistory[
            this.state.commandHistory.length - newIndex - 1
          ],
      });
      return;
    }

    await thymeClient
      .get("/last-command/", { params: { i: newIndex } })
      .then((response) => {
        this.setState({
          command: response.data.command,
          commandHistoryIndex: response.data.i,
        });
      })
      .catch((error) => {});
  };

  // Input should always be focused unless a modifier key is pressed
  handleKeyDown = (e) => {
    this.currentContext().handleInput(this, e);

    if (e.ctrlKey || e.altKey || e.metaKey || e.commandKey) {
      if (!this.textKeys.includes(e.key) && this.inputRef.current) {
        this.inputRef.current.blur();
        return;
      } else if (this.textKeys.includes(e.key) && this.inputRef.current) {
        this.inputRef.current.focus();
      } else {
        return;
      }
    }
    if (this.inputRef.current) {
      this.inputRef.current.focus();
    }
    if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      e.preventDefault();
    }
  };

  handleScroll = () => {
    if (!this.terminalRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = this.terminalRef.current;
    if (scrollHeight - scrollTop - clientHeight < 5) {
      this.setState({ autoScroll: true });
    } else {
      this.setState({ autoScroll: false });
    }
  };

  handleInputKeyDown = (e) => {
    if (this.isWaiting()) return;
    if (e.key === "ArrowUp") {
      e.preventDefault();
      this.navigateHistory(1);
    } else if (e.key === "ArrowDown" && !e.repeat) {
      e.preventDefault();
      this.navigateHistory(-1);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      this.setState({
        commandHistoryIndex: -1,
        command: this.state.savedCommand,
      });
    } else if (e.key === "Enter") {
      e.preventDefault();
      this.submitCommand(e);
    } else if (e.key === "Escape") {
      e.preventDefault();
      this.setState({ commandHistoryIndex: -1, command: "" });
    }
  };

  handleInputChange = (e) => {
    this.setState({
      command: e.target.value,
      savedCommand: e.target.value,
      caretPos: e.target.selectionStart,
    });
  };

  handleInputSelect = (e) => {
    this.setState({ caretPos: e.target.selectionStart });
  };

  render() {
    const {
      inputColor = "green",
      backgroundColor = "black",
      style = {},
    } = this.props;
    const { history, command, caretPos } = this.state;

    return (
      <div
        className="terminal"
        ref={this.terminalRef}
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
          return (
            <span
              key={index}
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
              {line || (index === arr.length - 1 ? "" : " ")}
              {index === arr.length - 1 &&
                (() => {
                  const before = command.slice(0, caretPos);
                  const after = command.slice(caretPos);
                  return (
                    <>
                      <span>{before}</span>
                      <span
                        style={{
                          display: "inline-block",
                          backgroundColor: inputColor,
                          color: backgroundColor,
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
                })()}
            </span>
          );
        })}
        <form
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
          <input
            ref={this.inputRef}
            value={command}
            onChange={this.handleInputChange}
            onSelect={this.handleInputSelect}
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
            onKeyDown={this.handleInputKeyDown}
            tabIndex={-1}
            disabled={this.isWaiting() ? "disabled" : ""}
          />
        </form>
      </div>
    );
  }
}

export default Terminal;
