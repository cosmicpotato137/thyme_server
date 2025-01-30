import "./App.css";
import { useState } from "react";
import { santaSelector } from "./scripts/SantaSelector";

import GroupMaker from "./GroupMaker";
import PairViewer from "./PairViewer";

function App() {
  const [groups, setGroups] = useState([]);
  const [pairings, setPairings] = useState([]);
  const [showPairings, setShowPairings] = useState(false);

  const updateGroup = (groupID, newgroup) => {
    // Create a new array with the updated subarray
    const updatedArray = [
      ...groups.slice(0, groupID), // Copy arrays before the target
      newgroup, // Updated subarray
      ...groups.slice(groupID + 1), // Copy arrays after the target
    ];
    setGroups(updatedArray);
  };

  const removeGroup = (groupID) => {
    const newgroups = [
      ...groups.slice(0, groupID),
      ...groups.slice(groupID + 1),
    ];
    setGroups(newgroups);
  };

  // Function to update a specific subarray
  const updateMember = (groupID, memberID, member) => {
    // Find the index of the subarray
    const newgroup = [
      ...groups[groupID].slice(0, memberID),
      member,
      ...groups[groupID].slice(memberID + 1),
    ];
    updateGroup(groupID, newgroup);
    return member;
  };

  const addMember = (groupID, member) => {
    const newgroup = [...groups[groupID], member];

    updateGroup(groupID, newgroup);
  };

  const removeMember = (groupID, memberID) => {
    const newgroup = [
      ...groups[groupID].slice(0, memberID),
      ...groups[groupID].slice(memberID + 1),
    ];
    updateGroup(groupID, newgroup);
  };

  return (
    <div className="App">
      <h1>Super Secret Santa Selector</h1>
      {!showPairings && (
        <GroupMaker
          groups={groups}
          updateGroup={updateGroup}
          updateMember={updateMember}
          addMember={addMember}
          removeGroup={removeGroup}
          removeMember={removeMember}
          onFindMatches={() => {
            try {
              setPairings(santaSelector(groups));
            } catch (error) {}
            setShowPairings(true);
          }}
          setGroups={setGroups}
        ></GroupMaker>
      )}
      {showPairings && (
        <PairViewer
          pairings={pairings}
          setShowPairings={setShowPairings}
          onRandomizeMatches={() => {
            try {
              setPairings(santaSelector(groups));
            } catch (error) {}
          }}
        ></PairViewer>
      )}
    </div>
  );
}

export default App;
