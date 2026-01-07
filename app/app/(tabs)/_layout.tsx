import React, { useEffect } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Link, Tabs, usePathname, useRouter } from 'expo-router';
import { Image, Platform, Pressable, Text, View } from 'react-native';

import Colors from '@/constants/Colors';
import { useI18n } from '@/components/I18nProvider';
import { useColorScheme } from '@/components/useColorScheme';
import { useClientOnlyValue } from '@/components/useClientOnlyValue';
import GradientTabBar from '@/components/GradientTabBar';
import LanguagePicker from '@/components/LanguagePicker';

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
  const { t } = useI18n();

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
              {t('header_title')}
            </Text>
          </View>
        ),
        headerRight: () => (
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginRight: 12 }}>
            <LanguagePicker />
            <Link href="/modal" asChild>
              <Pressable>
                {({ pressed }) => (
                  <FontAwesome
                    name="info-circle"
                    size={22}
                    color={Colors[colorScheme ?? 'light'].text}
                    style={{ opacity: pressed ? 0.5 : 1 }}
                  />
                )}
              </Pressable>
            </Link>
          </View>
        ),
        // Disable the static render of the header on web
        // to prevent a hydration error in React Navigation v6.
        headerShown: useClientOnlyValue(false, true),
      }}
      tabBar={(props) => <GradientTabBar {...props} />}
    >
      <Tabs.Screen
        name="index"
        options={{
          href: null,
        }}
      />
      <Tabs.Screen
        name="home"
        options={{
          title: t('tab_home'),
          tabBarIcon: ({ color }) => <TabBarIcon name="home" color={color} />,
        }}
      />
      <Tabs.Screen
        name="library"
        options={{
          title: t('tab_studio'),
          tabBarIcon: ({ color }) => <TabBarIcon name="film" color={color} />,
        }}
      />
      <Tabs.Screen
        name="editor"
        options={{
          title: t('tab_publish'),
          tabBarIcon: ({ color }) => <TabBarIcon name="upload" color={color} />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: t('tab_settings'),
          tabBarIcon: ({ color }) => <TabBarIcon name="cog" color={color} />,
        }}
      />
    </Tabs>
  );
}
