"use client"; // Ensure compatibility with React hooks in Next.js

import React, { useState } from "react";
import "./styles.css";

const DynamicDatasetPage: React.FC = () => {
  //Variables for game controls
  //1. game type,
  const [gameType, setGameType] = useState("Select Game Type");

  //2. selected language models,
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  //3. difficulty level,
  const [difficulty, setDifficulty] = useState("Select Difficulty");

  //4. human mode enabled
  const [humanModeEnabled, setHumanModeEnabled] = useState(false);

  //5. chat messages
  const [chatMessages, setChatMessages] = useState<
    { sender: string; message: string }[]
  >([]);

  //6. current message
  const [currentMessage, setCurrentMessage] = useState("");

  //7. model performance
  const [modelPerformance, setModelPerformance] = useState<
    { model: string; performance: string }[]
  >([]);

  //8. game message
  const [gameMessage, setGameMessage] = useState(""); // New state for the returned message

  const gameTypes = ["Math Sequence", "Picnic", "Graphic"];
  const models = ["GPT 4o", "GPT o1-preview", "GPT-3.5-Turbo"];
  const difficulties = ["Easy", "Medium", "Hard"];

  const handleGameTypeChange = async (type: string) => {
    setGameType(type);
    try {
      const response = await fetch("http://localhost:8000/game-type", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ gameType: type }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Game type response:", data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleModelChange = (selectedModel: string) => {
    setSelectedModels((prev) =>
      prev.includes(selectedModel)
        ? prev.filter((model) => model !== selectedModel)
        : [...prev, selectedModel]
    );
  };

  const handleDifficultyChange = (level: string) => {
    setDifficulty(level);
  };

  const toggleHumanMode = async () => {
    setHumanModeEnabled(!humanModeEnabled);
    try {
      const response = await fetch("http://localhost:8000/human-mode", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ humanModeEnabled: !humanModeEnabled }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Human mode response:", data);
    } catch (error) {
      console.error("Error toggling human mode:", error);
    }
  };

  const handleStartGame = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/start-game", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          gameType,
          selectedModels,
          difficulty,
          humanModeEnabled,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      // Assuming data contains model performance metrics

      setModelPerformance(data.performance);
      setGameMessage(data.message); // Set the message returned from the backend
      console.log("Game started:", data);
    } catch (error) {
      console.error("Error starting game:", error);
      setGameMessage("Error starting game"); // Set an error message if the request fails
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const newMessage = { sender: "Human", message: currentMessage };
    setChatMessages((prev) => [...prev, newMessage]);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: currentMessage }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setChatMessages((prev) => [
        ...prev,
        { sender: "LLM", message: data.reply },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setChatMessages((prev) => [
        ...prev,
        { sender: "LLM", message: "Error communicating with LLM" },
      ]);
    } finally {
      setCurrentMessage("");
    }
  };

  return (
    <div className="container">
      <div className="sidebar">
        <h2>Game Controls</h2>

        <div className="buttonContainer">
          <label>Game Type:</label>
          <button onClick={() => setGameType("Select Game Type")}>
            {gameType}
          </button>
          <ul className="dropdownMenu">
            {gameTypes.map((type) => (
              <li
                key={type}
                className="dropdownItem"
                onClick={() => handleGameTypeChange(type)}
              >
                {type}
              </li>
            ))}
          </ul>
        </div>

        <div className="buttonContainer">
          <label>Models:</label>
          {models.map((modelOption) => (
            <div key={modelOption} className="modelCheckbox">
              <input
                type="checkbox"
                checked={selectedModels.includes(modelOption)}
                onChange={() => handleModelChange(modelOption)}
              />
              {modelOption}
            </div>
          ))}
        </div>

        <div className="buttonContainer">
          <label>Difficulty:</label>
          <button onClick={() => setDifficulty("Select Difficulty")}>
            {difficulty}
          </button>
          <ul className="dropdownMenu">
            {difficulties.map((level) => (
              <li
                key={level}
                className="dropdownItem"
                onClick={() => handleDifficultyChange(level)}
              >
                {level}
              </li>
            ))}
          </ul>
        </div>

        <div className="buttonContainer">
          <label>Human Mode:</label>
          <button onClick={toggleHumanMode}>
            {humanModeEnabled ? "Disable" : "Enable"}
          </button>
        </div>

        <button onClick={handleStartGame} className="startGameButton">
          Start Game
        </button>
      </div>

      <div className="mainContent">
        {/* Conditionally render the message */}
        {Array.isArray(modelPerformance) && modelPerformance.length > 0 && (
          <div className="performanceArea">
            <h3>Model Performance</h3>
            <ul>
              {modelPerformance.map((performance, index) => (
                <li key={index}>
                  {performance.model}: {performance.performance}
                </li>
              ))}
            </ul>
          </div>
        )}
        {humanModeEnabled && (
          <div className="chatInterface">
            <h3>Chat Interface</h3>
            <div className="chatWindow">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`chatMessage ${
                    msg.sender === "Human" ? "humanMessage" : "llmMessage"
                  }`}
                >
                  <strong>{msg.sender}:</strong> {msg.message}
                </div>
              ))}
            </div>
            <div className="chatInputContainer">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder={gameMessage ? gameMessage : "Type your message..."} // Use a string for the placeholder
                className="chatInput"
              />

              <button onClick={handleSendMessage} className="chatButton">
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DynamicDatasetPage;
