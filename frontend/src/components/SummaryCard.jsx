import React from 'react';
import { Box, Text, VStack, HStack, Icon, useColorModeValue } from '@chakra-ui/react';
import { FaLightbulb, FaExclamationTriangle } from 'react-icons/fa';

const SummaryCard = ({ summary, warnings }) => {
  const bgColor = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('blue.200', 'blue.600');
  const textColor = useColorModeValue('blue.900', 'blue.100');
  const warningBg = useColorModeValue('yellow.50', 'yellow.900');
  const warningBorder = useColorModeValue('yellow.200', 'yellow.600');
  const warningText = useColorModeValue('yellow.900', 'yellow.100');

  return (
    <VStack align="stretch" spacing={3} w="100%">
      {/* Summary */}
      {summary && (
        <Box
          p={4}
          bg={bgColor}
          borderRadius="lg"
          border="2px solid"
          borderColor={borderColor}
          boxShadow="md"
        >
          <HStack align="start" spacing={3}>
            <Icon
              as={FaLightbulb}
              color={useColorModeValue('blue.500', 'blue.300')}
              boxSize={5}
              mt={1}
            />
            <VStack align="start" spacing={2} flex={1}>
              <Text fontWeight="bold" fontSize="sm" color={textColor}>
                AI-Generated Insights
              </Text>
              <Text fontSize="sm" color={textColor} lineHeight="1.6">
                {summary}
              </Text>
            </VStack>
          </HStack>
        </Box>
      )}

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <Box
          p={4}
          bg={warningBg}
          borderRadius="lg"
          border="1px solid"
          borderColor={warningBorder}
          boxShadow="sm"
        >
          <HStack align="start" spacing={3}>
            <Icon
              as={FaExclamationTriangle}
              color={useColorModeValue('yellow.600', 'yellow.300')}
              boxSize={5}
              mt={1}
            />
            <VStack align="start" spacing={2} flex={1}>
              <Text fontWeight="bold" fontSize="sm" color={warningText}>
                Warnings
              </Text>
              <VStack align="start" spacing={1}>
                {warnings.map((warning, idx) => (
                  <Text key={idx} fontSize="xs" color={warningText}>
                    • {warning}
                  </Text>
                ))}
              </VStack>
            </VStack>
          </HStack>
        </Box>
      )}
    </VStack>
  );
};

export default SummaryCard;

