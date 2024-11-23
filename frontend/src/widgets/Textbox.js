import "./Widgets.css";

export default function Textbox({
  style,
  defaultText,
  currentText,
  changeText,
  onEscape,
  onEnter,
}) {
  return (
    <input
      style={style}
      className="textbox"
      type="text"
      value={currentText}
      onChange={changeText}
      placeholder={defaultText}
      onKeyDown={(event) => {
        if (event.key == "Escape") onEscape();
        else if (event.key == "Enter") onEnter();
      }}
    />
    // <div style={style} className="textbox">
    //   <p>{currentText && currentText === "" ? currentText : defaultText}</p>
    // </div>
  );
}
