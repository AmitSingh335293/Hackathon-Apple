import React, { useState } from 'react';
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
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaTable, FaDownload, FaEnvelope } from 'react-icons/fa';
import EmailModal from './EmailModal';

const DataTable = ({ data, fullData, totalRows, executionTime, estimatedCost }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headerBg = useColorModeValue('gray.50', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

  // Use fullData for exports; fall back to data (preview) if fullData not provided
  const exportData = (fullData && fullData.length > 0) ? fullData : data;

  if (!data || data.length === 0) {
    return (
      <Box p={4} bg={bgColor} borderRadius="lg" border="1px solid" borderColor={borderColor} textAlign="center">
        <Text color="gray.500">No data to display</Text>
      </Box>
    );
  }

  // columns for table display (preview rows)
  const columns = Object.keys(data[0]);
  // columns for CSV (full data)
  const exportColumns = exportData.length > 0 ? Object.keys(exportData[0]) : columns;

  // Display count: prefer totalRows from backend (authoritative), fallback to exportData length
  const exportCount = totalRows !== undefined && totalRows !== null ? totalRows : exportData.length;

  const formatValue = (value) => {
    if (value === null || value === undefined) return 'NULL';
    if (typeof value === 'number') return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
    return String(value);
  };

  // Build CSV from ALL rows (exportData)
  const buildCSV = () => {
    const header = exportColumns.map((c) => `"${c}"`).join(',');
    const rows = exportData.map((row) =>
      exportColumns.map((col) => {
        const val = row[col];
        if (val === null || val === undefined) return '""';
        return `"${String(val).replace(/"/g, '""')}"`;
      }).join(',')
    );
    return [header, ...rows].join('\n');
  };

  const handleDownloadCSV = () => {
    const csvContent = buildCSV();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    // Use a hidden <a> that is never appended to DOM — avoids browser URL flash at bottom
    const link = document.createElement('a');
    link.style.display = 'none';
    link.href = url;
    link.download = 'query_results.csv';
    document.body.appendChild(link);
    link.click();
    // Small delay before cleanup so browser has time to start download
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 150);
  };

  return (
    <VStack align="stretch" spacing={3} w="100%">
      {/* Header with metadata */}
      <HStack justify="space-between" align="center" flexWrap="wrap" gap={2}>
        <HStack>
          <FaTable color={useColorModeValue('#3182ce', '#90cdf4')} />
          <Text fontWeight="bold" fontSize="sm" color={textColor}>
            Query Results
          </Text>
        </HStack>
        <HStack spacing={2} flexWrap="wrap">
          {totalRows !== undefined && (
            <Badge colorScheme="blue" fontSize="xs">{totalRows} rows</Badge>
          )}
          {executionTime !== undefined && (
            <Badge colorScheme="green" fontSize="xs">{executionTime.toFixed(3)}s</Badge>
          )}
          {estimatedCost !== undefined && (
            <Badge colorScheme="purple" fontSize="xs">${estimatedCost.toFixed(4)}</Badge>
          )}

          {/* CSV Download — no Tooltip to avoid browser URL preview at bottom-left */}
          <Button
            size="xs"
            leftIcon={<FaDownload />}
            colorScheme="teal"
            variant="outline"
            onClick={handleDownloadCSV}
            borderRadius="md"
            fontWeight="600"
            title=""
          >
            Download CSV ({exportCount})
          </Button>

          {/* Email Button */}
          <Button
            size="xs"
            leftIcon={<FaEnvelope />}
            colorScheme="blue"
            variant="outline"
            onClick={() => setIsEmailModalOpen(true)}
            borderRadius="md"
            fontWeight="600"
            title=""
          >
            Email ({exportCount})
          </Button>
        </HStack>
      </HStack>

      {/* Data Table — shows preview rows only */}
      <Box overflowX="auto" bg={bgColor} borderRadius="lg" border="1px solid" borderColor={borderColor} boxShadow="sm">
        <Table variant="simple" size="sm">
          <Thead bg={headerBg}>
            <Tr>
              {columns.map((column, idx) => (
                <Th key={idx} color={textColor} fontWeight="bold" textTransform="uppercase" fontSize="xs" letterSpacing="wide" borderColor={borderColor}>
                  {column}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {data.map((row, rowIdx) => (
              <Tr key={rowIdx} _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }} transition="background 0.2s">
                {columns.map((column, colIdx) => (
                  <Td key={colIdx} color={textColor} borderColor={borderColor} fontFamily={typeof row[column] === 'number' ? 'monospace' : 'inherit'}>
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
          Showing {data.length} of {totalRows} rows — CSV &amp; Email contain all {totalRows} rows
        </Text>
      )}

      {/* Email Modal — receives full export data */}
      <EmailModal
        isOpen={isEmailModalOpen}
        onClose={() => setIsEmailModalOpen(false)}
        data={exportData}
        columns={exportColumns}
        buildCSV={buildCSV}
      />
    </VStack>
  );
};

export default DataTable;

