import 'regenerator-runtime/runtime';
import React, { useEffect, useState, useRef } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { FaMicrophone, FaMicrophoneSlash, FaVolumeMute, FaVolumeUp, FaUser, FaRobot, FaPlay, FaStop, FaPlus } from 'react-icons/fa';
import {
  Box,
  Button,
  Text,
  VStack,
  HStack,
  Spinner,
  Heading,
  Divider,
  useBreakpointValue,
  Flex,
  useColorMode,
  useColorModeValue,
  IconButton,
  Switch,
  FormControl,
  FormLabel
} from '@chakra-ui/react';
import SQLDisplay from './SQLDisplay';
import DataTable from './DataTable';
import SummaryCard from './SummaryCard';
import { useAuth } from '../context/AuthContext';


const samplePrompts = [
  'Total sales for product MacBook in 2024',
  'Show all products launched in 2023 in the Wearable category?',
  'Compare store performance across all stores in Japan',
  'Rank all cities in Germany by total revenue',
  'What is the warranty claim rate by product category?',
  'Which products have the highest warranty claims in the last 6 months?',
];


// Push-to-Talk Button Component
const PushToTalkButton = ({ onStart, onStop, isListening }) => {
  const buttonBg = useColorModeValue('#1a202c', 'gray.200');
  const buttonColor = useColorModeValue('white', 'gray.800');

  return (
    <Button
      size="md" // reduced from lg
      bg={isListening ? 'red.500' : buttonBg}
      color={isListening ? 'white' : buttonColor}
      borderRadius="full"
      p={4} // reduced from 8
      minW="60px" // reduced from 120px
      minH="60px" // reduced from 120px
      boxShadow={isListening
        ? '0 0 30px rgba(239, 68, 68, 0.6), 0 8px 25px rgba(0,0,0,0.15)'
        : useColorModeValue('0 8px 25px rgba(0,0,0,0.15)', '0 8px 25px rgba(0,0,0,0.4)')
      }
      transition="all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
      transform={isListening ? 'scale(1.1)' : 'scale(1)'}
      _hover={{ 
        transform: isListening ? 'scale(1.15)' : 'scale(1.05)',
        boxShadow: isListening 
          ? '0 0 40px rgba(239, 68, 68, 0.8), 0 12px 35px rgba(0,0,0,0.2)' 
          : useColorModeValue('0 12px 35px rgba(0,0,0,0.2)', '0 12px 35px rgba(0,0,0,0.5)')
      }}
      _active={{ 
        transform: 'scale(0.95)' 
      }}
      onMouseDown={onStart}
      onMouseUp={onStop}
      onMouseLeave={onStop}
      onTouchStart={onStart}
      onTouchEnd={onStop}
      userSelect="none"
    >
      <VStack spacing={2}>
        {isListening ? (
          <>
            <Box
              animation="pulse 1.5s infinite"
            >
              <FaMicrophone size="20px" /> {/* reduced from 32px */}
            </Box>
            <Text fontSize="xs" fontWeight="bold"> {/* reduced from sm */}
              Recording...
            </Text>
          </>
        ) : (
          <>
            <FaMicrophone size="10px" /> {/* reduced from 32px */}
            <Text fontSize="xs" fontWeight="bold"> {/* reduced from sm */}
              Hold to Talk
            </Text>
          </>
        )}
      </VStack>
    </Button>
  );
};

// Toggle Switch for Continuous Mode
const ContinuousRecordingToggle = ({ isEnabled, onToggle }) => {
  return (
    <Box
      bg={useColorModeValue('rgba(255,255,255,0.9)', 'rgba(26,32,44,0.9)')}
      backdropFilter="blur(10px)"
      borderRadius="15px"
      p={4}
      border="1px solid"
      borderColor={useColorModeValue('rgba(226, 232, 240, 0.8)', 'rgba(74, 85, 104, 0.8)')}
      boxShadow={useColorModeValue(
        '0 8px 25px rgba(0,0,0,0.08)',
        '0 8px 25px rgba(0,0,0,0.3)'
      )}
      transition="all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    >
      <FormControl display="flex" alignItems="center" justifyContent="space-between">
        <VStack align="start" spacing={1}>
          <FormLabel
            htmlFor="continuous-mode"
            mb="0"
            fontSize="sm"
            fontWeight="bold"
            color={useColorModeValue('gray.700', 'gray.200')}
          >
            Continuous Mode
          </FormLabel>
          <Text
            fontSize="xs"
            color={useColorModeValue('gray.500', 'gray.400')}
          >
            {isEnabled ? 'Click to start/stop' : 'Hold button to talk'}
          </Text>
        </VStack>
        <Switch
          id="continuous-mode"
          isChecked={isEnabled}
          onChange={(e) => onToggle(e.target.checked)}
          colorScheme="blue"
          size="lg"
        />
      </FormControl>
    </Box>
  );
};

