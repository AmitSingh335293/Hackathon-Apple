import React from 'react';
import { Box, HStack, useColorMode } from '@chakra-ui/react';
import { FaSun, FaMoon } from 'react-icons/fa';

const DarkModeToggle = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const isDark = colorMode === 'dark';

  return (
    <Box
      as="button"
      onClick={toggleColorMode}
      display="flex"
      alignItems="center"
      bg="whiteAlpha.200"
      borderRadius="full"
      px={2}
      py={1}
      border="1px solid"
      borderColor="whiteAlpha.400"
      _hover={{ bg: 'whiteAlpha.300' }}
      transition="all 0.3s"
      cursor="pointer"
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <HStack spacing={1}>
        {/* Sun */}
        <Box
          transition="all 0.4s"
          opacity={isDark ? 0.4 : 1}
          transform={isDark ? 'scale(0.8)' : 'scale(1)'}
        >
          <FaSun color={isDark ? '#9CA3AF' : '#FDE68A'} size="15px" />
        </Box>

        {/* Track */}
        <Box
          position="relative"
          w="32px"
          h="16px"
          bg={isDark ? 'blue.400' : 'whiteAlpha.500'}
          borderRadius="full"
          transition="all 0.4s"
        >
          {/* Thumb */}
          <Box
            position="absolute"
            top="2px"
            left={isDark ? '16px' : '2px'}
            w="12px"
            h="12px"
            bg="white"
            borderRadius="full"
            transition="all 0.4s"
            boxShadow="sm"
          />
        </Box>

        {/* Moon */}
        <Box
          transition="all 0.4s"
          opacity={isDark ? 1 : 0.4}
          transform={isDark ? 'scale(1)' : 'scale(0.8)'}
        >
          <FaMoon color={isDark ? '#93C5FD' : '#9CA3AF'} size="13px" />
        </Box>
      </HStack>
    </Box>
  );
};

export default DarkModeToggle;

