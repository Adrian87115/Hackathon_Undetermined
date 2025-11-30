//v1
import { useState } from "react";
import styles from "./App.module.css";
import ChatBubble from "./components/ChatBubble";
import { sendToOpenAI } from "./api";
import WelcomeScreen from "./components/WelcomeScreen";

interface Message {
  role: "user" | "assistant";
  content: string;
  animate?: boolean;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isNewSession, setIsNewSession] = useState(true);
  const [briefChecked, setBriefChecked] = useState(false);



  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;


    setInput("");
    setLoading(true);
    setIsNewSession(false);

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

     try {
      const res = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      const data = await res.json();
      // setResponse(data.received);
      console.log(data.received);

      // setMessages((prev) => {
      // const updated = [...prev];
      // const lastIndex = updated.length - 1;

      // updated[lastIndex] = {
      //   ...updated[lastIndex],
      //   content: data.received   
      // };
      //       return updated;

      // });

      setMessages((prev) => {
        return prev.map((msg, i) => {
          if (i === prev.length - 1) {
            return {
              ...msg,
              content: data.received,
              animate: true,
            };
          }
          return { ...msg, animate: false };
        });
      });



      userMessage.content = data.received;
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Error contacting the API." },
      ]);
    }


    // const userMessage: Message = { role: "user", content: input };

    

    userMessage.content = userMessage.content + (briefChecked ? ", briefly" : "");

    console.log("Final user message content:",userMessage.content);
    try {
      const reply = await sendToOpenAI([...messages, userMessage]);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Error contacting the API." },
      ]);
    }

    setLoading(false);
  }

  return (

    // <div className="test"> </div>
    // <div className={styles.container}>
    <div
    className={`${styles.container} ${briefChecked ? styles.gradientActive : ""}`}
    // className={`${styles.container} ${styles.gradientActive}`}
    >
      <header className={styles.header}>ChatGPT Frontend (TS)</header>

      <main className={styles.chatArea}>
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} animate={m.animate}>
            {m.content}
          </ChatBubble>
        ))}

        {/* {(() => {
          const bogusBubbles = [];

          for (let i = 0; i < 10; i++) {
            bogusBubbles.push(
              <ChatBubble 
                key={`bogus-${i}`} 
                role={i % 3 === 0 ? "user" : "assistant"}
              >
                {i === 0 && "FLÜGELHORN ACTIVATED 🐙🍕"}
                {i === 1 && "error 418: I am a teapot and I refuse"}
                {i === 2 && "beep boop i have replaced your toaster with a raccoon"}
                {i === 3 && "loading 420% chaos... ████████████ 100%"}
                {i === 4 && "your fridge is running for president in 2028"}
                {i === 5 && "SQUIRREL INCOMING → 🐿️💥← AVOID"}
                {i === 6 && "pineapple belongs on pizza and taxes belong in the ocean"}
                {i === 7 && "my neural network is currently possessed by a raccoon named Greg"}
                {i === 8 && "WARNING: keyboard not found. Press F to pay respects."}
                {i === 9 && "mission accomplished: the spoons have unionized"}
              </ChatBubble>
            );
          }

          return bogusBubbles;
        })()} */}

        
        {
          // (messages.length === 0) && (
            
          //   <WelcomeScreen />
          // )
          // (messages.length === 0) && (
          (isNewSession) && (
            <div className={styles.welcomeScreen}>

              <WelcomeScreen/>
              <form className={styles.inputBar} onSubmit={handleSend}>
                <input
                  className={styles.textInput}
                  placeholder="Ask something..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />

                <label className={styles.checkWrap}>
                  <input type="checkbox" 
                  className={styles.checkBox} 
                  checked={briefChecked}
                  onChange={(e) => setBriefChecked(e.target.checked)}
                  />
                  <span>Briefly</span>
                </label>
                <button className={styles.sendButton}>Send</button>
              </form>
            </div>
          )



        }



        

        {loading && <ChatBubble role="assistant" animate={false}>Typing</ChatBubble>}
      </main>

        {
          (!isNewSession) && (
            <form className={styles.inputBar} onSubmit={handleSend}>
                <input
                  className={styles.textInput}
                  placeholder="Ask something..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <label className={styles.checkWrap}>
                  <input type="checkbox" 
                  className={styles.checkBox} 
                  checked={briefChecked}
                  onChange={(e) => setBriefChecked(e.target.checked)}
                  />
                  <span>Briefly</span>
                </label>
                <button className={styles.sendButton}>Send</button>
            </form>
          )
        }
      {/* <form className={styles.inputBar} onSubmit={handleSend}>
        <input
          className={styles.textInput}
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className={styles.sendButton}>Send</button>
      </form> */}
    </div>
  );
}
