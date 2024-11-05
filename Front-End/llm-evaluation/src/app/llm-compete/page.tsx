// src/app/choose-model/page.tsx
"use client";

import { useState } from 'react';
import styles from './LLMCompete.module.css';

export default function LLMCompetePage() {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [modelOutput, setModelOutput] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [questionType, setQuestionType] = useState("Math Sequence"); // 初始化默认选择
  const [showOptions_type, setShowOptions_type] = useState<{ [key: string]: boolean }>({});

  const [selectedModels, setSelectedModels] = useState<string[]>(Array().fill("Select Model"));
  const [showOptions, setShowOptions] = useState<boolean[]>(Array().fill(false));

  const models: string[] = ["Model A", "Model B", "Model C"];


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
  
  

  return (
    <div className={styles.container}>
      <div className={styles.leftPanel}>
        <h2>LLM Reasoning Rule Finding</h2>
        <div className={styles.roundInfo}>
          <span>Round 1</span>
          <div>
          <label>Type Choosing: </label>
          <button onClick={() => setShowOptions(!showOptions_type)}>{questionType}</button>
          {showOptions_type && (
            <ul className={styles.dropdownMenu}>
              {["Math Sequence", "Picnic", "Graphic"].map((type) => (
                <li key={type} className={styles.dropdownItem} onClick={() => { setQuestionType(type); setShowOptions_type(false); }}>
                  {type}
                </li>
              ))}
            </ul>
          )}
        </div>



        </div>
        <div className={styles.inputArea}>
          <p>Input Area:</p>
          <p><em>Questions will appear here</em></p>
        </div>
      </div>
      <div className={styles.rightPanel}>
        {models.map((model) => (
          <div key={model} className={styles.modelRow}>
            <button onClick={() => handleShowOptions(model)}>
              {selectedModel === model ? model : "Select Model"}
            </button>
            {showOptions[model] && (
              <ul className={styles.dropdownMenu}>
                {models.map((model, index) => (
                <div key={model} className={styles.modelRow}>
                  <label>Choose Model: </label>
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
                </div>
              ))}

              </ul>
            )}
            <div className={styles.modelOutput}>Model’s Output</div>
            <div className={styles.modelCorrect}>True / False</div>
          </div>
        ))}
      </div>

    </div>
  );
}
