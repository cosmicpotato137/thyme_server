import React, { useEffect, useRef, useState } from "react";
import Terminal from "./Terminal";

function App() {
  const terminalRef = useRef(null);
  const [screenHeight, setScreenHeight] = useState(window.innerHeight);
  const [screenWidth, setScreenWidth] = useState(window.innerWidth);

  useEffect(() => {
    // Reset body styles
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.height = "100vh";
    document.body.style.overflow = "hidden";

    const handleResize = () => {
      setScreenHeight(window.innerHeight);
      setScreenWidth(window.innerWidth);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const padding = 5;

  return (
    <div style={{ margin: 0, padding: 0, height: "100vh", width: "100vw" }}>
      <Terminal
        inputColor="green"
        errorColor="red"
        backgroundColor="black"
        barColor="black"
        msg="Welcome to Terminal.js in React!"
        ref={terminalRef}
        style={{
          height: `${screenHeight - padding * 2}px`,
          width: `${screenWidth - padding * 2}px`,
          padding: `${padding}px`,
        }}
      />
    </div>
  );
}

export default App;
