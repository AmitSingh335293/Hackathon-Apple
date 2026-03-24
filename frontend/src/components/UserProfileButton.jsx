import React, { useState } from 'react';
import {
  Popover, PopoverTrigger, PopoverContent, PopoverBody, PopoverArrow,
  Box, Button, VStack, HStack, Text, Badge, Avatar, Divider,
  useColorModeValue, IconButton,
} from '@chakra-ui/react';
import { FaSignOutAlt, FaUserShield, FaUser, FaTable } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const TABLE_SCHEME = {
  sales: 'green', products: 'blue', stores: 'orange',
  category: 'teal', warranty: 'red',
};

const UserProfileButton = () => {
  const { user, logout } = useAuth();
  const cardBg  = useColorModeValue('white',    'gray.800');
  const border  = useColorModeValue('gray.200', 'gray.600');
  const text    = useColorModeValue('gray.800', 'gray.100');
  const subtle  = useColorModeValue('gray.500', 'gray.400');
  const hoverBg = useColorModeValue('red.50',   'gray.700');

  if (!user) return null;

  const isAdmin = user.role === 'admin';
  const initials = (user.full_name || user.username)
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <Popover placement="bottom-end" closeOnBlur>
      <PopoverTrigger>
        <Button
          variant="ghost"
          borderRadius="full"
          p={1}
          _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
          title={user.full_name || user.username}
        >
          <Avatar
            size="sm"
            name={user.full_name || user.username}
            bg={isAdmin ? 'purple.500' : 'blue.500'}
            color="white"
            getInitials={() => initials}
          />
        </Button>
      </PopoverTrigger>

      <PopoverContent
        bg={cardBg} border="1px solid" borderColor={border}
        borderRadius="xl" boxShadow="xl" w="280px" zIndex={2000}
      >
        <PopoverArrow bg={cardBg} />
        <PopoverBody p={0}>
          {/* Profile header */}
          <Box
            bgGradient={isAdmin
              ? 'linear(to-r, purple.500, purple.700)'
              : 'linear(to-r, blue.400, blue.600)'}
            px={4} py={4} borderTopRadius="xl"
          >
            <HStack spacing={3}>
              <Avatar
                size="md"
                name={user.full_name || user.username}
                bg="whiteAlpha.300"
                color="white"
                getInitials={() => initials}
              />
              <VStack align="start" spacing={0}>
                <Text color="white" fontWeight="700" fontSize="sm">
                  {user.full_name || user.username}
                </Text>
                <Text color="whiteAlpha.800" fontSize="xs">
                  {user.email || '—'}
                </Text>
                <Badge
                  mt={1}
                  colorScheme={isAdmin ? 'purple' : 'blue'}
                  variant="solid"
                  fontSize="9px"
                  bg="whiteAlpha.300"
                  color="white"
                  borderRadius="full"
                  px={2}
                >
                  {isAdmin ? '👑 ADMIN' : '👤 USER'}
                </Badge>
              </VStack>
            </HStack>
          </Box>

          {/* Details */}
          <VStack spacing={0} align="stretch" px={4} py={3}>
            {/* Username row */}
            <HStack py={2} spacing={2}>
              <FaUser color="#718096" size="12px" />
              <Text fontSize="xs" color={subtle} fontWeight="600">Username</Text>
              <Text fontSize="xs" color={text} ml="auto">{user.username}</Text>
            </HStack>

            <Divider />

            {/* Permissions */}
            <Box py={2}>
              <HStack mb={2} spacing={2}>
                <FaTable color="#718096" size="12px" />
                <Text fontSize="xs" color={subtle} fontWeight="600">
                  Table Permissions ({user.permissions?.length || 0})
                </Text>
              </HStack>
              <HStack flexWrap="wrap" spacing={1}>
                {(user.permissions || []).map(p => (
                  <Badge
                    key={p}
                    colorScheme={TABLE_SCHEME[p] || 'gray'}
                    fontSize="10px"
                    borderRadius="full"
                    px={2}
                    py={0.5}
                    textTransform="capitalize"
                  >
                    {p}
                  </Badge>
                ))}
              </HStack>
            </Box>

            <Divider />

            {/* Logout */}
            <Button
              leftIcon={<FaSignOutAlt />}
              variant="ghost"
              colorScheme="red"
              size="sm"
              w="full"
              mt={2}
              borderRadius="lg"
              justifyContent="flex-start"
              _hover={{ bg: hoverBg }}
              onClick={logout}
            >
              Sign Out
            </Button>
          </VStack>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export default UserProfileButton;

