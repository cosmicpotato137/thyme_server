function santaSelector(groups) {
  // Validate the input
  if (
    !Array.isArray(groups) ||
    groups.length === 0 ||
    !groups.every(Array.isArray)
  ) {
    throw new Error("Invalid input. Please provide a 2D array of strings.");
  }
  if (groups.length === 0) return [];

  // Use reduce to create a dictionary mapping each string to its row
  const groupLookup = getGroupLookupTable(groups);
  // set the number of unmatched members in each group
  var keys = Object.keys(groupLookup);
  keys = shuffleArray(keys);

  // find the number of unmatched members in each group
  const unmatchedMembers = groups.map((group) => group.length);

  // check that the groups follow the triangle inequality
  let numMembers = keys.length; // total members in all groups
  groups.forEach((group, index) => {
    if (group.length > numMembers / 2) {
      throw new Error(
        `Group ${index} has too many members to create a complete mapping.`
      );
    }
  });

  var matches = [];

  // if (keys.length % 2 == 0) {
  var left = keys.slice(0, keys.length / 2);
  var right = keys.slice(keys.length / 2, keys.length);

  const start = right[0];
  var current = right[0];
  var onLeft = false;

  do {
    const groupID = groupLookup[current][0];

    // find the giving partner
    var maximalGroup = -1;
    var maximalVal = 0;
    unmatchedMembers.forEach((value, index) => {
      if (value >= maximalVal && index !== groupID) {
        maximalGroup = index;
        maximalVal = value;
      }
    });

    var partner = (onLeft ? right : left).find((member) => {
      return groupLookup[member][0] === maximalGroup && !groupLookup[member][2];
    });

    groupLookup[current][2] = true;

    // add matches
    if (partner === undefined) {
      partner = [...(onLeft ? right : left), ...(onLeft ? left : right)].find(
        (value) => {
          return (
            groupLookup[value][0] !== groupID &&
            (matches.length === 0 ||
              value !== matches[matches.length - 1][0]) &&
            !groupLookup[value][2]
          );
        }
      );

      if (partner === undefined) partner = start;
    }

    // append match
    matches.push([current, partner]);

    // degrement visited group
    unmatchedMembers[groupLookup[partner][0]] -= 1;

    // switch nodes
    onLeft = !onLeft;
    current = partner;
  } while (start !== current);
  // }

  return matches;
}

// Function to shuffle an array (Fisher-Yates algorithm)
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function getGroupLookupTable(groups) {
  return groups.reduce((mapping, row, rowIndex) => {
    row.forEach((value, index) => {
      mapping[value] = [rowIndex, index, false];
    });
    return mapping;
  }, {});
}

module.exports = {
  santaSelector,
  getGroupLookupTable,
};
