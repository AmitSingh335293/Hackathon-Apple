import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  VStack,
  HStack,
  Badge,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaTable, FaDownload } from 'react-icons/fa';

const DataTable = ({ data, totalRows, executionTime, estimatedCost }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headerBg = useColorModeValue('gray.50', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');

  if (!data || data.length === 0) {
    return (
      <Box
        p={4}
        bg={bgColor}
        borderRadius="lg"
        border="1px solid"
        borderColor={borderColor}
        textAlign="center"
      >
        <Text color="gray.500">No data to display</Text>
      </Box>
    );
  }

  const columns = Object.keys(data[0]);

  const formatValue = (value) => {
    if (value === null || value === undefined) {
      return 'NULL';
    }
    if (typeof value === 'number') {
      // Format large numbers with commas
      return value.toLocaleString('en-US', {
        maximumFractionDigits: 2,
      });
    }
    return String(value);
  };

  return (
    <VStack align="stretch" spacing={3} w="100%">
      {/* Header with metadata */}
      <HStack justify="space-between" align="center">
        <HStack>
          <FaTable color={useColorModeValue('#3182ce', '#90cdf4')} />
          <Text fontWeight="bold" fontSize="sm" color={textColor}>
            Query Results
          </Text>
        </HStack>
        <HStack spacing={2}>
          {totalRows !== undefined && (
            <Badge colorScheme="blue" fontSize="xs">
              {totalRows} rows
            </Badge>
          )}
          {executionTime !== undefined && (
            <Badge colorScheme="green" fontSize="xs">
              {executionTime.toFixed(3)}s
            </Badge>
          )}
          {estimatedCost !== undefined && (
            <Badge colorScheme="purple" fontSize="xs">
              ${estimatedCost.toFixed(4)}
            </Badge>
          )}
        </HStack>
      </HStack>

      {/* Data Table */}
      <Box
        overflowX="auto"
        bg={bgColor}
        borderRadius="lg"
        border="1px solid"
        borderColor={borderColor}
        boxShadow="sm"
      >
        <Table variant="simple" size="sm">
          <Thead bg={headerBg}>
            <Tr>
              {columns.map((column, idx) => (
                <Th
                  key={idx}
                  color={textColor}
                  fontWeight="bold"
                  textTransform="uppercase"
                  fontSize="xs"
                  letterSpacing="wide"
                  borderColor={borderColor}
                >
                  {column}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {data.map((row, rowIdx) => (
              <Tr
                key={rowIdx}
                _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                transition="background 0.2s"
              >
                {columns.map((column, colIdx) => (
                  <Td
                    key={colIdx}
                    color={textColor}
                    borderColor={borderColor}
                    fontFamily={typeof row[column] === 'number' ? 'monospace' : 'inherit'}
                  >
                    {formatValue(row[column])}
                  </Td>
                ))}
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {totalRows > data.length && (
        <Text fontSize="xs" color="gray.500" textAlign="center">
          Showing {data.length} of {totalRows} rows (preview)
        </Text>
      )}
    </VStack>
  );
};

export default DataTable;

