import React from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { BottomTabBar, BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { LinearGradient } from 'expo-linear-gradient';

export default function GradientTabBar(props: BottomTabBarProps) {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={["#ffffff", "#eef7ff", "#fcf1f5"]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={styles.gradient}
      />
      <BottomTabBar {...props} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  gradient: {
    ...StyleSheet.absoluteFillObject,
    height: Platform.select({ ios: 90, android: 70, default: 60 }),
    opacity: 0.96,
  },
});
