import React, { useEffect } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Link, Tabs, usePathname, useRouter } from 'expo-router';
import { Image, Platform, Pressable, Text, View } from 'react-native';

import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import { useClientOnlyValue } from '@/components/useClientOnlyValue';
import GradientTabBar from '@/components/GradientTabBar';

// You can explore the built-in icon families and icons on the web at https://icons.expo.fyi/
function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>['name'];
  color: string;
}) {
  return <FontAwesome size={28} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const logoSource = require('../../assets/images/logo.png');
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    if (!pathname) return;
    try {
      localStorage.setItem('lazyedit:lastTab', pathname);
    } catch (_err) {
      // ignore storage errors
    }
  }, [pathname]);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    try {
      if (pathname !== '/' && pathname !== '') return;
      const saved = localStorage.getItem('lazyedit:lastTab');
      if (saved && saved !== pathname) {
        router.replace(saved);
      }
    } catch (_err) {
      // ignore storage errors
    }
  }, [pathname, router]);

  return (
    <Tabs
      initialRouteName="home"
      screenOptions={{
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#64748b',
        tabBarStyle: {
          position: 'absolute',
          backgroundColor: 'transparent',
          borderTopWidth: 0,
          elevation: 0,
        },
        headerTitleAlign: 'left',
        headerTitle: () => (
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Image
              source={logoSource}
              style={{ height: 42, width: 54, resizeMode: 'contain', marginRight: 8 }}
              accessibilityLabel="LazyEdit logo"
            />
            <Text style={{ fontSize: 16, fontWeight: '700', color: '#0f172a' }}>
              LazyEdit - Powered by LazyingArt
            </Text>
          </View>
        ),
        // Disable the static render of the header on web
        // to prevent a hydration error in React Navigation v6.
        headerShown: useClientOnlyValue(false, true),
      }}
      tabBar={(props) => <GradientTabBar {...props} />}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => <TabBarIcon name="code" color={color} />,
          headerRight: () => (
            <Link href="/modal" asChild>
              <Pressable>
                {({ pressed }) => (
                  <FontAwesome
                    name="info-circle"
                    size={25}
                    color={Colors[colorScheme ?? 'light'].text}
                    style={{ marginRight: 15, opacity: pressed ? 0.5 : 1 }}
                  />
                )}
              </Pressable>
            </Link>
          ),
        }}
      />
      <Tabs.Screen
        name="library"
        options={{
          title: 'Studio',
          tabBarIcon: ({ color }) => <TabBarIcon name="folder" color={color} />,
        }}
      />
      <Tabs.Screen
        name="editor"
        options={{
          title: 'Publish',
          tabBarIcon: ({ color }) => <TabBarIcon name="edit" color={color} />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Settings',
          tabBarIcon: ({ color }) => <TabBarIcon name="cog" color={color} />,
        }}
      />
    </Tabs>
  );
}
