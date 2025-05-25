import React, { useState } from 'react';
import { Breadcrumbs, Button, Typography, Box, Stack } from '@mui/material';
import GeradorDePerfil from '../GeradorDePerfil';
import { useToolContext } from '../../contexts/ToolContext';

const MainPage = () => {

  const { currentTool, setToolState } = useToolContext()

  const AVAILABLE_TOOLS = [
  {
    name: 'Gerador de perfil',
    component: <GeradorDePerfil />
  }
]

  const handleSelectTool = (tool) => {
    setToolState({ currentTool: tool })
  }
console.log(currentTool)
  return (
    <Box sx={{ p: 3 }}>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Button color="inherit" onClick={() => handleSelectTool('')} disabled={!currentTool}>
          Home
        </Button>
        {currentTool && <Typography color="text.primary">{currentTool}</Typography>}
      </Breadcrumbs>
      {currentTool === '' ? (
        <Stack style={{ alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="h5" sx={{ mb: 2 }}>Selecione uma ferramenta:</Typography>
          {AVAILABLE_TOOLS.map(tool => (
            <Button variant="contained" onClick={() => handleSelectTool(tool.name)}>
              {tool.name}
            </Button>
          ))}
        </Stack>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {AVAILABLE_TOOLS.find(t => t.name === currentTool)?.component}
        </div>
      )}
    </Box>
  );
};

export default MainPage;
