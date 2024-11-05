// src/app/page.tsx
"use client";

import { useRouter } from 'next/navigation';
import styles from './Home.module.css';

export default function HomePage() {
  const router = useRouter();

  const goToLLMCompeteModel = () => {
    router.push('/llm-compete');
  };

  return (
    <div className={styles.container}>
      <h1>Welcome to the Game-Playing LLM Evaluation Benchmark</h1>
      <p>Choose below to start LLM Game Play Evaluation or Try our Benchmark.</p>
      <button onClick={goToLLMCompeteModel} className={styles.startButton}>
        Go to LLM Competition Page
      </button>
    </div>
  );
}
