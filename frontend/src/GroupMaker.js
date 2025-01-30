import Textbox from "./widgets/Textbox";
import Button from "./widgets/Button";
import { useState, useRef, useEffect, createRef } from "react";

const GroupMaker = ({
  groups,
  setGroups,
  onFindMatches,
  addMember,
  removeGroup,
  removeMember,
  updateMember,
}) => {
  // Function to create and return a ref

  // Create a 2D array of refs
  const [textboxRefs, setTextboxRefs] = useState([]);
  // const [fgroup, setFgroup] = useState(-1);

  // useEffect to focus on the last textbox after the component mounts
  useEffect(() => {
    setTextboxRefs(groups.map(() => createRef()));
    //   console.log(groups);
    //   console.log(textboxRefs);
    //   if (fgroup < 0 || textboxRefs.length < groups.length) return;
    //   // Check if the last ref is defined before calling focus
    //   const lastRef = textboxRefs[fgroup][textboxRefs[fgroup].length - 1];
    //   if (lastRef.current) {
    //     lastRef.current.focus();
    //   }
  }, [groups]); // Include textboxes in the dependency array if it might change

  return (
    <div style={{ marginBottom: "200px" }}>
      {groups.map((group, groupID) => {
        return (
          <div>
            {/* group specific rendering */}
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <h2>{`Group ${groupID}`}</h2>
              <Button
                style={{ marginLeft: "20px" }}
                text="Add member"
                size="medium"
                onClick={() => {
                  addMember(groupID, "");
                  // setFgroup(groupID);
                }}
              ></Button>
              <Button
                text="Delete"
                size="medium"
                onClick={() => removeGroup(groupID)}
              ></Button>
            </div>
            <div
              style={{
                width: "100%",
                maxWidth: "800px",
                margin: "20px auto 40px",
                padding: "0px 20px",
                display: "flex",
                flexDirection: "row",
                flexWrap: "wrap",
                justifyContent: "center",
              }}
            >
              {/* render each textbox of the group */}
              {group.map((member, memberID) => {
                return (
                  <div
                    style={{
                      width: "fit-content",
                      display: "flex",
                      flexDirection: "row",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Textbox
                      // ref={
                      //   textboxRefs.length != 0 &&
                      //   textboxRefs[groupID][memberID]
                      // }
                      key={groupID * memberID}
                      style={{ margin: "10px" }}
                      defaultText={"Member name"}
                      currentText={member}
                      changeText={(event) => {
                        updateMember(groupID, memberID, event.target.value);
                      }}
                      // onClick={() => setFgroup(groupID)}
                      onEscape={() => removeMember(groupID, memberID)}
                      onEnter={() => addMember(groupID, "")}
                    ></Textbox>
                    <Button
                      style={{ margin: "10px" }}
                      text="X"
                      size="small"
                      onClick={() => removeMember(groupID, memberID)}
                    ></Button>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
      <Button
        style={{
          position: "fixed",
          bottom: "100px",
          left: "10px",
        }}
        text="Add Group"
        onClick={() => setGroups((prev) => [...prev, []])}
        size="large"
      ></Button>
      <Button
        style={{
          position: "fixed",
          bottom: "20px",
          right: "10px",
        }}
        text="Find Matches"
        onClick={onFindMatches}
        size="large"
      ></Button>
      <Button
        style={{
          position: "fixed",
          bottom: "20px",
          left: "10px",
        }}
        text="Reset groups"
        onClick={() => {
          setGroups([]);
        }}
        size="large"
      ></Button>
    </div>
  );
};
export default GroupMaker;
