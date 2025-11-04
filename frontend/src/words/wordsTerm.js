import TerminalContext from "../terminal/TerminalContext";
import { Command, Parameter } from "../terminal/Command";
import thymeClient from "../client/thymeClient";

function prettyPrintWordResult(obj) {
  if (!obj || typeof obj !== "object") return String(obj);
  const { message, data } = obj;
  if (!data || typeof data !== "object") return message || String(obj);

  return (
    `Word: ${data.word}\n` +
    `Language: ${data.language_display} (${data.language})\n` +
    `ID: ${data.id}\n` +
    `Last Seen: ${data.last_seen}\n` +
    `Strength: ${data.strength}\n` +
    `Synonyms: ${Array.isArray(data.synonyms) ? data.synonyms.join(", ") : ""}\n` +
    (message ? `Message: ${message}` : "")
  );
}

const words_context = new TerminalContext("words> ", [
  new Command(
    async (terminal, args) => {
      await thymeClient
        .get("/word/", { params: args })
        .then((response) => {
          terminal.out(prettyPrintWordResult(response.data));
          console.log(response.data);
          terminal.br();
        })
        .catch((error) => {
          terminal.out(error.response?.data.error || error.message);
          terminal.br();
        });
    },
    "find",
    "Find a word in the database.",
    [
      new Parameter("word", String, "word to find", true, null, true),
      new Parameter("language", String, "language", false, null, true),
    ]
  ),
  new Command(
    async (terminal, args) => {
      await thymeClient
        .get("/list-words/", {
          params: {
            language: args.language,
            page: args.page,
            per_page: args.per_page,
          },
        })
        .then((response) => {
          terminal.out(
            `Showing page ${response.data.page} of ${response.data.pages}.\n`
          );
          for (const item of response.data.data) {
            terminal.out(
              `${item.word}, ${item.language_display}, ${item.strength}`
            );
            terminal.br();
          }

          console.log(response.data.message);
        })
        .catch((error) => {
          terminal.out(error);
          terminal.br();
        });
    },
    "list",
    "Get a paginated list of words",
    [
      new Parameter(
        "language",
        String,
        "language to filter by",
        false,
        "l",
        false
      ),
      new Parameter("page", Number, "page of words", false, "p", false),
      new Parameter("per_page", Number, "results per page", false, "n", false),
    ]
  ),
  // Add word (POST /post-word/)
  new Command(
    async (terminal, args) => {
      await thymeClient
        .post("/post-word/", {
          word: args.word,
          language: args.language,
        })
        .then((response) => {
          terminal.out(response.data.message);
          terminal.br();
        })
        .catch((error) => {
          terminal.out(error.response?.data.error || error.message);
          terminal.br();
        });
    },
    "add",
    "Add a new word to the database.",
    [
      new Parameter("word", String, "word to add", true, null, true),
      new Parameter("language", String, "language", true, null, true),
    ]
  ),
  // Delete word (DELETE /delete-word/)
  new Command(
    async (terminal, args) => {
      await thymeClient
        .delete("/delete-word/", {
          data: {
            word: args.word,
            language: args.language,
          },
        })
        .then((response) => {
          terminal.out(response.data.message);
          terminal.br();
        })
        .catch((error) => {
          terminal.out(error.response?.data.error || error.message);
          terminal.br();
        });
    },
    "delete",
    "Delete a word from the database.",
    [
      new Parameter("word", String, "word to delete", true, null, true),
      new Parameter("language", String, "language", false, null, false),
    ]
  ),
  // Get random word (GET /random-word/)
  new Command(
    async (terminal, args) => {
      await thymeClient
        .get("/random-word/", {
          params: {
            language: args.language,
          },
        })
        .then((response) => {
          terminal.out(prettyPrintWordResult(response.data));
          terminal.br();
        })
        .catch((error) => {
          terminal.out(error.response?.data.error || error.message);
          terminal.br();
        });
    },
    "random",
    "Get a random word from the database.",
    [
      new Parameter("language", String, "language", true, null, true),
    ]
  ),
  // Update word synonyms (POST /update-word-synonyms/)
  new Command(
    async (terminal, args) => {
      await thymeClient
        .post("/update-word-synonyms/", {
          word: args.word,
          language: args.language,
          synonym_list: args.synonym_list,
          synonym_language: args.synonym_language,
        })
        .then((response) => {
          terminal.out(response.data.message);
          terminal.br();
        })
        .catch((error) => {
          terminal.out(error.response?.data.error || error.message);
          terminal.br();
        });
    },
    "synonyms",
    "Update the synonyms for a word.",
    [
      new Parameter("word", String, "word to update", true, null, true),
      new Parameter("language", String, "language", true, null, true),
      new Parameter("synonym_list", String, "comma-separated list of synonyms", true, null, true),
      new Parameter("synonym_language", String, "language of synonyms", true, null, true),
    ]
  ),
]);

export default words_context;
