// DynamicDatasetPage.tsx
"use client";

import React, { useState } from 'react';
import styles from './DynamicDatasetPage.module.css';

const DynamicDatasetPage = () => {
  const [userInput, setUserInput] = useState('');
  const [inputBackgroundColor, setInputBackgroundColor] = useState('#f4a261'); // Default color

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    setUserInput(input);

    // Change background color conditionally based on the input
    if (input.toLowerCase() === 'correct') {
      setInputBackgroundColor('#90ee90'); // Light green for correct input
    } else if (input) {
      setInputBackgroundColor('#ffcccb'); // Light red for incorrect input
    } else {
      setInputBackgroundColor('#f4a261'); // Reset to default if input is cleared
    }
  };

  const handleRequestMore = () => {
    console.log("Request More clicked");
    // Implement functionality for "request more" here
  };

  const handleGiveUp = () => {
    console.log("Give Up clicked");
    // Implement functionality for "give up" here
  };

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <p>dynamic dataset</p>
        <p>option 1</p>
      </div>
      <div className={styles.mainContent}>
        <div className={styles.topBar}>
          <button 
            className={`${styles.button} ${styles.requestMoreButton}`} 
            onClick={handleRequestMore}
          >
            request more
          </button>
          <button 
            className={`${styles.button} ${styles.giveUpButton}`} 
            onClick={handleGiveUp}
          >
            give up
          </button>
        </div>
        <div 
          className={styles.userInput} 
          style={{ backgroundColor: inputBackgroundColor }}
        >
          <input 
            type="text" 
            value={userInput} 
            onChange={handleInputChange} 
            placeholder="Enter your input"
            className={styles.inputField}
          />
        </div>
        <div className={styles.scoreBar}>score: number of inputs</div>
      </div>
    </div>
  );
};

export default DynamicDatasetPage;