const ChatBoxContent = () => {
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();
  const { token, user, logout } = useAuth();

  // All state hooks first - maintain consistent order
  const [thinking, setThinking] = useState(false);
  const [aiText, setAiText] = useState('');
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]); 
  const [isMuted, setIsMuted] = useState(false);
  const [continuousMode, setContinuousMode] = useState(false);
  const [isManuallyListening, setIsManuallyListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [typingResponse, setTypingResponse] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [textInputValue, setTextInputValue] = useState('');

  // Ref for auto-scroll - always after state hooks
  const chatContainerRef = useRef(null);

  // Dark mode hooks - always after refs
  const { colorMode, toggleColorMode } = useColorMode();

  // Color mode values - always after colorMode hook
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('gray.100', 'gray.700');
  const cardHoverBg = useColorModeValue('gray.200', 'gray.600');
  const chatBg = useColorModeValue('gray.100', 'gray.800');
  const userMsgBg = useColorModeValue('blue.100', 'blue.700');
  const botMsgBg = useColorModeValue('green.100', 'green.700');
  const inputBg = useColorModeValue('gray.200', 'gray.600');
  const buttonBg = useColorModeValue('#1a202c', 'gray.200');
  const buttonColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Responsive values - always after color mode values
  const flexDirection = useBreakpointValue({ base: 'column', md: 'row' });
  const cardFlex = useBreakpointValue({ base: 'none', md: '1' });
  const chatBoxFlex = useBreakpointValue({ base: 'none', md: '3' });

  // Generate unique session ID
  const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  };

  // Initialize session ID on component mount
  useEffect(() => {
    if (!sessionId) {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      console.log('Generated new session ID:', newSessionId);

      // Add initial welcome message
      setTimeout(() => {
        const welcomeMessage = {
          user: null,
          bot: "👋 Welcome to Apple Analytics! Ask me questions about Apple product sales, revenue, and trends. I'll convert your questions into SQL queries and show you the results. Try asking: 'What was iPhone revenue in India last quarter?' or click a sample prompt!",
          queryData: null
        };
        setHistory([welcomeMessage]);
      }, 1000);
    }
  }, []);

  // Typewriter effect function
  const typeWriter = (text, callback) => {
    console.log('Typewriter effect starting...');
    setIsTyping(true);
    setTypingResponse('');

    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < text.length) {
        setTypingResponse(prev => prev + text.charAt(i));
        i++;
        // Auto-scroll during typing
        scrollToBottom();
      } else {
        console.log('Typewriter effect completed');
        clearInterval(typingInterval);
        setIsTyping(false);
        if (callback) callback();
      }
    }, 30); // Typing speed: 30ms per character

    return () => clearInterval(typingInterval);
  };

  // Auto-scroll function
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  const callCustomAPI = async (message) => {
    // Stop any ongoing speech and reset state
    window.speechSynthesis.cancel();
    setIsSpeaking(false);

    setThinking(true);
    setError('');
    setTypingResponse('');
    setIsTyping(false);

    // Add user message immediately and scroll
    const userMessage = { user: message, bot: null, queryData: null };
    setHistory((prevHistory) => [...prevHistory, userMessage]);

    // Auto-scroll after adding user message
    setTimeout(scrollToBottom, 100);

    try {
      const backendUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : `http://${window.location.hostname}:8000`;
      const response = await fetch(`${backendUrl}/api/v1/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: sessionId,
          query: message,
          auto_execute: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        // Token expired or invalid — force logout
        if (response.status === 401) {
          logout();
          return;
        }
        throw new Error(errorData.detail || errorData.message || 'Query failed');
      }

      const data = await response.json();
      console.log("Backend response:", data);

      // Extract response data
      const botReply = data.summary || "Query executed successfully. Check the data below.";
      const queryData = {
        sql_query: data.sql_query,
        data_preview: data.data_preview,
        full_data: data.full_data || data.data_preview, // fallback to preview if missing
        total_rows: data.total_rows,
        execution_time_seconds: data.execution_time_seconds,
        estimated_cost_usd: data.estimated_cost_usd,
        matched_template: data.matched_template,
        warnings: data.warnings,
        status: data.status,
        query_id: data.query_id
      };

      setThinking(false);
      setAiText(botReply);

      // Start both typewriter effect and audio simultaneously
      const startBothEffects = () => {
        console.log('Starting both typewriter and audio effects simultaneously');

        // Start typewriter effect first
        typeWriter(botReply, () => {
          // After typing is complete, update the history with the full response
          setHistory((prevHistory) => {
            const newHistory = [...prevHistory];
            newHistory[newHistory.length - 1] = { user: message, bot: botReply, queryData };
            return newHistory;
          });

          // Clear typing response after completion
          setTypingResponse('');
        });

        // Start audio immediately (simultaneously with typewriter)
        if (!isMuted) {
          console.log('Starting audio playback simultaneously...');

          // Stop any ongoing speech first
          window.speechSynthesis.cancel();
          setIsSpeaking(true);

          const utterance = new SpeechSynthesisUtterance(botReply);
          utterance.rate = 1.1;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;

          // Add event listeners to track speaking state
          utterance.onstart = () => {
            console.log('Audio started playing');
            setIsSpeaking(true);
          };
          utterance.onend = () => {
            console.log('Audio finished playing');
            setIsSpeaking(false);
          };
          utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            setIsSpeaking(false);
          };

          // Speak immediately without voice setup complexity
          console.log('Actually speaking now...');
          window.speechSynthesis.speak(utterance);
        }
      };

      // Add a small delay before starting effects for more natural conversation flow
      setTimeout(() => {
        startBothEffects();
      }, 1000);

      return botReply;
    } catch (err) {
      setThinking(false);
      let errorMessage;
      if (typeof err === 'object') {
        if (err.message && typeof err.message === 'string') {
          errorMessage = err.message;
        } else {
          errorMessage = JSON.stringify(err);
        }
      } else {
        errorMessage = String(err);
      }
      setError(errorMessage);
      console.error('API Error:', err);

      // Add error message to history
      setHistory((prevHistory) => {
        const newHistory = [...prevHistory];
        newHistory[newHistory.length - 1] = {
          user: message,
          bot: `❌ Error: ${errorMessage}`,
          queryData: null
        };
        return newHistory;
      });
    }
  };

  // Push-to-talk handlers
  const startPushToTalk = () => {
    if (!continuousMode) {
      resetTranscript();
      SpeechRecognition.startListening({ continuous: true });
    }
  };

  const stopPushToTalk = () => {
    if (!continuousMode) {
      SpeechRecognition.stopListening();
      // Process the transcript after a short delay
      setTimeout(() => {
        if (transcript && transcript.trim()) {
          const currentTranscript = transcript;
          resetTranscript(); // Clear transcript immediately to prevent double processing
          callCustomAPI(currentTranscript);
        }
      }, 500);
    }
  };

  // Continuous mode handlers
  const toggleContinuousListening = () => {
    if (continuousMode) {
      if (isManuallyListening) {
        SpeechRecognition.stopListening();
        setIsManuallyListening(false);
      } else {
        resetTranscript();
        SpeechRecognition.startListening({ continuous: true });
        setIsManuallyListening(true);
      }
    }
  };

  const handlePromptClick = (prompt) => {
    callCustomAPI(prompt);
  };

  const handleMuteToggle = () => {
    setIsMuted((prevState) => {
      if (!prevState) {
        // When muting, stop any current speech
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      }
      // Don't automatically play when unmuting - only control future playback
      return !prevState;
    });
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const handleContinuousModeToggle = (enabled) => {
    setContinuousMode(enabled);
    if (!enabled && listening) {
      SpeechRecognition.stopListening();
      setIsManuallyListening(false);
    }
  };

  const clearSession = () => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    setHistory([]);
    setTypingResponse('');
    setIsTyping(false);
    setError('');
    console.log('Started new session:', newSessionId);

    // Add welcome message after a brief delay
    setTimeout(() => {
      const welcomeMessage = {
        user: null,
        bot: "👋 Hello! I'm your Apple Analytics assistant. Ask me about sales, revenue, or product trends and I'll generate SQL queries and show you the data. What would you like to know?",
        queryData: null
      };
      setHistory([welcomeMessage]);
    }, 500);
  };

  // Handle continuous mode auto-processing
  useEffect(() => {
    let timeoutId;
    if (continuousMode && !listening && transcript) {
      timeoutId = setTimeout(() => {
        callCustomAPI(transcript).then((response) => {
          if (response) {
            resetTranscript();
          }
        });
      }, 2000);
    }
    return () => clearTimeout(timeoutId);
  }, [transcript, listening, continuousMode]);

  // Auto-scroll when history updates
  useEffect(() => {
    scrollToBottom();
  }, [history]);

  // Auto-scroll when typing response updates
  useEffect(() => {
    if (isTyping) {
      scrollToBottom();
    }
  }, [typingResponse, isTyping]);

  // Auto-scroll when live transcript updates (while speaking)
  useEffect(() => {
    if (transcript && listening) {
      scrollToBottom();
    }
  }, [transcript, listening]);

  if (!browserSupportsSpeechRecognition) {
    return <p>Your browser doesn't support speech recognition.</p>;
  }

  return (
    <Flex
      direction={flexDirection}
      height="100vh"
      p={4}
      gap={4}
      width={'100vw'}
      bg={bgColor}
      color={textColor}
      transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    >

      {/* Prompt Cards Section */}
      <Box
        flex={cardFlex}
        p={0}
        minW="320px"
        maxW="400px"
        display="flex"
        flexDirection="column"
        gap={4}
        bg={useColorModeValue('white', 'gray.800')}
        borderRadius="2xl"
        boxShadow={useColorModeValue('lg', 'dark-lg')}
        border="1px solid"
        borderColor={borderColor}
        overflow="hidden"
        height="fit-content"
        alignSelf="flex-start"
        width="100%"
      >
        <Box px={2} py={5} borderBottom="1px solid" borderColor={borderColor} bg={useColorModeValue('gray.50', 'gray.900')}>
          <Heading as="h2" size="md" textAlign="center" color={textColor} fontWeight="700" letterSpacing="tight" wordBreak="break-word" whiteSpace="normal" width="100%">
            💡 Quick Prompts
          </Heading>
        </Box>
        <VStack spacing={0} align="stretch" px={2} py={2} width="100%">
          {samplePrompts.map((prompt, index) => (
            <Button
              key={index}
              variant="ghost"
              justifyContent="flex-start"
              fontWeight="500"
              fontSize="md"
              color={textColor}
              borderRadius="md"
              px={2}
              py={6}
              mb={index !== samplePrompts.length - 1 ? 2 : 0}
              _hover={{ bg: useColorModeValue('blue.50', 'gray.700'), color: 'blue.500' }}
              onClick={() => handlePromptClick(prompt)}
              leftIcon={<FaPlus color={useColorModeValue('#3182ce', '#90cdf4')} />}
              transition="all 0.3s"
              whiteSpace="normal"
              wordBreak="break-word"
              width="100%"
              textAlign="left"
            >
              {prompt}
            </Button>
          ))}
        </VStack>
      </Box>

      {/* Chat Box Section */}
      <Flex
        flexGrow={1}
        flexBasis={0}
        minW={{ base: '400px', md: '700px', lg: '900px' }}
        maxW={{ base: '100vw', md: '100vw', lg: '1400px' }}
        width={{ base: '80vw', md: '85vw', lg: '88vw' }}
        direction="column"
        position="relative"
        p={0}
        bg={useColorModeValue('white', 'gray.800')}
        borderRadius="2xl"
        boxShadow={useColorModeValue('lg', 'dark-lg')}
        border="1px solid"
        borderColor={borderColor}
        mx="auto"
        height={{ base: '90vh', md: '92vh', lg: '96vh' }}
        maxHeight={{ base: '90vh', md: '92vh', lg: '96vh' }}
        transition="min-width 0.3s, max-width 0.3s, width 0.3s, height 0.3s"
      >
        <Box px={6} py={5} borderBottom="1px solid" borderColor={borderColor} bg={useColorModeValue('gray.50', 'gray.900')} borderTopRadius="2xl">
          <HStack justify="space-between">
            <Heading as="h3" size="md" color={textColor} fontWeight="700" letterSpacing="tight">
              🤖 AI Chat
            </Heading>
            <Button
              onClick={clearSession}
              leftIcon={<FaPlus />}
              size="sm"
              colorScheme="purple"
              borderRadius="md"
              fontWeight="600"
              variant="outline"
              _hover={{ bg: useColorModeValue('purple.50', 'purple.900') }}
            >
              New Chat
            </Button>
          </HStack>
        </Box>
        <Box
          ref={chatContainerRef}
          flex={1}
          overflowY="auto"
          px={6}
          py={4}
          bg={chatBg}
          borderBottom="1px solid"
          borderColor={borderColor}
          css={{
            scrollBehavior: 'smooth',
            '&::-webkit-scrollbar': { width: '8px' },
            '&::-webkit-scrollbar-thumb': { background: useColorModeValue('#c1c1c1', '#4a5568'), borderRadius: '4px' },
          }}
        >
          <VStack spacing={3} align="stretch">
            {history.map((entry, index) => (
              <VStack key={index} align={entry.user ? 'flex-end' : 'flex-start'} spacing={2} width="100%" maxWidth={entry.queryData ? '100%' : '80%'}>
                {entry.user && (
                  <Box alignSelf="flex-end" maxWidth="80%">
                    <HStack align="center" spacing={2} mb={1}>
                      <FaUser color={useColorModeValue('#3182ce', '#90cdf4')} />
                      <Text fontWeight="600" color={useColorModeValue('blue.800', 'blue.100')}>You</Text>
                    </HStack>
                    <Box
                      p={3}
                      bg={userMsgBg}
                      borderRadius="lg"
                      boxShadow={useColorModeValue('sm', 'dark-lg')}
                      border="1px solid"
                      borderColor={borderColor}
                      fontSize="md"
                      color={textColor}
                      whiteSpace="pre-wrap"
                      wordBreak="break-word"
                    >
                      {entry.user}
                    </Box>
                  </Box>
                )}
                {entry.bot && (
                  <VStack align="stretch" spacing={3} width="100%">
                    <HStack align="center" spacing={2} mb={1}>
                      <FaRobot color={useColorModeValue('#38a169', '#68d391')} />
                      <Text fontWeight="600" color={useColorModeValue('green.800', 'green.100')}>Bot</Text>
                    </HStack>

                    {/* Summary/Text Response */}
                    {entry.queryData ? (
                      <SummaryCard
                        summary={entry.bot}
                        warnings={entry.queryData.warnings}
                      />
                    ) : (
                      <Box
                        p={3}
                        bg={botMsgBg}
                        borderRadius="lg"
                        boxShadow={useColorModeValue('sm', 'dark-lg')}
                        border="1px solid"
                        borderColor={borderColor}
                        fontSize="md"
                        color={textColor}
                        whiteSpace="pre-wrap"
                        wordBreak="break-word"
                        maxWidth="80%"
                      >
                        {entry.bot}
                      </Box>
                    )}

                    {/* SQL Query Display */}
                    {entry.queryData && entry.queryData.sql_query && (
                      <SQLDisplay
                        sqlQuery={entry.queryData.sql_query}
                        status={entry.queryData.status}
                        matchedTemplate={entry.queryData.matched_template}
                      />
                    )}

                    {/* Data Table */}
                    {entry.queryData && entry.queryData.data_preview && entry.queryData.data_preview.length > 0 && (
                      <DataTable
                        data={entry.queryData.data_preview}
                        fullData={entry.queryData.full_data}
                        totalRows={entry.queryData.total_rows}
                        executionTime={entry.queryData.execution_time_seconds}
                        estimatedCost={entry.queryData.estimated_cost_usd}
                      />
                    )}
                  </VStack>
                )}
              </VStack>
            ))}

            {/* Live Transcript While Speaking */}
            {transcript && listening && (
              <Box
                alignSelf="flex-end"
                p={4}
                bg={userMsgBg}
                borderRadius="lg"
                boxShadow={useColorModeValue('sm', 'dark-lg')}
                maxWidth="70%"
                ml="auto"
                display="flex"
                alignItems="flex-start"
                transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                border="1px solid"
                borderColor={borderColor}
                opacity="0.8"
              >
                <FaUser style={{ marginRight: '8px', marginTop: '4px', flexShrink: 0 }} />
                <Text
                  color={useColorModeValue('blue.800', 'blue.100')}
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  whiteSpace="pre-wrap"
                  wordBreak="break-word"
                >
                  <strong>You:</strong> {transcript}
                  {/* Speaking indicator */}
                  <Box
                    as="span"
                    display="inline-block"
                    width="2px"
                    height="20px"
                    bg="currentColor"
                    ml="2px"
                    animation="blink 1s infinite"
                    verticalAlign="text-bottom"
                  />
                </Text>
              </Box>
            )}

            {/* Typing Indicator */}
            {isTyping && (
              <Box
                alignSelf="flex-start"
                p={4}
                bg={botMsgBg}
                borderRadius="lg"
                boxShadow={useColorModeValue('sm', 'dark-lg')}
                maxWidth="70%"
                mr="auto"
                position="relative"
                display="flex"
                alignItems="flex-start"
                transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                border="1px solid"
                borderColor={borderColor}
                minHeight="60px"
              >
                <FaRobot style={{ marginRight: '8px', marginTop: '4px', flexShrink: 0 }} />
                <Box flex="1">
                  <Text
                    color={useColorModeValue('green.800', 'green.100')}
                    transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                    whiteSpace="pre-wrap"
                    wordBreak="break-word"
                  >
                    <strong>Bot:</strong> {typingResponse}
                    {/* Typing cursor */}
                    <Box
                      as="span"
                      display="inline-block"
                      width="2px"
                      height="20px"
                      bg="currentColor"
                      ml="1px"
                      animation="blink 1s infinite"
                      verticalAlign="text-bottom"
                    />
                  </Text>
                </Box>
              </Box>
            )}

            {/* Thinking Indicator */}
            {thinking && !isTyping && (
              <Box
                alignSelf="flex-start"
                p={4}
                bg={botMsgBg}
                borderRadius="lg"
                boxShadow={useColorModeValue('sm', 'dark-lg')}
                maxWidth="70%"
                mr="auto"
                display="flex"
                alignItems="center"
                transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                border="1px solid"
                borderColor={borderColor}
              >
                <FaRobot style={{ marginRight: '8px' }} />
                <HStack>
                  <Spinner size="sm" color="green.500" />
                  <Text
                    color={useColorModeValue('green.800', 'green.100')}
                    transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  >
                    <strong>Bot:</strong> Thinking...
                  </Text>
                </HStack>
              </Box>
            )}
          </VStack>
        </Box>

        <Divider
          my={4}
          borderColor={borderColor}
          transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
        />

        <VStack spacing={4}>
          {/* Session Management - keep only the top new chat button */}
          <HStack spacing={4} width="100%" justify="flex-end" align="center">
{/*             <Button */}
{/*               onClick={clearSession} */}
{/*               leftIcon={<FaPlus />} */}
{/*               transition="all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)" */}
{/*               _hover={{ transform: 'scale(1.05)' }} */}
{/*               borderRadius="lg" */}
{/*               boxShadow={useColorModeValue('md', 'dark-lg')} */}
{/*               variant="outline" */}
{/*               colorScheme="purple" */}
{/*               size="sm" */}
{/*               fontWeight="600" */}
{/*             > */}
{/*               New Chat */}
{/*             </Button> */}
            {sessionId && (
              <Box
                px={3}
                py={1}
                bg={useColorModeValue('gray.100', 'gray.700')}
                borderRadius="full"
                border="1px solid"
                borderColor={borderColor}
              >
                <Text fontSize="xs" color={useColorModeValue('gray.600', 'gray.300')} fontWeight="500">
                  Session: {sessionId.slice(-8)}
                </Text>
              </Box>
            )}
          </HStack>

          {/* Input and Audio Controls - text field above, audio options centered below */}
          <VStack spacing={4} width={{ base: '98%', md: '85%', lg: '80%' }} mx="auto" minH={{ base: 'auto', md: 'auto', lg: 'auto' }} maxH={{ base: 'none', md: 'none', lg: 'none' }}>
            <Flex width="100%" direction="column" align="center" gap={4} wrap="wrap">
              <Box width={{ base: '100%', md: '60%', lg: '40%' }} maxW="320px" mx="auto">
                {/* Text Input (top, with border and shadow) */}
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    if (textInputValue && textInputValue.trim()) {
                      callCustomAPI(textInputValue);
                      setTextInputValue("");
                    }
                  }}
                  style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}
                >
                  <input
                    type="text"
                    value={textInputValue || ''}
                    onChange={e => setTextInputValue(e.target.value)}
                    placeholder="Type your message..."
                    style={{
                      flex: 1,
                      padding: '10px', // reduced from 14px
                      borderRadius: '10px',
                      border: `2px solid ${borderColor}`,
                      background: inputBg,
                      color: textColor,
                      fontSize: '1rem', // reduced from 1.08rem
                      outline: 'none',
                      boxShadow: useColorModeValue('0 2px 8px rgba(49,130,206,0.08)', '0 2px 8px rgba(49,130,206,0.18)'),
                      transition: 'all 0.3s',
                    }}
                    disabled={thinking || isTyping}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (textInputValue && textInputValue.trim()) {
                          callCustomAPI(textInputValue);
                          setTextInputValue("");
                        }
                      }
                    }}
                  />
                  <Button
                    type="submit"
                    colorScheme="blue"
                    borderRadius="md"
                    px={4} // reduced from 6
                    isDisabled={thinking || isTyping || !(textInputValue && textInputValue.trim())}
                  >
                    Send
                  </Button>
                </form>
                {/* Audio Controls (centered below input, improved alignment) */}
                <VStack align="center" spacing={2} width="100%" mt={2}>
                  <ContinuousRecordingToggle
                    isEnabled={continuousMode}
                    onToggle={handleContinuousModeToggle}
                  />
                  {continuousMode ? (
                    <Button
                      size="md" // reduced from lg
                      bg={listening ? 'red.500' : buttonBg}
                      color={listening ? 'white' : buttonColor}
                      borderRadius="full"
                      p={4} // reduced from 6
                      minW="60px" // reduced from 100px
                      boxShadow={listening
                        ? '0 0 30px rgba(239, 68, 68, 0.6)'
                        : useColorModeValue('0 8px 25px rgba(0,0,0,0.15)', '0 8px 25px rgba(0,0,0,0.4)')
                      }
                      transition="all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                      _hover={{
                        transform: 'scale(1.08)',
                        boxShadow: listening
                          ? '0 0 40px rgba(239, 68, 68, 0.8)'
                          : useColorModeValue('0 12px 35px rgba(0,0,0,0.2)', '0 12px 35px rgba(0,0,0,0.5)')
                      }}
                      onClick={toggleContinuousListening}
                      leftIcon={listening ? <FaStop /> : <FaPlay />}
                    >
                      {listening ? 'Stop Recording' : 'Start Recording'}
                    </Button>
                  ) : (
                    <Button
                      size="md" // reduced from lg
                      bgGradient="linear(to-r, blue.400, blue.600, purple.500)"
                      color="white"
                      borderRadius="full"
                      p={4} // reduced from 8
                      minW="60px" // reduced from 140px
                      minH="60px" // reduced from 140px
                      boxShadow="0 0 40px rgba(49,130,206,0.18), 0 8px 25px rgba(0,0,0,0.15)"
                      transition="all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                      transform={listening ? 'scale(1.12)' : 'scale(1)'}
                      _hover={{
                        transform: 'scale(1.18)',
                        bgGradient: 'linear(to-r, blue.500, purple.600, pink.400)',
                        boxShadow: '0 0 60px rgba(49,130,206,0.25), 0 12px 35px rgba(0,0,0,0.2)'
                      }}
                      _active={{
                        transform: 'scale(0.98)',
                        bgGradient: 'linear(to-r, blue.700, purple.700, pink.600)'
                      }}
                      onMouseDown={startPushToTalk}
                      onMouseUp={stopPushToTalk}
                      onMouseLeave={stopPushToTalk}
                      onTouchStart={startPushToTalk}
                      onTouchEnd={stopPushToTalk}
                      userSelect="none"
                    >
                      <VStack spacing={2} align="center">
                        <Box
                          animation={listening ? 'pulse 1.5s infinite' : undefined}
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                        >
                          <FaMicrophone size="20px" /> {/* reduced from 38px */}
                        </Box>
                        <Text fontSize="xs" fontWeight="bold" letterSpacing="tight">
                          {listening ? 'Recording...' : 'Hold to Talk'}
                        </Text>
                      </VStack>
                    </Button>
                  )}
                  <Button
                    onClick={handleMuteToggle}
                    leftIcon={isMuted ? <FaVolumeMute /> : <FaVolumeUp />}
                    transition="all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                    _hover={{ transform: 'scale(1.05)' }}
                    borderRadius="lg"
                    boxShadow={useColorModeValue('md', 'dark-lg')}
                    variant={isMuted ? 'solid' : 'outline'}
                    colorScheme={isMuted ? 'red' : 'blue'}
                    mt={2}
                    size="sm" // reduced from default
                  >
                    {isMuted ? 'Unmute' : 'Mute'}
                  </Button>
                </VStack>
              </Box>
            </Flex>
          </VStack>
          {/* Status Messages - only show once, not after audio controls */}
          <VStack spacing={2} width="100%" align="center" justify="center">
            {continuousMode ? (
              listening ? (
                <Text
                  textAlign="center"
                  color="green.500"
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  fontWeight="bold"
                  width="100%"
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                >
                  🎤 Recording... Click "Stop Recording" when done
                </Text>
              ) : (
                <Text
                  textAlign="center"
                  color="blue.500"
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  width="100%"
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                >
                  Click "Start Recording" to begin
                </Text>
              )
            ) : (
              listening ? (
                <Text
                  textAlign="center"
                  color="green.500"
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  fontWeight="bold"
                  animation="pulse 2s infinite"
                  width="100%"
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                >
                  🎤 Listening... Keep holding the button!
                </Text>
              ) : (
                <Text
                  textAlign="center"
                  color="blue.500"
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                  width="100%"
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                >
                  Hold the microphone button to speak
                </Text>
              )
            )}
            {thinking && (
              <HStack justify="center" width="100%">
                <Spinner size="md" color="blue.500" />
                <Text
                  fontSize="lg"
                  color={textColor}
                  transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                >
                  Connecting to AI...
                </Text>
              </HStack>
            )}
            {error && (
              <Text
                fontSize="lg"
                color="red.500"
                transition="all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
                width="100%"
                textAlign="center"
              >
                {error}
              </Text>
            )}
          </VStack>
        </VStack>
      </Flex>
    </Flex>
  );
};

const ChatBox = () => {
  // Add Google Fonts link
  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
    
    return () => {
      document.head.removeChild(link);
    };
  }, []);

  return (
    <>
      <style>{`
        @keyframes sunGlow {
          0%, 100% { opacity: 0.2; transform: translate(-50%, -50%) scale(1); }
          50% { opacity: 0.4; transform: translate(-50%, -50%) scale(1.1); }
        }
        @keyframes moonGlow {
          0% { opacity: 0.15; transform: translate(-50%, -50%) scale(1); }
          100% { opacity: 0.25; transform: translate(-50%, -50%) scale(1.05); }
        }
        @keyframes twinkle {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
      <ChatBoxContent />
    </>
  );
};

export default ChatBox;

