import { Command, Parameter } from "./Command.js";
import axios from "axios";
// Assuming Command and InputHandler are defined elsewhere

class TerminalContext {
  constructor(prompt = "> ", commands = []) {
    this.prompt = prompt;

    this._commands = {
      help: new Command(
        (terminal) => {
          terminal.out(this.helpStatement());
          terminal.br();
        },
        "help",
        "List all available commands.",
        []
      ),
    };
    for (const command of commands) {
      this.attachCommand(command);
    }

    console.debug(this._commands);
  }

  _parseCommand(commandStr) {
    const commandSplit = commandStr.trim().split(/\s+/);
    const command = commandSplit[0] || null;
    const args = [];
    const kwargs = {};

    for (let i = 1; i < commandSplit.length; i++) {
      const item = commandSplit[i];
      if (item.startsWith("--") && item.includes("=")) {
        // --option=value
        const [key, value] = item.slice(2).split("=", 2);
        kwargs[key] = value;
      } else if (item.startsWith("--")) {
        // --option value or --option
        const key = item.slice(2);
        if (
          i + 1 < commandSplit.length &&
          !commandSplit[i + 1].startsWith("-")
        ) {
          kwargs[key] = commandSplit[i + 1];
          i++;
        } else {
          kwargs[key] = true;
        }
      } else if (item.startsWith("-") && item.includes("=")) {
        // -o=value
        const [key, value] = item.slice(1).split("=", 2);
        kwargs[key] = value;
      } else if (item.startsWith("-")) {
        // -o value or -o
        const key = item.slice(1);
        if (
          i + 1 < commandSplit.length &&
          !commandSplit[i + 1].startsWith("-")
        ) {
          kwargs[key] = commandSplit[i + 1];
          i++;
        } else {
          kwargs[key] = true;
        }
      } else {
        args.push(item);
      }
    }

    return [command, args, kwargs];
  }

  handleInput(terminal, e) {
    console.debug(`Handling hotkey: ${e}`);

    if (e.ctrlKey && e.key === "c") {
      terminal.clearInput("^C");
      if (!terminal.isWaiting()) terminal.out(this.prompt);
      terminal.setWaiting(false);
      return;
    }
  }

  async handleCommand(terminal, input) {
    if (input.trim() === "") {
      return "";
    }

    const [command, args, kwargs] = this._parseCommand(input);
    console.debug(
      `Handling input: command=${command}, args=${JSON.stringify(
        args
      )}, kwargs=${JSON.stringify(kwargs)}`
    );

    if (!this._commands.hasOwnProperty(command)) {
      terminal.out("Command not found.\n");
      return;
    }

    try {
      let matchedCommand = null;
      for (const key in this._commands) {
        if (key === command) {
          matchedCommand = this._commands[key];
          break;
        }
      }
      if (!matchedCommand) {
        terminal.out("Command not found.\n");
        return;
      }
      if (kwargs.help || kwargs.h) {
        terminal.out(matchedCommand.helpStatement());
        terminal.br();
      }

      console.debug(`Executing command: ${matchedCommand.name}`);
      terminal.setWaiting(true);
      await matchedCommand.call(terminal, ...args, kwargs);
      terminal.setWaiting(false);
    } catch (e) {
      terminal.out(`Error executing command '${command}': ${e}\n`);
      terminal.setWaiting(false);
    }
  }

  attachCommand(command) {
    if (!(command instanceof Command)) {
      throw new Error("All commands must be instances of Command class.");
    }
    if (this._commands.hasOwnProperty(command.name)) {
      console.warn(
        `Command '${command.name}' is already attached. Overwriting it.`
      );
    }
    this._commands[command.name] = command;
  }

  detachCommand(name) {
    if (this._commands.hasOwnProperty(name)) {
      delete this._commands[name];
    }
  }

  helpStatement() {
    return Object.values(this._commands)
      .map((cmd) => cmd.helpStatement())
      .join("\n");
  }

  createRelation(
    terminal,
    child,
    commandName,
    commandDescription = "",
    welcomeMessage = ""
  ) {
    const switchTerminals = () => {
      terminal.pushContext(child);
      terminal.out(welcomeMessage);
      terminal.br();
    };

    const exitTerminal = () => {
      terminal.popContext();
      terminal.out("Bye!\n");
    };

    this.attachCommand(
      new Command(switchTerminals, commandName, commandDescription)
    );
    child.attachCommand(
      new Command(exitTerminal, "exit", "Exit the current terminal")
    );
  }
}

const default_context = new TerminalContext("user@terminal:~$ ", [
  new Command(
    (terminal) => {
      terminal.clearHistory();
    },
    "clear",
    "Clears the terminal output.",
    []
  ),
  new Command(
    (terminal) => {
      terminal.out(terminal.props.msg || "Hello, World!");
      terminal.br();
    },
    "msg",
    "Outputs the welcome message.",
    []
  ),
  new Command(
    async (terminal, args) => {
      console.debug(args.url);
      terminal.out("Attempting to ping GitHub API...\n");
      terminal.out("Press Ctrl+C to cancel.\n");
      let count = 0;
      await new Promise((resolve) => {
        const intervalId = setInterval(async () => {
          if (count >= 4 || !terminal.isWaiting()) {
            clearInterval(intervalId);
            resolve();
            terminal.out("Ping process completed.\n");
            return;
          }
          try {
            const response = await axios.get(`https://${args.url}`);

            if (response.status === 200) {
              terminal.out(
                `Ping ${count} successful! Status: ${response.status}\n`
              );
            } else {
              terminal.out(`Ping attempt ${count} failed\n`);
            }
          } catch (error) {
            terminal.out(`Ping attempt ${count} failed: ${error.message}\n`);
          }
          count += 1;
        }, 1000);
      });
    },
    "ping",
    "Pings a website to check connectivity.",
    [new Parameter("url", String, "URL to ping", true, false, true)]
  ),
  new Command(
    async (terminal) => {
      let dots = "Loading";
      terminal.out(dots);
      await new Promise(async (resolve) => {
        const intervalId = setInterval(() => {
          if (!terminal.isWaiting()) {
            terminal.out("Done wating.\n");
            clearInterval(intervalId);
            resolve();
            return;
          }
          const history = terminal.getHistory().split("\n");
          history.pop(); // Remove last line
          history.push(dots);
          terminal.setHistory(history.join("\n"));
          dots += ".";
          if (dots.length > 10) {
            dots = "Loading";
          }
        }, 500);
      });
    },
    "wait",
    "Simulates a loading process with dots.",
    []
  ),
  new Command(
    (terminal) => {
      terminal.out("Closing the terminal...\n");
      window.close();
    },
    "exit",
    "Closes the terminal.",
    []
  ),
  new Command(
    (terminal) => {
      terminal.out("Reloading the page...\n");
      window.location.reload();
    },
    "reload",
    "Reloads the page.",
    []
  ),
]);

export default TerminalContext;
export { default_context };
