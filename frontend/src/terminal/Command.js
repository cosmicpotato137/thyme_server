/**
 * Represents a command parameter with description, required flag, and datatype.
 * If datatype is null, the parameter is treated as a flag (boolean).
 */
class Parameter {
  /**
   * @param {string} name - The name of the parameter.
   * @param {Function|null} datatype - The datatype constructor (e.g., String, Number) or null for flag.
   * @param {string} description - Description of the parameter.
   * @param {boolean} [required=false] - Whether the parameter is required.
   * @param {string|null} [alias=null] - Optional alias for the parameter.
   * @param {boolean} [positional=false] - Whether the parameter is positional.
   */
  constructor(
    name,
    datatype,
    description,
    required = false,
    alias = null,
    positional = false
  ) {
    this.name = name;
    this.description = description;
    this.required = required;
    this.datatype = datatype; // e.g., String, Number, null for flag
    this.alias = alias;
    this.positional = positional;
  }

  toString() {
    const aliasStr = this.alias ? `alias: -${this.alias}, ` : "";
    const typeName = "type: " + (this.datatype ? this.datatype.name : "flag");
    const requiredStr = this.required && !this.positional ? ", required" : "";
    const nameStr = this.positional ? `${this.name}` : `--${this.name}`;
    return `${nameStr} (${aliasStr}${typeName}${requiredStr}): ${this.description}`;
  }
}

/**
 * Represents a command with a callable, parameter hints, and a description.
 */
class Command {
  /**
   * @param {Function} func - The function to execute.
   * @param {string} [name] - Optional command name (defaults to func.name).
   * @param {string} [description=""] - Description of the command.
   * @param {Parameter[]} [params=[]] - List of Parameter instances.
   */
  constructor(func, name = null, description = "", params = []) {
    if (typeof func !== "function") {
      throw new Error("func must be a function");
    }
    this.func = func;
    this.name = name || func.name;
    this.description = description;
    this.params = params;

    // Check for duplicate parameter names or aliases
    const paramNames = new Set();
    const paramAliases = new Set();
    for (const p of this.params) {
      if (paramNames.has(p.name)) {
        throw new Error(
          "Duplicate parameter names found in command parameters."
        );
      }
      paramNames.add(p.name);
      if (p.alias) {
        if (paramAliases.has(p.alias)) {
          throw new Error(
            "Duplicate parameter aliases found in command parameters."
          );
        }
        paramAliases.add(p.alias);
      }
    }
  }

  /**
   * Calls the command function with validated arguments.
   * @param {Terminal} terminal - The terminal instance.
   * @param  {...any} args - Positional arguments.
   * @returns {*} - The result of the command function.
   */
  async call(terminal, ...args) {
    // Support for named arguments via last argument as object
    let kwargs = {};
    if (
      args.length &&
      typeof args[args.length - 1] === "object" &&
      !Array.isArray(args[args.length - 1])
    ) {
      kwargs = args.pop();
    }

    if (kwargs.h || kwargs.help) {
      return this.helpStatement();
    }

    let position = 0;
    const newKwargs = {};
    for (const param of this.params) {
      // Required named parameter
      if (
        param.required &&
        !param.positional &&
        !(param.name in kwargs) &&
        !(param.alias && param.alias in kwargs)
      ) {
        throw new Error(`Missing required parameter: ${param.name}`);
      }
      // Named or alias parameter
      if (param.name in kwargs || (param.alias && param.alias in kwargs)) {
        let value =
          param.alias && param.alias in kwargs
            ? kwargs[param.alias]
            : kwargs[param.name];
        if (param.datatype) {
          try {
            value = param.datatype(value);
          } catch (e) {
            throw new Error(
              `Invalid value for parameter '${param.name}': expected ${param.datatype.name}, got ${value}`
            );
          }
        }
        newKwargs[param.name] = value;
      }
      // Positional parameter
      if (param.positional) {
        if (position < args.length) {
          let value = args[position];
          if (param.datatype) {
            try {
              value = param.datatype(value);
            } catch (e) {
              throw new Error(
                `Invalid value for positional parameter '${param.name}': expected ${param.datatype.name}, got ${value}`
              );
            }
          }
          newKwargs[param.name] = value;
        } else if (param.required) {
          throw new Error(
            `Missing required positional parameter: ${param.name}`
          );
        }
        position += 1;
      }
    }
    console.debug(`Calling command: ${this.name} with args:`);
    console.debug(newKwargs);

    return await this.func(terminal, newKwargs);
  }

  /**
   * Returns a formatted help statement for the command.
   * @returns {string}
   */
  helpStatement() {
    const paramHints = this.params
      .map((param) => param.toString())
      .join("\n\t");
    return paramHints
      ? `${this.name} - ${this.description}\n\t${paramHints}`
      : `${this.name} - ${this.description}`;
  }

  /**
   * Returns parameter hints as a list.
   * @returns {Parameter[]}
   */
  getParamHints() {
    return this.params;
  }

  /**
   * Returns the command description.
   * @returns {string}
   */
  getDescription() {
    return this.description;
  }
}

export { Command, Parameter };
