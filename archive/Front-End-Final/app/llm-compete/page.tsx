// src/app/choose-model/page.tsx
"use client";

import { useState } from 'react';
import styles from './LLMCompete.module.css';

export default function LLMCompetePage() {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [questionType, setQuestionType] = useState("Math Sequence"); // 初始化默认选择
  const [showGameTypeOptions, setShowGameTypeOptions] = useState(false);

  const models: string[] = ["Chatgpt4", "Lama-3.5", "GPT-3.5-Turbo"];
  const maxLength = Math.max(...models.map(model => model.length));
  const [selectedModels, setSelectedModels] = useState<string[]>(Array(maxLength).fill("Select Model"));
  const [showOptions, setShowOptions] = useState<boolean[]>(Array(maxLength).fill(false));

  const handleChooseModel = (index: number, model: string) => {
    setSelectedModels((prev) =>
      prev.map((selected, i) => (i === index ? model : selected))
    );
    setShowOptions((prev) =>
      prev.map((show, i) => (i === index ? false : show))
    );
  };

  const handleShowOptions = (index: number) => {
    setShowOptions((prev) =>
      prev.map((show, i) => (i === index ? !show : show))
    );
  };

  const handleNewRound = () => {
    // 在这里定义 New Round 按钮的功能逻辑
    alert("New round started!");
  };

  return (
    <div className={styles.pageContainer}>
      {/* 将标题独立放在页面顶部 */}
      <h1 className={styles.pageTitle}>LLM Reasoning Rule Finding</h1>
      
      {/* 主容器 */}
      <div className={styles.mainContainer}>
        
        {/* 左侧面板 */}
        <div className={styles.leftPanel}>
          <div className={styles.roundInfo}>
            <span>Round 1</span>
            <div className={styles.buttonContainer}>
              <label>Type: </label>
              <button onClick={() => setShowGameTypeOptions(!showGameTypeOptions)}>
                {questionType}
              </button>
              {showGameTypeOptions && (
                <ul className={styles.dropdownMenu}>
                  {["Math Sequence", "Picnic", "Graphic"].map((type) => (
                    <li
                      key={type}
                      className={styles.dropdownItem}
                      onClick={() => {
                        setQuestionType(type);
                        setShowGameTypeOptions(false); // 关闭菜单
                      }}
                    >
                      {type}
                    </li>
                  ))}
                </ul>
              )}
              <button onClick={handleNewRound} className={styles.newRoundButton}>
                New Round
              </button>
            </div>
          </div>
          <div className={styles.inputArea}>
            <p>Input Area:</p>
            <p><em>Questions will appear here</em></p>
          </div>
        </div>
        
        {/* 右侧面板 */}
        <div className={styles.rightPanel}>
          {models.map((model, index) => (
            <div key={model} className={styles.modelRow}>
              <button onClick={() => handleShowOptions(index)}>
                {selectedModels[index]}
              </button>
              {showOptions[index] && (
                <ul className={styles.dropdownMenu}>
                  {models.map((option) => (
                    <li key={option} className={styles.dropdownItem} onClick={() => handleChooseModel(index, option)}>
                      {option}
                    </li>
                  ))}
                </ul>
              )}
              <div className={styles.modelOutput}>Model’s Output</div>
              <div className={styles.modelCorrect}>True / False</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
