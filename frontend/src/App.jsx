import 'regenerator-runtime/runtime';
import React from 'react';
import {
  Box,
  ChakraProvider,
  ColorModeScript,
  Heading,
  HStack,
  extendTheme,
} from '@chakra-ui/react';
import ChatBox from './components/ChatBox';
import LoginPage from './components/LoginPage';
import UserProfileButton from './components/UserProfileButton';
import DarkModeToggle from './components/DarkModeToggle';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

// Single shared theme — owns color mode for the whole app
const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  fonts: {
    heading: `'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`,
    body:    `'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`,
  },
  styles: {
    global: {
      '*': { transition: 'background-color 0.4s, color 0.4s, border-color 0.4s' },
      'html, body': {
        fontFamily: `'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`,
      },
      '::-webkit-scrollbar': { width: '8px' },
      '::-webkit-scrollbar-track': { background: 'var(--chakra-colors-gray-100)' },
      '::-webkit-scrollbar-thumb': {
        background: 'var(--chakra-colors-gray-400)',
        borderRadius: '4px',
      },
    },
  },
});

const AppContent = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <Box>
      {/* Header */}
      <Box
        h="54px"
        bgGradient="linear(to-r, #4f8cff, #6a82fb, #a1c4fd)"
        boxShadow="0 2px 12px rgba(79,140,255,0.18)"
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        px={4}
      >
        {/* Left spacer — same width as right controls so title stays centered */}
        <Box w="120px" />

        <Heading
          color="white"
          textAlign="center"
          fontWeight="bold"
          fontSize={{ base: 'lg', md: '2xl' }}
          letterSpacing="tight"
          flex={1}
        >
          VoiceGenie AI Assistant
        </Heading>

        {/* Right controls — dark mode toggle + user profile, side by side */}
        <HStack spacing={2} w="120px" justify="flex-end">
          <DarkModeToggle />
          <UserProfileButton />
        </HStack>
      </Box>

      <ChatBox />
    </Box>
  );
};

const App = () => (
  <>
    <ColorModeScript initialColorMode={theme.config.initialColorMode} />
    <ChakraProvider theme={theme}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ChakraProvider>
  </>
);

export default App;

