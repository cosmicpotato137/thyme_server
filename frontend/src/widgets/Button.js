import "./Widgets.css";

export default function Button({ style, text, onClick, size }) {
  return (
    <div style={style} className={`button-1 ${size}`} onClick={onClick}>
      <p className="button-text">{text}</p>
    </div>
  );
}
