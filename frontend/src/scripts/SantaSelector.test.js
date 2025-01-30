import { santaSelector, getGroupLookupTable } from "./SantaSelector";

function verifyMatching(input, matching) {
  const groupLookup = getGroupLookupTable(input);

  matching.forEach((element) => {
    // make sure match is in the correct format
    expect(element.length).toEqual(2);

    // chek that groups aren't paired
    expect(groupLookup[element[0]][0] === groupLookup[element[1]][0]).toEqual(
      false
    );

    // check for 2 cycles
    const p = matching.find((value) => value[0] === element[1]);
    expect(element[0] === p[1]).toEqual(false);
  });
}

test("even groups", () => {
  const input = [
    ["apple", "orange", "banana"],
    ["red", "green", "blue"],
  ];

  const result = santaSelector(input);

  // Use jest-dom's toEqual method for deep equality check
  verifyMatching(input, result);
});

test("check odd groups", () => {
  const input = [
    ["Alice", "Bob"],
    ["David", "Eva"],
    ["Jean", "Dunkirk"],
    ["Frankie", "Arnold", "Julie"],
  ];

  const result = santaSelector(input);

  verifyMatching(input, result);
});

test("check lots of groups", () => {
  const input = [
    ["a", "b", "c"],
    ["d", "e", "f", "g"],
    ["h", "i", "h", "k", "l", "m"],
    ["n"],
    ["o", "p"],
    ["q"],
  ];

  const result = santaSelector(input);

  verifyMatching(input, result);
});

test("check triangle inequality", () => {
  const input = [
    ["apple", "orange", "banana", "grape"],
    ["red", "green"],
    ["one"],
  ];

  expect(() => santaSelector(input)).toThrow(Error);
});

test("check for invalid input", () => {
  expect(() => santaSelector(1)).toThrow(Error);
  expect(() => santaSelector([1, 1, 1])).toThrow(Error);
  expect(() =>
    santaSelector([
      [1, 1, 1],
      [1, 1],
    ])
  ).toThrow(Error);
});
