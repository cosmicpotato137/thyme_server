import Button from "./widgets/Button";
import "./App.css";

function capFirstLetter(str) {
  // Check if the string is not empty
  if (str.length === 0) {
    return str;
  }

  // Capitalize the first letter and concatenate the rest of the string
  return str.charAt(0).toUpperCase() + str.slice(1);
}

const PairViewer = ({ pairings, setShowPairings, onRandomizeMatches }) => (
  <>
    {pairings.map((pair) => {
      return (
        <div>
          <p className="pair-text">{`${capFirstLetter(
            pair[0]
          )} gifts to ${capFirstLetter(pair[1])}`}</p>
        </div>
      );
    })}
    <Button
      style={{ position: "fixed", bottom: "20px", left: "10px" }}
      text={"Randomize matches"}
      onClick={onRandomizeMatches}
      size="large"
    ></Button>
    <Button
      style={{ position: "fixed", bottom: "20px", right: "10px" }}
      text={"<-"}
      onClick={() => setShowPairings(false)}
      size="large"
    ></Button>
  </>
);

export default PairViewer;
