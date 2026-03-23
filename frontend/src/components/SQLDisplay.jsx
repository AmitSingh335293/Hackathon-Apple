import React from 'react';
import { Box, Text, Code, VStack, HStack, Badge, useColorModeValue } from '@chakra-ui/react';
import { FaDatabase } from 'react-icons/fa';

const SQLDisplay = ({ sqlQuery, status, matchedTemplate }) => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBg = useColorModeValue('gray.800', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'pending_approval':
        return 'yellow';
      case 'executing':
        return 'blue';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <VStack
      align="stretch"
      spacing={2}
      p={4}
      bg={bgColor}
      borderRadius="lg"
      border="1px solid"
      borderColor={borderColor}
      boxShadow="sm"
    >
      <HStack justify="space-between" align="center">
        <HStack>
          <FaDatabase color={useColorModeValue('#3182ce', '#90cdf4')} />
          <Text fontWeight="bold" fontSize="sm" color={textColor}>
            Generated SQL Query
          </Text>
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
        </HStack>
      </HStack>

      <Box
        as="pre"
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
    </VStack>
  );
};

export default SQLDisplay;
