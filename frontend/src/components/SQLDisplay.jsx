import React, { useState } from 'react';
import {
  Box, Text, Code, VStack, HStack, Badge,
  useColorModeValue, Collapse, IconButton
} from '@chakra-ui/react';
import { FaDatabase, FaChevronDown, FaChevronUp, FaCopy, FaCheck } from 'react-icons/fa';

const SQLDisplay = ({ sqlQuery, status, matchedTemplate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBg = useColorModeValue('gray.800', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const headerHoverBg = useColorModeValue('gray.100', 'gray.750');
  const iconColor = useColorModeValue('#3182ce', '#90cdf4');

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'pending_approval': return 'yellow';
      case 'executing': return 'blue';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(sqlQuery).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <VStack
      align="stretch"
      spacing={0}
      bg={bgColor}
      borderRadius="lg"
      border="1px solid"
      borderColor={borderColor}
      boxShadow="sm"
      overflow="hidden"
    >
      {/* Clickable Header / Dropdown Toggle */}
      <HStack
        justify="space-between"
        align="center"
        px={4}
        py={3}
        cursor="pointer"
        onClick={() => setIsOpen((prev) => !prev)}
        _hover={{ bg: headerHoverBg }}
        transition="background 0.2s"
      >
        <HStack spacing={2}>
          <FaDatabase color={iconColor} />
          <Text fontWeight="bold" fontSize="sm" color={textColor}>
            Generated SQL Query
          </Text>
          <Badge colorScheme={isOpen ? 'blue' : 'gray'} fontSize="xs" variant="subtle">
            {isOpen ? 'Hide' : 'Show'}
          </Badge>
        </HStack>

        <HStack spacing={2}>
          {matchedTemplate && (
            <Badge colorScheme="purple" fontSize="xs">
              Template: {matchedTemplate}
            </Badge>
          )}
          <Badge colorScheme={getStatusColor(status)} fontSize="xs">
            {status.replace('_', ' ').toUpperCase()}
          </Badge>

          {/* Copy button — only visible when expanded */}
          {isOpen && (
            <IconButton
              icon={copied ? <FaCheck /> : <FaCopy />}
              size="xs"
              variant="ghost"
              colorScheme={copied ? 'green' : 'gray'}
              aria-label={copied ? 'Copied!' : 'Copy SQL'}
              title={copied ? 'Copied!' : 'Copy SQL'}
              onClick={handleCopy}
              _hover={{ bg: useColorModeValue('gray.200', 'gray.600') }}
            />
          )}

          {/* Chevron icon */}
          <Box color={iconColor}>
            {isOpen ? <FaChevronUp size="12px" /> : <FaChevronDown size="12px" />}
          </Box>
        </HStack>
      </HStack>

      {/* Collapsible SQL Code Block */}
      <Collapse in={isOpen} animateOpacity>
        <Box
          as="pre"
          mx={4}
          mb={4}
          p={3}
          bg={codeBg}
          borderRadius="md"
          overflowX="auto"
          fontSize="sm"
          fontFamily="monospace"
          color="green.300"
          border="1px solid"
          borderColor={useColorModeValue('gray.300', 'gray.600')}
        >
          <Code colorScheme="green" bg="transparent" whiteSpace="pre-wrap" wordBreak="break-word">
            {sqlQuery}
          </Code>
        </Box>
      </Collapse>
    </VStack>
  );
};

export default SQLDisplay;
