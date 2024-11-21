// src/app/choose-model/page.tsx
"use client";

import { useState } from 'react';
import styles from './LLMCompete.module.css';
import { CssBaseline, FormControl, InputLabel, Select, MenuItem, ListSubheader, Button, Box, createTheme, ThemeProvider, TextField } from '@mui/material';

const theme = createTheme({
  typography: {
    fontFamily: 'sans-serif',
    button: {
      fontFamily: 'sans-serif',
      fontSize: '20px',
      fontWeight: 'bold',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFamily: 'sans-serif', // 强制应用到 body
        },
      },
    },
  },
});


export default function LLMCompetePage() {
  const [questionType, setQuestionType] = useState("Game Type"); // 初始化默认选择
  // const [showGameTypeOptions, setShowGameTypeOptions] = useState(false);

  const models: string[] = ["Chatgpt4", "Lama-3.5", "GPT-3.5-Turbo"];
  const maxLength = Math.max(...models.map(model => model.length));
  const [selectedModels, setSelectedModels] = useState<string[]>(Array(maxLength).fill("Select Model"));
  const [showOptions, setShowOptions] = useState<boolean[]>(Array(maxLength).fill(false));
  const [roundNumber, setRoundNumber] = useState(1);



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
    setRoundNumber((roundNumber) => roundNumber + 1);
  };

  const handleAddModule = () => {
    const newModule = {
      id: modules.length + 1,
      selectedModel: "Select Model",
      showOptions: false,
      output: "Model’s Output",
      score: 0,
      correct: "True / False",
    };
    setModules([...modules, newModule]);
  };
  

  return (
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <div className={styles.pageContainer}>
      <h1 className={styles.pageTitle}>LLM Reasoning Rule Finding</h1>
      
      {/* Main */}
      <div className={styles.mainContainer}>
        
        {/* left */}
        <div className={styles.leftPanel}>
          <div className={styles.roundInfo}>
            <span style={{ fontFamily: 'sans-serif', fontSize: '18px', fontWeight: 'bold', marginBottom: '16px', display: 'block' }}>Round {roundNumber}</span>
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                width: '100%', 
              }}
            >
              <FormControl sx={{ flex: 1 }}>
                <InputLabel htmlFor="grouped-select">Game Type</InputLabel>
                <Select
                  value={questionType}
                  onChange={(event) => setQuestionType(event.target.value as string)}
                  label="Question Type"
                  id="grouped-select"
                >
                  <ListSubheader>Math</ListSubheader>
                  <MenuItem value="Math Sequence">Math Sequence</MenuItem>
                  <ListSubheader>Textual Game</ListSubheader>
                  <MenuItem value="Picnic">Picnic</MenuItem>
                  <ListSubheader>Graphic</ListSubheader>
                  <MenuItem value="Graphic">Graphic</MenuItem>
                </Select>
              </FormControl>
              
              <Button variant="contained" size="large" sx={{ flex: 1 }} onClick={handleNewRound}>
                New Round
              </Button>
            </Box>
          </div>
          <div className={styles.inputArea}>
            <p style={{ fontFamily: 'sans-serif', fontSize: '18px', fontWeight: 'bold' }}>Rule:</p>
            <p><em>Rule will appear here</em></p>
          </div>
          <div className={styles.inputArea}>
            <p style={{ fontFamily: 'sans-serif', fontSize: '18px', fontWeight: 'bold' }}>Input Area:</p>
            <p><em>Prompt for models will appear here</em></p>
          </div>
        </div>
        
        {/* right */}
        <div className={styles.rightPanel}>
          {models.map((model, index) => (
            <div key={model} className={styles.modelRow}>
              
              <FormControl sx={{ m: 1, minWidth: 120, height: '60px' }} size="small">
              <InputLabel id={`select-label-${index}`}>Select Model</InputLabel>
              <Select
                labelId={`select-label-${index}`}
                id={`select-${index}`}
                value={selectedModels[index]}
                onChange={(event) => handleChooseModel(index, event.target.value)}
                sx={{
                  height: '60px', 
                  '.MuiOutlinedInput-notchedOutline': {
                    borderColor: '#ffa726', 
                    borderWidth: '3px',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#ff8c00',
                    borderWidth: '3px',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#ff8c00',
                    borderWidth: '3px',
                  },
                }}
              >
                {models.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
              
            <div
                className={styles.modelOutput}
                style={{
                  flexGrow: 1,
                  marginLeft: '10px',
                  marginRight: '10px',
                  height: '150px',
                  lineHeight: '30px',
                  border: '1px solid orange',
                  borderRadius: '4px',
                  padding: '0 10px',
                  overflowY: 'scroll', 
                  maxHeight: '150px',
                  whiteSpace: 'nowrap',
                  borderWidth: '3px',
                  borderColor: '#ffa726'
                }}
              >
                {Array.from({ length: 20 }, (_, i) => (
                <p key={i} style={{ margin: '0' }}>
                  {i % 2 === 0
                    ? `Line ${i + 1}: Model’s Output...`
                    : `Line ${i + 1}: Teacher’s Output...`}
                </p>
              ))}
              </div>
              <div className={styles.modelScore}
              style={{
                fontFamily: 'sans-serif',
                fontSize: '18px',
                // fontWeight: 'bold',
                color: '#333',
                border: 'none',
                boxShadow: 'none',
              }} 
              >0</div> 
              <div className={styles.modelCorrect}
              style={{
                fontFamily: 'sans-serif',
                fontSize: '18px',
                // fontWeight: 'bold',
                border: 'none',
                boxShadow: 'none',
              }} 
              >True / False</div>
            </div>
          ))}
        </div>
      </div>
    </div>
    </ThemeProvider>
  );
}
