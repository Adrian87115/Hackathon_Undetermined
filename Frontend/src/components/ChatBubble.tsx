import { useEffect, useState } from "react";
import styles from "./ChatBubble.module.css";

interface ChatBubbleProps {
  role: "user" | "assistant";
  children: React.ReactNode;
  animate?: boolean;
}

export default function ChatBubble({ role, children, animate}: ChatBubbleProps) {
  const isTypingBubble =
    typeof children === "string" &&
    children.toLowerCase().includes("typing");

  const isUser = role === "user";

  const [displayedText, setDisplayedText] = useState("");
  const [playAnim, setPlayAnim] = useState(false);


  // Animate text only for assistant messages, not user, not typing bubble
  useEffect(() => {
    if (isUser || isTypingBubble) {
      setDisplayedText(children as string);
      return;
    }

    let i = 0;
    const text = children as string;

    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i));
      i++;
      if (i > text.length) clearInterval(interval);
    }, 0.2); // typing speed

    return () => clearInterval(interval);
  }, [children]);

  useEffect(() => {
    if (animate) {
      setPlayAnim(false);           // restart
      requestAnimationFrame(() => { // ensure DOM refresh
        setPlayAnim(true);
      });
    }
  }, [animate]);

  return (
    <div className={`${isUser ? styles.userBubble : styles.assistantBubble}
      ${playAnim ? styles.changeAnim : ""}`}>
      {isTypingBubble ? (
        <div className={styles.typingIndicator}>
          <span></span><span></span><span></span>
        </div>
      ) : (
        <span className={styles.typeText}>{displayedText}</span>
      )}
    </div>
  );
}
