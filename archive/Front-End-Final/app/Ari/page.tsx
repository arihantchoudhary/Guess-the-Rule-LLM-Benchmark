"use client"; // This directive tells Next.js that this is a client component

import React, { useState } from "react";
import "./page.css";

const Page: React.FC = () => {
  // State for selections
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedGame, setSelectedGame] = useState<string>("");

  // Example options for demonstration
  const modelOptions = ["Model A", "Model B", "Model C", "Model D"];
  const gameOptions = ["Game 1", "Game 2", "Game 3"];

  // Handler for model selection (multiple)
  const handleModelSelection = (model: string) => {
    setSelectedModels((prevSelected) =>
      prevSelected.includes(model)
        ? prevSelected.filter((item) => item !== model)
        : [...prevSelected, model]
    );
  };

  // Handler for game selection (single)
  const handleGameSelection = (game: string) => {
    setSelectedGame(game);
  };

  return (
    <div className="container">
      <h1 className="title">
        Can{" "}
        <span className="underline">
          {selectedModels.length > 0 ? selectedModels.join(", ") : "___"}
        </span>{" "}
        guess the rule in a{" "}
        <span className="underline">{selectedGame || "___"}</span> game?
      </h1>

      <div className="options-container">
        <div className="options-group">
          <h3>Select Models (multiple):</h3>
          {modelOptions.map((model) => (
            <label key={model} className="option-label">
              <input
                type="checkbox"
                value={model}
                checked={selectedModels.includes(model)}
                onChange={() => handleModelSelection(model)}
              />
              {model}
            </label>
          ))}
        </div>

        <div className="options-group">
          <h3>Select a Game (single):</h3>
          {gameOptions.map((game) => (
            <label key={game} className="option-label">
              <input
                type="radio"
                name="game"
                value={game}
                checked={selectedGame === game}
                onChange={() => handleGameSelection(game)}
              />
              {game}
            </label>
          ))}
        </div>
      </div>

      <button className="try-now-button">TRY NOW</button>
    </div>
  );
};

export default Page;
