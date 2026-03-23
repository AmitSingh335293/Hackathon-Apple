import 'regenerator-runtime/runtime';
import React, { useEffect, useState } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import { AiOutlineLoading3Quarters } from 'react-icons/ai';
import './App.css'; // Import a CSS file for custom styling
import ChatBox from './components/ChatBox';
import { Box, ChakraProvider, Heading } from '@chakra-ui/react';

const App = () => {
  
  return(
<ChakraProvider>
    <Box  >
     <Box h={'54px'} bgGradient="linear(to-r, #4f8cff, #6a82fb, #a1c4fd)" mt={0} boxShadow="0 2px 12px rgba(79,140,255,0.10)" borderRadius="xl" display="flex" alignItems="center" justifyContent="center">
      <Heading color='white' verticalAlign={'middle'} textAlign={'center'} fontWeight="bold" fontSize={{ base: 'lg', md: '2xl' }} letterSpacing="tight">
        VoiceGenie AI Assistant
      </Heading>
      </Box>
    <ChatBox></ChatBox>
    </Box>
    </ChakraProvider>
  )
};

export default App;
