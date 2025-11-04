class IOStream {
  commands = [];
  terminal = null;

  constructor({ terminal }) {
    this.terminal = terminal;
  }

  out(data) {
    if (this.terminal && typeof this.terminal.write === "function") {
      this.terminal.write(data);
    }
  }

  receive(data) {
    // Logic to receive data from the terminal
    console.log("Receiving data:", data);
  }
}
