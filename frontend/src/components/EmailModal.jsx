import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  Input,
  VStack,
  Text,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  Textarea,
  Badge,
  Box,
  HStack,
  Tag,
  TagLabel,
  TagCloseButton,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import { FaEnvelope, FaCheckCircle, FaPlus } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const DEFAULT_FORM = {
  recipientInput: '',
  recipients: [],
  subject: 'Query Results — VoiceGenie AI',
  body: 'Please find the query results attached as a CSV file.',
};

const EmailModal = ({ isOpen, onClose, data, columns, buildCSV }) => {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState(null);
  const { token } = useAuth();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const labelColor = useColorModeValue('gray.700', 'gray.200');
  const tagBg = useColorModeValue('blue.50', 'blue.900');

  const rowCount = data ? data.length : 0;
  const colCount = columns ? columns.length : 0;

  // Add a recipient from the input field
  const addRecipient = () => {
    const email = form.recipientInput.trim().toLowerCase();
    if (!email) return;
    // Basic email format check
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setSendResult({ success: false, message: `"${email}" is not a valid email address.` });
      return;
    }
    if (form.recipients.includes(email)) {
      setForm((p) => ({ ...p, recipientInput: '' }));
      return;
    }
    setForm((p) => ({ ...p, recipients: [...p.recipients, email], recipientInput: '' }));
    setSendResult(null);
  };

  const removeRecipient = (email) => {
    setForm((p) => ({ ...p, recipients: p.recipients.filter((r) => r !== email) }));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',' || e.key === ' ') {
      e.preventDefault();
      addRecipient();
    }
  };

  const handleSend = async () => {
    setSendResult(null);

    // Allow comma-separated input that hasn't been confirmed yet
    const pendingEmails = form.recipientInput
      .split(/[,\s]+/)
      .map((e) => e.trim().toLowerCase())
      .filter(Boolean);

    const allRecipients = [...new Set([...form.recipients, ...pendingEmails])];

    if (allRecipients.length === 0) {
      setSendResult({ success: false, message: 'Please add at least one recipient email.' });
      return;
    }

    const csvContent = buildCSV();

    setIsSending(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          recipient_emails: allRecipients,
          subject: form.subject.trim() || 'Query Results — VoiceGenie AI',
          body: form.body.trim(),
          csv_content: csvContent,
          csv_filename: 'query_results.csv',
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setSendResult({
          success: true,
          message: result.message || 'Email sent successfully!',
        });
        // Update confirmed recipients list
        setForm((p) => ({ ...p, recipients: allRecipients, recipientInput: '' }));
      } else {
        setSendResult({
          success: false,
          message: result.detail || result.message || 'Failed to send email.',
        });
      }
    } catch (err) {
      setSendResult({ success: false, message: `Network error: ${err.message}` });
    } finally {
      setIsSending(false);
    }
  };

  const handleClose = () => {
    setForm(DEFAULT_FORM);
    setSendResult(null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="lg" scrollBehavior="inside">
      <ModalOverlay backdropFilter="blur(4px)" />
      <ModalContent bg={bgColor} borderRadius="xl" mx={4}>
        <ModalHeader borderBottom="1px solid" borderColor={borderColor}>
          <HStack spacing={2}>
            <FaEnvelope color="#3182ce" />
            <Text>Send Data via Email</Text>
            <Badge colorScheme="blue" fontSize="xs" ml={1}>
              {rowCount} rows · {colCount} cols
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />

        <ModalBody py={5}>
          <VStack spacing={5} align="stretch">
            {/* Result Alert */}
            {sendResult && (
              <Alert
                status={sendResult.success ? 'success' : 'error'}
                borderRadius="md"
                variant="left-accent"
              >
                <AlertIcon />
                <Box>
                  <AlertTitle>{sendResult.success ? 'Email Sent!' : 'Send Failed'}</AlertTitle>
                  <AlertDescription fontSize="sm">{sendResult.message}</AlertDescription>
                </Box>
              </Alert>
            )}

            {/* Recipients */}
            <FormControl isRequired>
              <FormLabel fontSize="sm" fontWeight="700" color={labelColor}>
                Recipient Email(s)
              </FormLabel>

              {/* Recipient tags */}
              {form.recipients.length > 0 && (
                <Wrap mb={2} spacing={2}>
                  {form.recipients.map((email) => (
                    <WrapItem key={email}>
                      <Tag
                        size="sm"
                        borderRadius="full"
                        variant="subtle"
                        colorScheme="blue"
                        bg={tagBg}
                      >
                        <TagLabel>{email}</TagLabel>
                        <TagCloseButton onClick={() => removeRecipient(email)} />
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              )}

              <HStack>
                <Input
                  placeholder="colleague@example.com"
                  size="sm"
                  value={form.recipientInput}
                  onChange={(e) => {
                    setForm((p) => ({ ...p, recipientInput: e.target.value }));
                    setSendResult(null);
                  }}
                  onKeyDown={handleKeyDown}
                  borderRadius="md"
                />
                <Button
                  size="sm"
                  leftIcon={<FaPlus />}
                  colorScheme="blue"
                  variant="outline"
                  onClick={addRecipient}
                  borderRadius="md"
                  flexShrink={0}
                >
                  Add
                </Button>
              </HStack>
              <FormHelperText fontSize="xs">
                Press <kbd>Enter</kbd> or <kbd>,</kbd> to add each address, or paste multiple comma-separated addresses and click Send.
              </FormHelperText>
            </FormControl>

            {/* Subject */}
            <FormControl>
              <FormLabel fontSize="sm" fontWeight="700" color={labelColor}>
                Subject
              </FormLabel>
              <Input
                size="sm"
                value={form.subject}
                onChange={(e) => setForm((p) => ({ ...p, subject: e.target.value }))}
                borderRadius="md"
              />
            </FormControl>

            {/* Body */}
            <FormControl>
              <FormLabel fontSize="sm" fontWeight="700" color={labelColor}>
                Message
              </FormLabel>
              <Textarea
                size="sm"
                value={form.body}
                onChange={(e) => setForm((p) => ({ ...p, body: e.target.value }))}
                borderRadius="md"
                rows={3}
                resize="vertical"
              />
            </FormControl>

            {/* Attachment info */}
            <Box
              p={3}
              bg={useColorModeValue('gray.50', 'gray.700')}
              borderRadius="md"
              border="1px solid"
              borderColor={borderColor}
            >
              <HStack spacing={2}>
                <FaCheckCircle color="#38a169" size="12px" />
                <Text fontSize="xs" color="gray.600">
                  <strong>Attachment:</strong> query_results.csv — {rowCount} rows, {colCount} columns
                </Text>
              </HStack>
              <Text fontSize="xs" color="gray.400" mt={1}>
                📌 SMTP credentials are configured on the server — no need to enter them here.
              </Text>
            </Box>
          </VStack>
        </ModalBody>

        <ModalFooter borderTop="1px solid" borderColor={borderColor} gap={3}>
          <Button variant="ghost" onClick={handleClose} size="sm">
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            leftIcon={<FaEnvelope />}
            onClick={handleSend}
            isLoading={isSending}
            loadingText="Sending..."
            size="sm"
            borderRadius="md"
            isDisabled={sendResult?.success}
          >
            Send Email
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default EmailModal;

