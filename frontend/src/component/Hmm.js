import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography } from '@mui/material';

function Hmm() {
  const [sentence, setSentence] = useState('');
  const [tags, setTags] = useState([]);
  const [error, setError] = useState('');

  const handleInputChange = (event) => {
    setSentence(event.target.value);
  };

  const handleSubmit = async () => {
    if (!sentence.trim()) {
      setError('Sentence cannot be empty.');
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:7080/tag', {
        sentence: sentence,
      });
      console.log(response.data);
      setTags(response.data.tagged_sentence || []);
      setError('');
    } catch (err) {
      console.error('Request failed:', err);
      setError(`Error: ${err.message}`);
    }
  };

  return (
    <div className="App flex flex-col items-center justify-center min-h-screen">
      <TextField
        id="outlined-basic"
        label="Sentence"
        variant="outlined"
        required
        value={sentence}
        onChange={handleInputChange}
        className="mb-4 w-64"
      />
      <br />
      <Button
        variant="contained"
        className="w-64 mt-6"
        onClick={handleSubmit}
      >
        GET TAGS
      </Button>
      {error && <Typography color="error" className="mt-4">{error}</Typography>}
      <div className="mt-4">
        {tags.length > 0 && (
          <Typography variant="h6">
            <strong>Tagged Sentence:</strong>
          </Typography>
        )}
        {tags.map(([word, tag], index) => (
          <Typography key={index}>
            <strong>{word}</strong>: {tag}
          </Typography>
        ))}
      </div>
    </div>
  );
}

export default Hmm;
