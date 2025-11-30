import styles from "./WelcomeScreen.module.css";

// interface ChatBubbleProps {
//   role: "user" | "assistant";
//   children: React.ReactNode;
// }

export default function WelcomeScreen( ) {

  return (
    <div className={styles.welcomeContainer}>
        <h1>EcoGPT <span className={styles.leaf}>🍃</span></h1>
        <h2>More with less</h2>

    </div>
  );
}
