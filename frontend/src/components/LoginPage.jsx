import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  Button,
  Text,
  Heading,
  FormControl,
  FormLabel,
  Alert,
  AlertIcon,
  AlertDescription,
  IconButton,
  Divider,
  Badge,
  ChakraProvider,
} from '@chakra-ui/react';
import { FaUser, FaLock, FaEye, FaEyeSlash } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const DEMO_ACCOUNTS = [
  { u: 'admin',            pw: 'admin123',    tables: 'All tables',                  role: 'admin' },
  { u: 'sales_user',       pw: 'sales123',    tables: 'sales, products',             role: 'user'  },
  { u: 'store_manager',    pw: 'store123',    tables: 'stores, sales',               role: 'user'  },
  { u: 'category_analyst', pw: 'category123', tables: 'category, products, warranty', role: 'user'  },
];

const LoginPageInner = () => {
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPw,   setShowPw]   = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }
    setLoading(true);
    try {
      const backendUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : `http://${window.location.hostname}:8000`;
      const res = await fetch(`${backendUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Login failed. Check your credentials.');
      } else {
        login(data.access_token, {
          username:    data.username,
          email:       data.email,
          full_name:   data.full_name,
          role:        data.role,
          permissions: data.permissions,
        });
      }
    } catch (err) {
      setError(`Cannot connect to backend (http://localhost:8000). Is the server running? Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const autofill = (u, pw) => {
    setUsername(u);
    setPassword(pw);
    setError('');
  };

  return (
    <Box
      minH="100vh"
      w="100vw"
      bg="gray.50"
      display="flex"
      alignItems="center"
      justifyContent="center"
      px={4}
      py={8}
    >
      <Box
        w="full"
        maxW="440px"
        bg="white"
        borderRadius="2xl"
        boxShadow="0 20px 60px rgba(0,0,0,0.12)"
        border="1px solid"
        borderColor="gray.200"
        overflow="hidden"
      >
        {/* Header */}
        <Box
          bgGradient="linear(to-r, #4f8cff, #6a82fb, #a1c4fd)"
          py={8}
          px={6}
          textAlign="center"
        >
          <Heading color="white" fontSize="2xl" fontWeight="800" letterSpacing="tight">
            VoiceGenie AI
          </Heading>
          <Text color="whiteAlpha.900" fontSize="sm" mt={1}>
            Analytics Assistant — Sign In
          </Text>
        </Box>

        {/* Form */}
        <Box px={8} py={8}>
          {/* Error */}
          {error && (
            <Alert status="error" borderRadius="md" mb={5} variant="left-accent" fontSize="sm">
              <AlertIcon />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <VStack spacing={5}>
              {/* Username */}
              <FormControl isRequired>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.700">
                  Username
                </FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <FaUser color="#718096" size="14px" />
                  </InputLeftElement>
                  <Input
                    placeholder="e.g. sales_user"
                    value={username}
                    onChange={e => { setUsername(e.target.value); setError(''); }}
                    autoComplete="username"
                    borderRadius="lg"
                    focusBorderColor="blue.400"
                    bg="gray.50"
                  />
                </InputGroup>
              </FormControl>

              {/* Password */}
              <FormControl isRequired>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.700">
                  Password
                </FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <FaLock color="#718096" size="14px" />
                  </InputLeftElement>
                  <Input
                    type={showPw ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError(''); }}
                    autoComplete="current-password"
                    borderRadius="lg"
                    focusBorderColor="blue.400"
                    bg="gray.50"
                    pr="3rem"
                  />
                  <InputRightElement>
                    <IconButton
                      icon={showPw ? <FaEyeSlash /> : <FaEye />}
                      size="sm"
                      variant="ghost"
                      aria-label="Toggle password visibility"
                      onClick={() => setShowPw(p => !p)}
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              {/* Submit */}
              <Button
                type="submit"
                w="full"
                borderRadius="lg"
                fontWeight="700"
                size="lg"
                isLoading={loading}
                loadingText="Signing in..."
                bgGradient="linear(to-r, blue.400, blue.600)"
                color="white"
                _hover={{
                  bgGradient: 'linear(to-r, blue.500, blue.700)',
                  transform: 'translateY(-1px)',
                  boxShadow: 'lg',
                }}
                _active={{ transform: 'translateY(0)' }}
                transition="all 0.2s"
              >
                Sign In
              </Button>
            </VStack>
          </form>

          <Divider my={6} />

          {/* Demo accounts */}
          <Box bg="blue.50" borderRadius="lg" p={4} border="1px solid" borderColor="blue.100">
            <Text fontSize="xs" fontWeight="700" color="gray.500" mb={3} letterSpacing="wider">
              DEMO ACCOUNTS — click to autofill
            </Text>
            <VStack spacing={2} align="stretch">
              {DEMO_ACCOUNTS.map(d => (
                <Box
                  key={d.u}
                  cursor="pointer"
                  px={3}
                  py={2}
                  borderRadius="md"
                  bg={username === d.u ? 'blue.100' : 'white'}
                  border="1px solid"
                  borderColor={username === d.u ? 'blue.300' : 'gray.200'}
                  _hover={{ bg: 'blue.100', borderColor: 'blue.300' }}
                  onClick={() => autofill(d.u, d.pw)}
                  transition="all 0.15s"
                >
                  <HStack justify="space-between">
                    <HStack spacing={2}>
                      <Badge
                        colorScheme={d.role === 'admin' ? 'purple' : 'blue'}
                        fontSize="9px"
                        borderRadius="full"
                        px={2}
                      >
                        {d.role}
                      </Badge>
                      <Text fontSize="sm" fontWeight="600" color="gray.800">
                        {d.u}
                      </Text>
                    </HStack>
                    <Text fontSize="xs" color="gray.500">
                      {d.tables}
                    </Text>
                  </HStack>
                </Box>
              ))}
            </VStack>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

// Wrap with its own ChakraProvider so it works standalone
const LoginPage = () => (
  <ChakraProvider>
    <LoginPageInner />
  </ChakraProvider>
);

export default LoginPage;

